"""Celery tasks for newsletter functionality"""

import logging
from typing import List, Dict, Any
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from django.core.mail import send_mail

from config.celery import app
from .models import Newsletter, Subscriber, NewsletterSend
from .email_service import EmailService

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3)
def process_pending_newsletters(self):
    """
    Process pending newsletters and queue them for sending
    Runs every 30 minutes via Celery Beat
    """
    try:
        # Find newsletters that should be sent now
        pending_newsletters = Newsletter.objects.filter(
            status='scheduled',
            scheduled_at__lte=timezone.now()
        )

        processed_count = 0
        for newsletter in pending_newsletters:
            try:
                # Mark as sending
                newsletter.status = 'sending'
                newsletter.save()

                # Queue individual sends
                active_subscribers = Subscriber.objects.filter(
                    is_active=True,
                    is_confirmed=True
                )

                # Batch subscribers for efficiency
                batch_size = 100
                subscriber_batches = [
                    active_subscribers[i:i + batch_size]
                    for i in range(0, active_subscribers.count(), batch_size)
                ]

                for batch in subscriber_batches:
                    send_newsletter_to_batch.delay(
                        newsletter.id,
                        [sub.id for sub in batch]
                    )

                processed_count += 1
                logger.info(f"Queued newsletter '{newsletter.subject}' for {active_subscribers.count()} subscribers")

            except Exception as e:
                logger.error(f"Failed to process newsletter {newsletter.id}: {str(e)}")
                newsletter.status = 'failed'
                newsletter.save()

        return f"Processed {processed_count} newsletters"

    except Exception as e:
        logger.error(f"Error in process_pending_newsletters: {str(e)}")
        raise self.retry(countdown=60, exc=e)


@app.task(bind=True, max_retries=3)
def send_newsletter_to_batch(self, newsletter_id: int, subscriber_ids: List[int]):
    """
    Send newsletter to a batch of subscribers
    """
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)
        subscribers = Subscriber.objects.filter(id__in=subscriber_ids, is_active=True, is_confirmed=True)

        sent_count = 0
        for subscriber in subscribers:
            try:
                # Create or update send record
                send_record, created = NewsletterSend.objects.get_or_create(
                    newsletter=newsletter,
                    subscriber=subscriber,
                    defaults={'status': 'pending'}
                )

                if send_record.status != 'sent':
                    # Send the email
                    success = EmailService.send_newsletter_email(
                        newsletter=newsletter,
                        subscriber=subscriber
                    )

                    if success:
                        send_record.status = 'sent'
                        send_record.sent_at = timezone.now()
                        sent_count += 1
                    else:
                        send_record.status = 'failed'
                        send_record.error_message = 'Email service failed'

                    send_record.save()

            except Exception as e:
                logger.error(f"Failed to send newsletter {newsletter_id} to subscriber {subscriber.id}: {str(e)}")

        # Update newsletter status if all subscribers processed
        if sent_count > 0:
            total_sends = NewsletterSend.objects.filter(newsletter=newsletter, status='sent').count()
            if total_sends >= subscribers.count():
                newsletter.status = 'sent'
                newsletter.sent_at = timezone.now()
                newsletter.save()

        return f"Sent to {sent_count} subscribers"

    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter {newsletter_id} not found")
        return "Newsletter not found"
    except Exception as e:
        logger.error(f"Error sending newsletter batch: {str(e)}")
        raise self.retry(countdown=60, max_retries=3, exc=e)


