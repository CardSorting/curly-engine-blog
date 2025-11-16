from django.contrib import admin
from .models import PageView, DailyAnalytics, ArticleAnalytics


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'url', 'timestamp', 'user', 'ip_address', 'time_on_page']
    list_filter = ['content_type', 'timestamp', 'is_bounce']
    search_fields = ['url', 'user_agent', 'referrer']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # PageViews should only be created programmatically


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'date', 'total_views', 'unique_views', 'avg_time_on_page', 'bounce_rate']
    list_filter = ['content_type', 'date']
    readonly_fields = ['date']
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False  # DailyAnalytics should only be created programmatically


@admin.register(ArticleAnalytics)
class ArticleAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['article', 'total_views', 'unique_views', 'avg_reading_time', 'completion_rate', 'views_last_30_days']
    list_filter = ['last_updated']
    search_fields = ['article__title']
    readonly_fields = ['last_updated']
    
    def has_add_permission(self, request):
        return False  # ArticleAnalytics should only be created programmatically
