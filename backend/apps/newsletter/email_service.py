import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import resend

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling email operations with Resend integration"""
    
    def __init__(self):
        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY
        else:
            logger.warning("RESEND_API_KEY not configured")
    
    def send_confirmation_email(self, subscriber):
        """Send double opt-in confirmation email"""
        try:
            subject = 'Confirm your newsletter subscription'
            context = {
                'subscriber': subscriber,
                'confirmation_url': f"{settings.FRONTEND_URL}/newsletter/confirm/{subscriber.confirmation_token}/"
            }
            
            html_message = render_to_string('newsletter/confirmation_email.html', context)
            text_message = render_to_string('newsletter/confirmation_email.txt', context)
            
            # Try Resend first, fallback to Django email
            if settings.RESEND_API_KEY:
                return self._send_with_resend(
                    to_email=subscriber.email,
                    subject=subject,
                    html_content=html_message,
                    text_content=text_message
                )
            else:
                return self._send_with_django(
                    to_email=subscriber.email,
                    subject=subject,
                    html_message=html_message,
                    text_message=text_message
                )
                
        except Exception as e:
            logger.error(f"Error sending confirmation email to {subscriber.email}: {str(e)}")
            raise
    
    def send_newsletter(self, newsletter_send):
        """Send newsletter to a specific subscriber"""
        try:
            newsletter = newsletter_send.newsletter
            subscriber = newsletter_send.subscriber
            
            # Add tracking pixels and links
            context = {
                'newsletter': newsletter,
                'subscriber': subscriber,
                'newsletter_send': newsletter_send,
                'tracking_pixel_url': f"{settings.BACKEND_URL}/api/newsletter/tracking/open/{newsletter_send.open_token}/",
                'unsubscribe_url': f"{settings.FRONTEND_URL}/newsletter/unsubscribe/{subscriber.unsubscribe_token}/"
            }
            
            # Personalize content
            subject = newsletter.subject
            html_content = self._add_tracking_to_html(newsletter.content_html, newsletter_send)
            text_content = self._add_tracking_to_text(newsletter.content_text, newsletter_send)
            
            # Try Resend first, fallback to Django email
            if settings.RESEND_API_KEY:
                result = self._send_with_resend(
                    to_email=subscriber.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL
                )
            else:
                result = self._send_with_django(
                    to_email=subscriber.email,
                    subject=subject,
                    html_message=html_content,
                    text_message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL
                )
            
            # Update send record
            if result:
                newsletter_send.status = 'sent'
                newsletter_send.sent_at = timezone.now()
                newsletter_send.save()
                return True
            else:
                newsletter_send.status = 'failed'
                newsletter_send.save()
                return False
                
        except Exception as e:
            logger.error(f"Error sending newsletter to {subscriber.email}: {str(e)}")
            newsletter_send.status = 'failed'
            newsletter_send.save()
            raise
    
    def _send_with_resend(self, to_email, subject, html_content, text_content=None, from_email=None):
        """Send email using Resend API"""
        try:
            params = {
                "from": from_email or settings.DEFAULT_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            
            if text_content:
                params["text"] = text_content
            
            result = resend.Emails.send(params)
            
            if result.get("id"):
                logger.info(f"Email sent successfully via Resend to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email via Resend: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Resend API error: {str(e)}")
            return False
    
    def _send_with_django(self, to_email, subject, html_message=None, text_message=None, from_email=None):
        """Send email using Django's default email backend"""
        try:
            send_mail(
                subject=subject,
                message=text_message or '',
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent successfully via Django to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Django email error: {str(e)}")
            return False
    
    def _add_tracking_to_html(self, html_content, newsletter_send):
        """Add tracking pixel and convert links to tracked links"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Add tracking pixel at the end
        tracking_pixel = soup.new_tag('img')
        tracking_pixel.attrs = {
            'src': f"{settings.BACKEND_URL}/api/newsletter/tracking/open/{newsletter_send.open_token}/",
            'width': '1',
            'height': '1',
            'style': 'display:none;',
            'alt': ''
        }
        soup.body.append(tracking_pixel)
        
        # Convert links to tracked links
        for link in soup.find_all('a', href=True):
            original_url = link['href']
            tracked_url = f"{settings.BACKEND_URL}/api/newsletter/tracking/click/{newsletter_send.click_token}/?url={original_url}"
            link['href'] = tracked_url
        
        return str(soup)
    
    def _add_tracking_to_text(self, text_content, newsletter_send):
        """Add tracking info to text content"""
        # For text emails, we can't add a tracking pixel, but we can modify links
        lines = text_content.split('\n')
        modified_lines = []
        
        for line in lines:
            # Simple URL detection and replacement
            if 'http' in line:
                words = line.split()
                modified_words = []
                for word in words:
                    if word.startswith(('http://', 'https://')):
                        tracked_url = f"{settings.BACKEND_URL}/api/newsletter/tracking/click/{newsletter_send.click_token}/?url={word}"
                        modified_words.append(tracked_url)
                    else:
                        modified_words.append(word)
                modified_lines.append(' '.join(modified_words))
            else:
                modified_lines.append(line)
        
        return '\n'.join(modified_lines)


# Global email service instance
email_service = EmailService()
