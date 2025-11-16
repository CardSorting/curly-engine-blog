import uuid
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Subscriber, Newsletter, SubscriberGroup, NewsletterSend, NewsletterTemplate


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_confirmed', 'created_at', 'user_link']
    list_filter = ['is_active', 'is_confirmed', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['id', 'confirmation_token', 'unsubscribe_token', 'created_at', 'confirmed_at', 'unsubscribed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('email', 'first_name', 'last_name', 'user')
        }),
        ('Subscription Status', {
            'fields': ('is_active', 'is_confirmed')
        }),
        ('Tokens', {
            'fields': ('confirmation_token', 'unsubscribe_token'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'confirmed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_confirmation_emails', 'activate_subscribers', 'deactivate_subscribers']
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = 'User'
    
    def send_confirmation_emails(self, request, queryset):
        count = 0
        for subscriber in queryset.filter(is_confirmed=False):
            try:
                subscriber.send_confirmation_email()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error sending to {subscriber.email}: {e}', level='error')
        self.message_user(request, f'Confirmation emails sent to {count} subscribers.')
    send_confirmation_emails.short_description = 'Send confirmation emails'
    
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'Activated {queryset.count()} subscribers.')
    activate_subscribers.short_description = 'Activate selected subscribers'
    
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {queryset.count()} subscribers.')
    deactivate_subscribers.short_description = 'Deactivate selected subscribers'


@admin.register(SubscriberGroup)
class SubscriberGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'subscriber_count']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'subscriber_count']
    
    def subscriber_count(self, obj):
        return obj.subscribers.count()
    subscriber_count.short_description = 'Subscribers'


class NewsletterSendInline(admin.TabularInline):
    model = NewsletterSend
    extra = 0
    readonly_fields = ['subscriber', 'status', 'sent_at', 'opened_at', 'clicked_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at', 'scheduled_at', 'sent_at', 'total_sent', 'total_opened', 'total_clicked']
    list_filter = ['status', 'created_at', 'scheduled_at', 'sent_at']
    search_fields = ['title', 'subject']
    readonly_fields = ['id', 'total_sent', 'total_opened', 'total_clicked', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subject', 'preview_text', 'created_by')
        }),
        ('Content', {
            'fields': ('content_html', 'content_text')
        }),
        ('Status & Scheduling', {
            'fields': ('status', 'scheduled_at', 'sent_at')
        }),
        ('Targeting', {
            'fields': ('target_all_subscribers', 'target_groups')
        }),
        ('Metrics', {
            'fields': ('total_sent', 'total_opened', 'total_clicked'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['target_groups']
    inlines = [NewsletterSendInline]
    actions = ['send_newsletter', 'duplicate_newsletter']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by').prefetch_related('target_groups')
    
    def send_newsletter(self, request, queryset):
        for newsletter in queryset.filter(status='draft'):
            try:
                newsletter.send_newsletter()
                self.message_user(request, f'Newsletter "{newsletter.title}" sent successfully.')
            except Exception as e:
                self.message_user(request, f'Error sending "{newsletter.title}": {e}', level='error')
    send_newsletter.short_description = 'Send selected newsletters'
    
    def duplicate_newsletter(self, request, queryset):
        for newsletter in queryset:
            new_newsletter = Newsletter.objects.create(
                title=f'{newsletter.title} (Copy)',
                subject=newsletter.subject,
                preview_text=newsletter.preview_text,
                content_html=newsletter.content_html,
                content_text=newsletter.content_text,
                created_by=request.user,
                target_all_subscribers=newsletter.target_all_subscribers,
            )
            new_newsletter.target_groups.set(newsletter.target_groups.all())
        self.message_user(request, f'Duplicated {queryset.count()} newsletters.')
    duplicate_newsletter.short_description = 'Duplicate selected newsletters'


@admin.register(NewsletterSend)
class NewsletterSendAdmin(admin.ModelAdmin):
    list_display = ['newsletter', 'subscriber', 'status', 'sent_at', 'opened_at', 'clicked_at']
    list_filter = ['status', 'sent_at', 'opened_at', 'clicked_at']
    search_fields = ['newsletter__title', 'subscriber__email']
    readonly_fields = ['id', 'open_token', 'click_token', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('newsletter', 'subscriber')


@admin.register(NewsletterTemplate)
class NewsletterTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'created_at', 'updated_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_default')
        }),
        ('Template Content', {
            'fields': ('subject_template', 'html_template', 'text_template')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['set_as_default', 'unset_as_default']
    
    def set_as_default(self, request, queryset):
        NewsletterTemplate.objects.update(is_default=False)
        queryset.update(is_default=True)
        self.message_user(request, f'Set {queryset.count()} templates as default.')
    set_as_default.short_description = 'Set as default template'
    
    def unset_as_default(self, request, queryset):
        queryset.update(is_default=False)
        self.message_user(request, f'Unset {queryset.count()} templates from default.')
    unset_as_default.short_description = 'Unset from default'
