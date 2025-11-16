from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404


class IsAccountMember(BasePermission):
    """
    Permission to check if user is a member of the current account
    """
    def has_permission(self, request, view):
        return hasattr(request, 'account_user') and request.account_user is not None


class IsAccountAdmin(BasePermission):
    """
    Permission to check if user has admin role in the current account
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.role == 'admin'
        )


class IsAccountEditorOrAdmin(BasePermission):
    """
    Permission to check if user has editor or admin role
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.role in ['admin', 'editor']
        )


class CanManageUsers(BasePermission):
    """
    Permission to check if user can manage other users
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.can_manage_users
        )


class CanManageBilling(BasePermission):
    """
    Permission to check if user can manage billing
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.can_manage_billing
        )


class CanPublishArticles(BasePermission):
    """
    Permission to check if user can publish articles
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.can_publish_articles
        )


class CanEditAllArticles(BasePermission):
    """
    Permission to check if user can edit all articles in the account
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.can_edit_all_articles
        )


class CanViewAnalytics(BasePermission):
    """
    Permission to check if user can view analytics
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.can_view_analytics
        )


class IsArticleAuthorOrEditor(BasePermission):
    """
    Permission to check if user is the article author or can edit all articles
    """
    def has_object_permission(self, request, view, obj):
        # Check if user can edit all articles
        if (
            hasattr(request, 'account_user') and 
            request.account_user and 
            request.account_user.can_edit_all_articles
        ):
            return True
        
        # Check if user is the article author
        return obj.author == request.user


class IsAccountOwner(BasePermission):
    """
    Permission to check if user is the account owner
    """
    def has_permission(self, request, view):
        return (
            hasattr(request, 'tenant') and 
            request.tenant and 
            request.user.is_authenticated and 
            request.tenant.owner == request.user
        )


class HasSubscriptionAccess(BasePermission):
    """
    Permission to check if account has active subscription or trial
    """
    def has_permission(self, request, view):
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
        
        return request.tenant.is_trial_active or request.tenant.is_subscription_active


class WithinSubscriptionLimits(BasePermission):
    """
    Permission to check if account is within subscription limits
    """
    def __init__(self, limit_type='articles'):
        self.limit_type = limit_type
    
    def has_permission(self, request, view):
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
        
        tenant = request.tenant
        
        if self.limit_type == 'articles':
            return tenant.can_create_article
        elif self.limit_type == 'users':
            return tenant.can_add_user
        elif self.limit_type == 'storage':
            # For storage, we'd need to check the actual file size
            # This is a basic check
            return True
        
        return False
