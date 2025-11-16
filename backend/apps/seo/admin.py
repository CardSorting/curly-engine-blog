from django.contrib import admin
from .models import SEOSettings, SitemapEntry, Redirect, MetaTag


@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ['site', 'meta_title', 'organization_name', 'google_analytics_id', 'updated_at']
    search_fields = ['site__domain', 'meta_title', 'organization_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image')
        }),
        ('Twitter Cards', {
            'fields': ('twitter_card', 'twitter_site', 'twitter_creator')
        }),
        ('Structured Data', {
            'fields': ('organization_name', 'organization_url', 'organization_logo')
        }),
        ('Technical SEO', {
            'fields': ('google_analytics_id', 'google_search_console', 'bing_webmaster_tools')
        }),
        ('Sitemap Settings', {
            'fields': ('sitemap_priority', 'sitemap_changefreq')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SitemapEntry)
class SitemapEntryAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'url', 'priority', 'changefreq', 'last_modified']
    list_filter = ['content_type', 'changefreq']
    search_fields = ['url', 'object_id']
    readonly_fields = ['last_modified']
    list_editable = ['priority', 'changefreq']
    
    def has_add_permission(self, request):
        return False  # Sitemap entries should be managed programmatically


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ['old_path', 'new_path', 'status_code', 'is_active', 'updated_at']
    list_filter = ['status_code', 'is_active']
    search_fields = ['old_path', 'new_path']
    list_editable = ['status_code', 'is_active']
    ordering = ['old_path']


@admin.register(MetaTag)
class MetaTagAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'url_pattern', 'meta_title', 'is_active', 'updated_at']
    list_filter = ['content_type', 'is_active', 'robots_index', 'robots_follow']
    search_fields = ['meta_title', 'meta_description', 'url_pattern', 'object_id']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('content_type', 'object_id', 'url_pattern')
        }),
        ('Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url')
        }),
        ('Robots', {
            'fields': ('robots_index', 'robots_follow')
        }),
        ('Custom Meta', {
            'fields': ('custom_meta',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
