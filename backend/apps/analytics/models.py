from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class PageView(models.Model):
    """
    Track individual page views for analytics
    """
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('page', 'Page'),
        ('topic', 'Topic'),
        ('home', 'Home'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What was viewed
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.UUIDField(null=True, blank=True)  # For article/page/topic IDs
    url = models.CharField(max_length=500)  # Full URL path
    
    # Who viewed (optional - can be anonymous)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # When and how long
    timestamp = models.DateTimeField(default=timezone.now)
    session_id = models.CharField(max_length=100, blank=True)  # For tracking unique sessions
    referrer = models.URLField(blank=True)
    
    # Additional tracking
    time_on_page = models.IntegerField(null=True, blank=True)  # Seconds
    is_bounce = models.BooleanField(default=False)  # Left without interaction
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.content_type} view at {self.timestamp}"


class DailyAnalytics(models.Model):
    """
    Aggregated daily analytics for performance
    """
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('page', 'Page'),
        ('topic', 'Topic'),
        ('home', 'Home'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What and when
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.UUIDField(null=True, blank=True)
    date = models.DateField()
    
    # Metrics
    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)  # Based on session_id
    avg_time_on_page = models.FloatField(default=0.0)  # Seconds
    bounce_rate = models.FloatField(default=0.0)  # Percentage
    
    class Meta:
        unique_together = ['content_type', 'object_id', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['content_type', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.content_type} analytics for {self.date}"


class ArticleAnalytics(models.Model):
    """
    Extended analytics specifically for articles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.OneToOneField('articles.Article', on_delete=models.CASCADE, related_name='analytics')
    
    # Engagement metrics
    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    avg_reading_time = models.FloatField(default=0.0)  # Actual time vs estimated
    completion_rate = models.FloatField(default=0.0)  # Percentage who read to end
    
    # Social metrics
    shares_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    # SEO metrics
    search_views = models.IntegerField(default=0)  # From search engines
    direct_views = models.IntegerField(default=0)  # Direct traffic
    referral_views = models.IntegerField(default=0)  # From other sites
    
    # Performance over time
    views_last_7_days = models.IntegerField(default=0)
    views_last_30_days = models.IntegerField(default=0)
    views_last_90_days = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-views_last_30_days']
    
    def __str__(self):
        return f"Analytics for {self.article.title}"
