from django.contrib import admin
from .models import Account, SubscriptionPlan, AccountUser


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'monthly_price', 'yearly_price', 'max_users', 'max_articles', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class AccountUserInline(admin.TabularInline):
    model = AccountUser
    extra = 0
    readonly_fields = ['joined_at']
    fields = ['user', 'role', 'is_active', 'joined_at']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'subscription_status', 'subscription_plan', 'created_at']
    list_filter = ['subscription_status', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__email']
    readonly_fields = ['id', 'stripe_customer_id', 'stripe_subscription_id', 'created_at', 'updated_at']
    inlines = [AccountUserInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'description', 'owner', 'is_active')
        }),
        ('Subscription', {
            'fields': ('subscription_plan', 'subscription_status', 'trial_ends_at', 'subscription_ends_at')
        }),
        ('Usage', {
            'fields': ('current_article_count', 'current_user_count', 'current_storage_mb'),
            'classes': ('collapse',)
        }),
        ('Domain', {
            'fields': ('custom_domain', 'domain_verified'),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AccountUser)
class AccountUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'account', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__email', 'account__name']
    readonly_fields = ['id', 'joined_at']
