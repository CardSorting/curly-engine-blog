from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Account, AccountUser


class TenantMiddleware:
    """
    Middleware to identify and set the current tenant (account)
    based on subdomain or custom domain
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract tenant from subdomain or custom domain
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Skip tenant resolution for admin and API docs
        if host.startswith('admin.') or host.startswith('api.') or host == 'localhost':
            request.tenant = None
            request.account_user = None
            return self.get_response(request)
        
        # Try to find account by custom domain first
        account = None
        try:
            account = Account.objects.filter(custom_domain=host, domain_verified=True).first()
        except:
            pass
        
        # If not found, try by slug (subdomain)
        if not account:
            slug = host.split('.')[0] if '.' in host else host
            try:
                account = Account.objects.filter(slug=slug, is_active=True).first()
            except:
                pass
        
        # Set tenant on request
        request.tenant = account
        
        # If user is authenticated and tenant exists, set account user relationship
        if request.user.is_authenticated and account:
            try:
                request.account_user = AccountUser.objects.get(
                    account=account,
                    user=request.user,
                    is_active=True
                )
            except AccountUser.DoesNotExist:
                request.account_user = None
        else:
            request.account_user = None
        
        response = self.get_response(request)
        return response


class TenantPermissionMiddleware:
    """
    Middleware to check tenant-specific permissions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip permission checks for admin and certain paths
        skip_paths = ['/admin/', '/api/auth/', '/api/accounts/create/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # If tenant exists but user is not authenticated, redirect to login
        if request.tenant and not request.user.is_authenticated:
            # For API requests, return 401
            if request.path.startswith('/api/'):
                from django.http import JsonResponse
                return JsonResponse({'error': 'Authentication required'}, status=401)
            # For web requests, you might want to redirect to login
            # This depends on your frontend setup
        
        # If user is authenticated but not a member of the tenant
        if request.tenant and request.user.is_authenticated and not request.account_user:
            raise Http404("You don't have access to this account")
        
        return self.get_response(request)
