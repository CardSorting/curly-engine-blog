def tenant_context(request):
    """
    Add tenant information to template context
    """
    context = {}
    
    if hasattr(request, 'tenant') and request.tenant:
        context['tenant'] = request.tenant
        context['tenant_name'] = request.tenant.name
        context['tenant_slug'] = request.tenant.slug
        context['is_custom_domain'] = bool(request.tenant.custom_domain)
    
    if hasattr(request, 'account_user') and request.account_user:
        context['account_user'] = request.account_user
        context['user_role'] = request.account_user.role
        context['can_manage_users'] = request.account_user.can_manage_users
        context['can_manage_billing'] = request.account_user.can_manage_billing
        context['can_publish_articles'] = request.account_user.can_publish_articles
        context['can_edit_all_articles'] = request.account_user.can_edit_all_articles
        context['can_view_analytics'] = request.account_user.can_view_analytics
    
    return context
