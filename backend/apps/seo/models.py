from django.db import models
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils import timezone
import uuid


class SEOSettings(models.Model):
    """
    Global SEO settings for the blog
    """
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='seo_settings')
    
    # Basic SEO
    meta_title = models.CharField(max_length=60, help_text="Default meta title for homepage")
    meta_description = models.CharField(max_length=160, help_text="Default meta description for homepage")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    
    # Open Graph
    og_title = models.CharField(max_length=100, blank=True)
    og_description = models.CharField(max_length=200, blank=True)
    og_image = models.ForeignKey('media.Media', on_delete=models.SET_NULL, null=True, blank=True, related_name='og_images')
    
    # Twitter Cards
    twitter_card = models.CharField(max_length=50, default='summary_large_image')
    twitter_site = models.CharField(max_length=50, blank=True)  # @username
    twitter_creator = models.CharField(max_length=50, blank=True)  # @username
    
    # Structured Data
    organization_name = models.CharField(max_length=100)
    organization_url = models.URLField()
    organization_logo = models.ForeignKey('media.Media', on_delete=models.SET_NULL, null=True, blank=True, related_name='org_logos')
    
    # Technical SEO
    google_analytics_id = models.CharField(max_length=50, blank=True)  # GA-XXXXXXXXX
    google_search_console = models.URLField(blank=True)
    bing_webmaster_tools = models.CharField(max_length=100, blank=True)
    
    # Sitemap settings
    sitemap_priority = models.FloatField(default=0.8)
    sitemap_changefreq = models.CharField(max_length=20, default='weekly')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SEO Settings for {self.site.domain}"


class SitemapEntry(models.Model):
    """
    Individual sitemap entries for dynamic content
    """
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('page', 'Page'),
        ('topic', 'Topic'),
        ('home', 'Homepage'),
        ('custom', 'Custom URL'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Content identification
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.UUIDField(null=True, blank=True)  # For article/page/topic IDs
    url = models.CharField(max_length=500)
    
    # Sitemap attributes
    priority = models.FloatField(default=0.5)
    changefreq = models.CharField(
        max_length=20,
        choices=[
            ('always', 'Always'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('never', 'Never'),
        ],
        default='weekly'
    )
    
    # Timestamps
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['content_type', 'object_id', 'url']
        ordering = ['-last_modified']
        indexes = [
            models.Index(fields=['content_type', 'last_modified']),
            models.Index(fields=['last_modified']),
        ]
    
    def __str__(self):
        return f"{self.content_type}: {self.url}"


class Redirect(models.Model):
    """
    URL redirects for SEO and maintenance
    """
    STATUS_CHOICES = [
        ('301', 'Permanent (301)'),
        ('302', 'Temporary (302)'),
        ('410', 'Gone (410)'),
    ]
    
    old_path = models.CharField(max_length=500, unique=True, help_text="The old URL path (without domain)")
    new_path = models.CharField(max_length=500, blank=True, help_text="The new URL path (leave empty for 410)")
    status_code = models.CharField(max_length=3, choices=STATUS_CHOICES, default='301')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['old_path']
    
    def __str__(self):
        return f"{self.old_path} → {self.new_path or 'GONE'} ({self.status_code})"


class MetaTag(models.Model):
    """
    Custom meta tags for specific pages
    """
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('page', 'Page'),
        ('topic', 'Topic'),
        ('custom', 'Custom URL'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.UUIDField(null=True, blank=True)
    url_pattern = models.CharField(max_length=500, blank=True, help_text="URL pattern for custom matching")
    
    # Meta tags
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    canonical_url = models.URLField(blank=True)
    robots_index = models.BooleanField(default=True)
    robots_follow = models.BooleanField(default=True)
    
    # Custom meta tags (JSON format)
    custom_meta = models.JSONField(default=dict, blank=True, help_text="Additional meta tags as JSON")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['content_type', 'object_id', 'url_pattern']
        ordering = ['content_type', 'url_pattern']
    
    def __str__(self):
        return f"Meta tags for {self.content_type}: {self.object_id or self.url_pattern}"
