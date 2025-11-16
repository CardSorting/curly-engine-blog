from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .models import Account, SubscriptionPlan, AccountUser
from .serializers import (
    AccountSerializer, AccountCreateSerializer, AccountUpdateSerializer,
    AccountPublicSerializer, SubscriptionPlanSerializer, AccountUserSerializer
)
from .permissions import (
    IsAccountMember, IsAccountAdmin, CanManageUsers, CanManageBilling,
    IsAccountOwner, HasSubscriptionAccess
)


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
        """Upgrade subscription plan"""
        account = self.get_object()
        plan_id = request.data.get('plan_id')
        
        if not plan_id:
            return Response({'error': 'Plan ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Invalid plan'}, status=status.HTTP_404_NOT_FOUND)
        
        # Here you would integrate with Stripe or other payment processor
        # For now, we'll just update the plan
        account.subscription_plan = plan
        account.subscription_status = 'active'
        account.subscription_ends_at = timezone.now() + timedelta(days=30)
        account.save()
        
        return Response({'message': 'Plan upgraded successfully'})
    
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

        data = {
            'subscription_status': account.subscription_status,
            'subscription_plan': SubscriptionPlanSerializer(account.subscription_plan).data if account.subscription_plan else None,
            'trial_ends_at': account.trial_ends_at,
            'subscription_ends_at': account.subscription_ends_at,
            'stripe_customer_id': account.stripe_customer_id,
            'stripe_subscription_id': account.stripe_subscription_id,
        }

        return Response(data)

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
