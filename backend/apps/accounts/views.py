from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from django.conf import settings
from datetime import timedelta
from .billing import BillingService

from .models import Account, SubscriptionPlan, AccountUser
from .serializers import (
    AccountSerializer, AccountCreateSerializer, AccountUpdateSerializer,
    AccountPublicSerializer, SubscriptionPlanSerializer, AccountUserSerializer
)
from .permissions import (
    IsAccountMember, IsAccountAdmin, CanManageUsers, CanManageBilling,
    IsAccountOwner, HasSubscriptionAccess
)


def csrf_failure(request, reason=""):
    """
    Custom CSRF failure handler that returns a 403 with JSON response
    instead of the default HTML page for better API integration
    """
    from django.http import JsonResponse
    from django.middleware.csrf import get_token

    # Log the CSRF failure for security monitoring
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"CSRF failure for {request.path}: {reason}")

    # Return JSON response for API clients
    if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'CSRF token validation failed',
            'message': 'Your session may have expired. Please refresh the page and try again.',
            'csrf_token': get_token(request)
        }, status=403)

    # Fall back to HTML response for web clients
    from django.template import loader
    from django.http import HttpResponseForbidden
    t = loader.get_template('403_csrf_failure.html')
    return HttpResponseForbidden(t.render({
        'reason': reason,
        'request': request,
        'csrf_token': get_token(request)
    }, request))


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing accounts (blogs/sites)
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return accounts where the user is a member
        return Account.objects.filter(
            account_users__user=self.request.user,
            account_users__is_active=True
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AccountCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AccountUpdateSerializer
        return AccountSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAccountAdmin()]
        elif self.action in ['manage_users', 'billing_info']:
            return [IsAuthenticated(), CanManageBilling()]
        elif self.action in ['public_browse', 'public_detail']:
            return [AllowAny()]
        else:
            return [IsAuthenticated(), IsAccountMember()]
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def subscription_status(self, request, pk=None):
        """Get current subscription status and usage"""
        account = self.get_object()
        
        data = {
            'subscription_status': account.subscription_status,
            'subscription_plan': SubscriptionPlanSerializer(account.subscription_plan).data if account.subscription_plan else None,
            'trial_ends_at': account.trial_ends_at,
            'subscription_ends_at': account.subscription_ends_at,
            'usage': {
                'articles': {
                    'current': account.current_article_count,
                    'limit': account.subscription_plan.max_articles if account.subscription_plan else 10,
                    'can_create': account.can_create_article
                },
                'users': {
                    'current': account.current_user_count,
                    'limit': account.subscription_plan.max_users if account.subscription_plan else 1,
                    'can_add': account.can_add_user
                },
                'storage': {
                    'current': account.current_storage_mb,
                    'limit': account.subscription_plan.max_storage_mb if account.subscription_plan else 100,
                }
            },
            'is_trial_active': account.is_trial_active,
            'is_subscription_active': account.is_subscription_active
        }
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def upgrade_plan(self, request, pk=None):
        """Upgrade subscription plan with Stripe integration (Industry Standard)"""
        account = self.get_object()
        plan_id = request.data.get('plan_id')
        billing_type = request.data.get('billing_type', 'monthly')  # 'monthly' or 'yearly'

        if not plan_id:
            return Response({'error': 'Plan ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if billing_type not in ['monthly', 'yearly']:
            return Response({'error': 'Billing type must be either "monthly" or "yearly"'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Invalid plan'}, status=status.HTTP_404_NOT_FOUND)

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Rate limiting (industry standard protection)
        if not BillingService.check_rate_limit(account, 'upgrade_plan'):
            return Response({
                'error': 'Too many billing operations. Please wait a moment before trying again.',
                'retry_after': 3600  # seconds
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            # Validate account limits before upgrade
            warnings = BillingService.validate_account_limits(account, plan)
            if warnings:
                # Allow upgrade but warn about limit issues
                print(f"Account {account.slug} has limit warnings: {warnings}")

            if account.stripe_subscription_id and account.subscription_status in ['active', 'past_due']:
                # Update existing subscription
                result = BillingService.update_subscription(account, plan, billing_type)

                # Log the successful upgrade
                BillingService.log_billing_event(
                    account, 'subscription_upgraded',
                    {
                        'from_plan': account.subscription_plan.name if account.subscription_plan else None,
                        'to_plan': plan.name,
                        'billing_type': billing_type,
                        'subscription_id': result.get('subscription_id')
                    },
                    request.user
                )

                return Response({
                    'message': 'Plan updated successfully',
                    'subscription_id': result.get('subscription_id'),
                    'status': result.get('status'),
                    'warnings': warnings
                })
            else:
                # Create new subscription with audit logging
                result = BillingService.create_subscription_with_audit(account, plan, billing_type, request.user)

                return Response({
                    'message': 'Subscription created successfully',
                    'subscription_id': result.get('subscription_id'),
                    'client_secret': result.get('client_secret'),  # For payment confirmation on frontend
                    'status': result.get('status'),
                    'warnings': warnings
                })

        except ValueError as e:
            BillingService.log_billing_event(
                account, 'subscription_upgrade_failed',
                {'plan_id': plan_id, 'billing_type': billing_type, 'error': str(e)},
                request.user
            )
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            BillingService.log_billing_event(
                account, 'subscription_upgrade_error',
                {'plan_id': plan_id, 'billing_type': billing_type, 'error': str(e)},
                request.user
            )
            return Response({'error': 'Billing service error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get', 'post'])
    def manage_users(self, request, pk=None):
        """Manage account users"""
        account = self.get_object()
        
        if request.method == 'GET':
            users = AccountUser.objects.filter(account=account, is_active=True)
            serializer = AccountUserSerializer(users, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Invite a new user
            email = request.data.get('email')
            role = request.data.get('role', 'author')
            
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not account.can_add_user:
                return Response({'error': 'User limit reached'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already exists
            from apps.users.models import User
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create a new user (you might want to send an invitation email instead)
                user = User.objects.create_user(
                    email=email,
                    username=email.split('@')[0],
                    password=User.objects.make_random_password()
                )
            
            # Check if user is already a member
            if AccountUser.objects.filter(account=account, user=user).exists():
                return Response({'error': 'User is already a member'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create account user relationship
            account_user = AccountUser.objects.create(
                account=account,
                user=user,
                role=role,
                invited_by=request.user,
                invited_at=timezone.now()
            )
            
            # Update user count
            account.current_user_count = AccountUser.objects.filter(account=account, is_active=True).count()
            account.save()
            
            return Response(AccountUserSerializer(account_user).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_user(self, request, pk=None):
        """Remove a user from the account"""
        account = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            account_user = AccountUser.objects.get(account=account, user_id=user_id)
            
            # Don't allow removing the owner
            if account_user.user == account.owner:
                return Response({'error': 'Cannot remove account owner'}, status=status.HTTP_400_BAD_REQUEST)
            
            account_user.is_active = False
            account_user.save()
            
            # Update user count
            account.current_user_count = AccountUser.objects.filter(account=account, is_active=True).count()
            account.save()
            
            return Response({'message': 'User removed successfully'})
            
        except AccountUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def billing_info(self, request, pk=None):
        """Get billing information"""
        account = self.get_object()

        payment_methods = []
        if getattr(settings, 'STRIPE_SECRET_KEY', None) and account.stripe_customer_id:
            payment_methods = BillingService.get_payment_methods(account)

        data = {
            'subscription_status': account.subscription_status,
            'subscription_plan': SubscriptionPlanSerializer(account.subscription_plan).data if account.subscription_plan else None,
            'trial_ends_at': account.trial_ends_at,
            'subscription_ends_at': account.subscription_ends_at,
            'stripe_customer_id': account.stripe_customer_id,
            'stripe_subscription_id': account.stripe_subscription_id,
            'payment_methods': payment_methods,
        }

        return Response(data)

    @action(detail=True, methods=['post'])
    def cancel_subscription(self, request, pk=None):
        """Cancel subscription"""
        account = self.get_object()
        cancel_immediately = request.data.get('cancel_immediately', False)  # Boolean flag

        if not account.stripe_subscription_id:
            return Response({'error': 'No active subscription'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            success = BillingService.cancel_subscription(account, cancel_at_period_end=not cancel_immediately)

            if success:
                message = 'Subscription cancelled successfully'
                if not cancel_immediately:
                    message += ' - will remain active until end of billing period'
                return Response({'message': message})
            else:
                return Response({'error': 'Failed to cancel subscription'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': 'Billing service error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reactivate_subscription(self, request, pk=None):
        """Reactivate a cancelled subscription"""
        account = self.get_object()

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if not account.stripe_subscription_id:
            return Response({'error': 'No subscription found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            import stripe
            subscription = stripe.Subscription.retrieve(account.stripe_subscription_id)

            if subscription.cancel_at_period_end:
                # Remove the cancellation
                stripe.Subscription.modify(
                    account.stripe_subscription_id,
                    cancel_at_period_end=False
                )

                # Update account status
                account.subscription_status = subscription.status
                account.save()

                return Response({'message': 'Subscription reactivated successfully'})
            else:
                return Response({'error': 'Subscription is not scheduled for cancellation'}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({'error': f'Stripe error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Billing service error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def payment_methods(self, request, pk=None):
        """Get payment methods for the account"""
        account = self.get_object()

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            payment_methods = BillingService.get_payment_methods(account)
            return Response({'payment_methods': payment_methods})

        except Exception as e:
            return Response({'error': 'Failed to retrieve payment methods'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ============ INDUSTRY STANDARD BILLING ENDPOINTS ============

    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Get invoice history for the account (Industry Standard)"""
        account = self.get_object()
        limit = int(request.query_params.get('limit', 20))

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            invoices = BillingService.get_invoices(account, limit=min(limit, 100))  # Max 100 invoices
            return Response({'invoices': invoices})

        except Exception as e:
            return Response({'error': 'Failed to retrieve invoices'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def billing_analytics(self, request, pk=None):
        """Get comprehensive billing analytics (Industry Standard)"""
        account = self.get_object()

        try:
            analytics = BillingService.get_subscription_analytics(account)

            # Add invoice revenue data if Stripe is configured
            if getattr(settings, 'STRIPE_SECRET_KEY', None) and account.stripe_customer_id:
                try:
                    total_invoices = len(BillingService.get_invoices(account, 100))
                    analytics['total_invoices'] = total_invoices
                except:
                    analytics['total_invoices'] = 0

            return Response(analytics)

        except Exception as e:
            return Response({'error': 'Failed to retrieve billing analytics'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def billing_alerts(self, request, pk=None):
        """Get billing alerts and notifications (Industry Standard)"""
        account = self.get_object()

        try:
            alerts = BillingService.get_billing_alerts(account)
            return Response({'alerts': alerts})

        except Exception as e:
            return Response({'error': 'Failed to retrieve billing alerts'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def calculate_proration(self, request, pk=None):
        """Calculate proration amount for plan changes (Industry Standard)"""
        account = self.get_object()
        plan_id = request.data.get('plan_id')
        billing_type = request.data.get('billing_type', 'monthly')

        if not plan_id:
            return Response({'error': 'Plan ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Invalid plan'}, status=status.HTTP_404_NOT_FOUND)

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            proration = BillingService.calculate_proration(account, plan, billing_type)
            return Response(proration)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Failed to calculate proration'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def apply_coupon(self, request, pk=None):
        """Apply discount coupon to subscription (Industry Standard)"""
        account = self.get_object()
        coupon_code = request.data.get('coupon_code')

        if not coupon_code:
            return Response({'error': 'Coupon code is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not coupon_code.strip():
            return Response({'error': 'Coupon code cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            result = BillingService.apply_coupon(account, coupon_code.strip().upper(), request.user)
            return Response(result)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Failed to apply coupon'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def pause_subscription(self, request, pk=None):
        """Pause subscription billing (Industry Standard)"""
        account = self.get_object()
        reason = request.data.get('reason', '')

        if not account.stripe_subscription_id:
            return Response({'error': 'No active subscription'}, status=status.HTTP_400_BAD_REQUEST)

        if account.subscription_status != 'active':
            return Response({'error': 'Subscription is not active'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            success = BillingService.pause_subscription(account, reason, request.user)

            if success:
                return Response({'message': 'Subscription paused successfully'})
            else:
                return Response({'error': 'Failed to pause subscription'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': 'Billing service error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def resume_subscription(self, request, pk=None):
        """Resume paused subscription (Industry Standard)"""
        account = self.get_object()

        if not account.stripe_subscription_id:
            return Response({'error': 'No subscription found'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if Stripe is configured
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({'error': 'Billing service is not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            success = BillingService.resume_subscription(account, request.user)

            if success:
                return Response({'message': 'Subscription resumed successfully'})
            else:
                return Response({'error': 'Failed to resume subscription'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': 'Billing service error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def extend_trial(self, request, pk=None):
        """Extend trial period (Industry Standard - Admin Feature)"""
        account = self.get_object()
        days = request.data.get('days')
        reason = request.data.get('reason', 'Administrative extension')

        if days is None:
            return Response({'error': 'Number of days is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            days = int(days)
            if days <= 0 or days > 365:
                return Response({'error': 'Days must be between 1 and 365'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid days value'}, status=status.HTTP_400_BAD_REQUEST)

        if not account.is_trial_active:
            return Response({'error': 'Account is not on trial'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            success = BillingService.manage_trial_extension(account, days, reason, request.user)

            if success:
                return Response({
                    'message': f'Trial extended by {days} days',
                    'new_trial_end': account.trial_ends_at.isoformat()
                })
            else:
                return Response({'error': 'Failed to extend trial'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': 'Billing service error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public_browse(self, request):
        """Public endpoint for browsing all active accounts"""
        search_query = request.query_params.get('search', '').strip()

        # Query all active accounts
        accounts = Account.objects.filter(is_active=True).order_by('-created_at')

        # Apply search filter if provided
        if search_query:
            accounts = accounts.filter(
                models.Q(name__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(slug__icontains=search_query)
            )

        serializer = AccountPublicSerializer(accounts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def public_detail(self, request, pk=None):
        """Public endpoint for viewing account details by slug"""
        try:
            account = Account.objects.get(slug=pk, is_active=True)
            serializer = AccountPublicSerializer(account)
            return Response(serializer.data)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing available subscription plans
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
