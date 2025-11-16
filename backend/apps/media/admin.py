from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Admin configuration for media files"""
    list_display = ('filename', 'uploaded_by', 'mime_type', 'width', 'height', 'file_size', 'created_at')
    list_filter = ('mime_type', 'created_at', 'uploaded_by')
    search_fields = ('filename', 'alt_text')
    readonly_fields = ('width', 'height', 'file_size', 'mime_type')
    ordering = ('-created_at',)

    fieldsets = (
        ('File Info', {
            'fields': ('file', 'filename', 'alt_text')
        }),
        ('Metadata', {
            'fields': ('width', 'height', 'file_size', 'mime_type'),
            'classes': ('collapse',)
        }),
        ('Ownership', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
    )