@app.task(bind=True, max_retries=3)
def update_email_analytics(self):
    """
    Update email analytics for sent newsletters
    Runs every 2 hours via Celery Beat
    """
    try:
        # Get newsletters sent in the last 48 hours
        recent_newsletters = Newsletter.objects.filter(
            sent_at__gte=timezone.now() - timezone.timedelta(days=2),
            status='sent'
        )

        analytics_updated = 0
        for newsletter in recent_newsletters:
            try:
                # Calculate open rates, click rates, etc.
                total_sends = NewsletterSend.objects.filter(
                    newsletter=newsletter,
                    status='sent'
                ).count()

                if total_sends > 0:
                    opened = NewsletterSend.objects.filter(
                        newsletter=newsletter,
                        status='sent',
                        opened_at__isnull=False
                    ).count()

                    clicked = NewsletterSend.objects.filter(
                        newsletter=newsletter,
                        status='sent',
                        clicked_at__isnull=False
                    ).count()

                    # Update newsletter with analytics
                    newsletter.open_rate = (opened / total_sends) * 100
                    newsletter.click_rate = (clicked / total_sends) * 100
                    newsletter.save()

                    analytics_updated += 1

            except Exception as e:
                logger.error(f"Failed to update analytics for newsletter {newsletter.id}: {str(e)}")

        return f"Updated analytics for {analytics_updated} newsletters"

    except Exception as e:
        logger.error(f"Error in update_email_analytics: {str(e)}")
        raise self.retry(countdown=300, exc=e)


@app.task(bind=True)
def resend_failed_emails(self, newsletter_id: int = None, days_back: int = 7):
    """
    Retry sending failed emails from recent newsletters
    """
    try:
        # Find failed sends from recent newsletters
        cutoff_date = timezone.now() - timezone.timedelta(days=days_back)

        failed_sends = NewsletterSend.objects.filter(
            status='failed',
            newsletter__sent_at__gte=cutoff_date
        )

        if newsletter_id:
            failed_sends = failed_sends.filter(newsletter_id=newsletter_id)

        resent_count = 0
        for send_record in failed_sends:
            try:
                success = EmailService.send_newsletter_email(
                    newsletter=send_record.newsletter,
                    subscriber=send_record.subscriber
                )

                if success:
                    send_record.status = 'sent'
                    send_record.sent_at = timezone.now()
                    send_record.error_message = None
                    send_record.save()
                    resent_count += 1
                else:
                    send_record.error_message = 'Retry failed'
                    send_record.save()

            except Exception as e:
                logger.error(f"Failed to resend to subscriber {send_record.subscriber.id}: {str(e)}")

        return f"Resent {resent_count} failed emails"

    except Exception as e:
        logger.error(f"Error in resend_failed_emails: {str(e)}")
        raise


@app.task(bind=True)
def clean_old_newsletter_data(self, days_to_keep: int = 90):
    """
    Clean up old newsletter send data and analytics
    """
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)

        # Delete old send records
        old_sends = NewsletterSend.objects.filter(
            created_at__lt=cutoff_date
        )

        deleted_count = old_sends.delete()[0]
        logger.info(f"Cleaned up {deleted_count} old newsletter send records")

        return f"Cleaned up {deleted_count} records"

    except Exception as e:
        logger.error(f"Error in clean_old_newsletter_data: {str(e)}")
        raise


@app.task(bind=True)
def generate_newsletter_performance_report(self, days: int = 30):
    """
    Generate comprehensive newsletter performance report
    """
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        newsletters = Newsletter.objects.filter(sent_at__gte=cutoff_date)

        report = {
            'period_days': days,
            'total_newsletters': newsletters.count(),
            'total_sends': 0,
            'total_opens': 0,
            'total_clicks': 0,
            'average_open_rate': 0,
            'average_click_rate': 0,
            'top_performing_subject': None,
            'best_open_rate': 0,
        }

        if newsletters.exists():
            for newsletter in newsletters:
                sends = NewsletterSend.objects.filter(newsletter=newsletter, status='sent')
                opens = sends.filter(opened_at__isnull=False).count()
                clicks = sends.filter(clicked_at__isnull=False).count()

                report['total_sends'] += sends.count()
                report['total_opens'] += opens
                report['total_clicks'] += clicks

                open_rate = (opens / sends.count()) * 100 if sends.count() > 0 else 0
                if open_rate > report['best_open_rate']:
                    report['best_open_rate'] = open_rate
                    report['top_performing_subject'] = newsletter.subject

            if report['total_sends'] > 0:
                report['average_open_rate'] = (report['total_opens'] / report['total_sends']) * 100
                report['average_click_rate'] = (report['total_clicks'] / report['total_sends']) * 100

        # Log the report
        logger.info(f"Newsletter Performance Report: {report}")

        return report

    except Exception as e:
        logger.error(f"Error generating newsletter performance report: {str(e)}")
        raise
