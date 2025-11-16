from django.db import models
from django.utils import timezone
import uuid


class SubscriptionPlan(models.Model):
    """
    SAAS subscription plans (Free, Pro, Enterprise)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    
    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Limits
    max_users = models.IntegerField(default=1)  # Number of users allowed
    max_articles = models.IntegerField(default=10)  # Number of articles allowed
    max_storage_mb = models.IntegerField(default=100)  # Storage in MB
    
    # Features
    features = models.JSONField(default=dict, blank=True)  # Store features as JSON
    
    # Stripe integration
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['monthly_price']
    
    def __str__(self):
        return self.name


class Account(models.Model):
    """
    Tenant account for SAAS model - represents a blog/site
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)  # Blog/Site name
    slug = models.SlugField(unique=True, max_length=200)  # Subdomain or custom domain
    description = models.TextField(blank=True)
    
    # Owner
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='owned_accounts')
    
    # Subscription
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trialing', 'Trialing'),
            ('active', 'Active'),
            ('past_due', 'Past Due'),
            ('canceled', 'Canceled'),
            ('unpaid', 'Unpaid'),
        ],
        default='trialing'
    )
    
    # Billing
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    current_article_count = models.IntegerField(default=0)
    current_storage_mb = models.IntegerField(default=0)
    current_user_count = models.IntegerField(default=1)
    
    # Custom domain (for paid plans)
    custom_domain = models.CharField(max_length=255, blank=True)
    domain_verified = models.BooleanField(default=False)
    
    # Stripe integration
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
            models.Index(fields=['subscription_status']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_trial_active(self):
        if self.trial_ends_at:
            return timezone.now() < self.trial_ends_at
        return False
    
    @property
    def is_subscription_active(self):
        if self.subscription_status == 'active':
            if self.subscription_ends_at:
                return timezone.now() < self.subscription_ends_at
            return True
        return False
    
    @property
    def can_create_article(self):
        if not self.subscription_plan:
            return self.current_article_count < 10  # Default trial limit
        return self.current_article_count < self.subscription_plan.max_articles
    
    @property
    def can_add_user(self):
        if not self.subscription_plan:
            return self.current_user_count < 1  # Default trial limit
        return self.current_user_count < self.subscription_plan.max_users
    
    def check_storage_limit(self, additional_mb):
        if not self.subscription_plan:
            return (self.current_storage_mb + additional_mb) <= 100  # Default trial limit
        return (self.current_storage_mb + additional_mb) <= self.subscription_plan.max_storage_mb


class AccountUser(models.Model):
    """
    Many-to-many relationship between Account and User with roles
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_users')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='account_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='author')
    
    # Invitation tracking
    invited_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations')
    invited_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['account', 'user']
        indexes = [
            models.Index(fields=['account', 'role']),
            models.Index(fields=['user', 'role']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.account.name} ({self.role})"
    
    @property
    def can_manage_users(self):
        return self.role in ['admin']
    
    @property
    def can_manage_billing(self):
        return self.role in ['admin']
    
    @property
    def can_publish_articles(self):
        return self.role in ['admin', 'editor', 'author']
    
    @property
    def can_edit_all_articles(self):
        return self.role in ['admin', 'editor']
    
    @property
    def can_view_analytics(self):
        return self.role in ['admin', 'editor']
