from django.contrib import admin
from .models import Article, Topic, Page


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin configuration for topics"""
    list_display = ('name', 'slug', 'article_count', 'color', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('created_at',)

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for articles"""
    list_display = (
        'title', 'author', 'topic', 'status', 'published_at',
        'word_count', 'reading_time', 'view_count', 'created_at'
    )
    list_filter = ('status', 'topic', 'published_at', 'created_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at', '-created_at')
    readonly_fields = ('word_count', 'reading_time', 'view_count')
    raw_id_fields = ('author', 'topic', 'hero_image')

    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'excerpt')
        }),
        ('Metadata', {
            'fields': ('author', 'topic', 'hero_image', 'status'),
            'classes': ('collapse',)
        }),
        ('Auto-calculated', {
            'fields': ('slug', 'word_count', 'reading_time', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Admin configuration for pages"""
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
