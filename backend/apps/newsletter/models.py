import uuid
import logging
from django.db import models
from django.utils import timezone
from django.conf import settings
from .email_service import email_service

logger = logging.getLogger(__name__)


class Subscriber(models.Model):
    """Newsletter subscriber with double opt-in"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    
    # Tokens for opt-in and unsubscribe
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # User association (optional)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='newsletter_subscription'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['confirmation_token']),
            models.Index(fields=['unsubscribe_token']),
            models.Index(fields=['is_active', 'is_confirmed']),
        ]
    
    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    def send_confirmation_email(self):
        """Send double opt-in confirmation email"""
        return email_service.send_confirmation_email(self)
    
    def confirm_subscription(self):
        """Confirm the subscription after double opt-in"""
        self.is_confirmed = True
        self.is_active = True
        self.confirmed_at = timezone.now()
        self.save()
    
    def unsubscribe(self):
        """Unsubscribe from newsletter"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()


class Newsletter(models.Model):
    """Newsletter campaign/email"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    preview_text = models.CharField(max_length=150, help_text="Text shown in email clients")
    
    # Content
    content_html = models.TextField()
    content_text = models.TextField()
    
    # Status and scheduling
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    SENT = 'sent'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SCHEDULED, 'Scheduled'),
        (SENT, 'Sent'),
        (CANCELLED, 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Targeting
    target_all_subscribers = models.BooleanField(default=True)
    target_groups = models.ManyToManyField(
        'SubscriberGroup', 
        blank=True, 
        related_name='newsletters'
    )
    
    # Metrics
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_newsletters'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def get_recipients(self):
        """Get list of recipient email addresses"""
        if self.target_all_subscribers:
            return Subscriber.objects.filter(is_active=True, is_confirmed=True)
        else:
            return Subscriber.objects.filter(
                is_active=True, 
                is_confirmed=True,
                groups__in=self.target_groups.all()
            ).distinct()
    
    def send_newsletter(self):
        """Send newsletter to all recipients"""
        recipients = self.get_recipients()
        
        for subscriber in recipients:
            try:
                newsletter_send = NewsletterSend.objects.create(
                    newsletter=self,
                    subscriber=subscriber,
                    status=NewsletterSend.PENDING
                )
                # Send email using email service
                email_service.send_newsletter(newsletter_send)
            except Exception as e:
                logger.error(f"Error creating newsletter send for {subscriber.email}: {e}")
                continue
        
        self.total_sent = recipients.count()
        self.status = self.SENT
        self.sent_at = timezone.now()
        self.save()


class SubscriberGroup(models.Model):
    """Groups for segmenting subscribers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NewsletterSend(models.Model):
    """Track individual newsletter sends"""
    PENDING = 'pending'
    SENT = 'sent'
    DELIVERED = 'delivered'
    OPENED = 'opened'
    CLICKED = 'clicked'
    BOUNCED = 'bounced'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SENT, 'Sent'),
        (DELIVERED, 'Delivered'),
        (OPENED, 'Opened'),
        (CLICKED, 'Clicked'),
        (BOUNCED, 'Bounced'),
        (FAILED, 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='sends')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='newsletter_sends')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Tokens for tracking
    open_token = models.UUIDField(default=uuid.uuid4, editable=False)
    click_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['newsletter', 'subscriber']
        indexes = [
            models.Index(fields=['newsletter', 'status']),
            models.Index(fields=['subscriber', 'status']),
            models.Index(fields=['open_token']),
            models.Index(fields=['click_token']),
        ]
    
    def __str__(self):
        return f"{self.newsletter.title} -> {self.subscriber.email} ({self.status})"


class NewsletterTemplate(models.Model):
    """Reusable email templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Template content
    subject_template = models.CharField(max_length=200)
    html_template = models.TextField()
    text_template = models.TextField()
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
