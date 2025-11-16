from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    Extended user model for authors.
    Uses email as username.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # SAAS related fields
    default_account = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_users')
    is_trialing = models.BooleanField(default=False)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # For createsuperuser
    
    def __str__(self):
        return self.email
    
    @property
    def current_account(self):
        """Get the current account based on request context or default"""
        # This would typically be set by middleware
        if hasattr(self, '_current_account') and self._current_account:
            return self._current_account
        return self.default_account
    
    @property
    def account_role(self):
        """Get user's role in current account"""
        if self.current_account:
            from apps.accounts.models import AccountUser
            try:
                membership = AccountUser.objects.get(
                    account=self.current_account,
                    user=self
                )
                return membership.role
            except AccountUser.DoesNotExist:
                return None
        return None
    
    @property
    def can_create_account(self):
        """Check if user can create a new account"""
        # For now, allow all users to create accounts
        # You could add logic here based on subscription limits
        return True
