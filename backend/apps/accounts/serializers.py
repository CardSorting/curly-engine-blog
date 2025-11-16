from rest_framework import serializers
from .models import Account, SubscriptionPlan, AccountUser


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'slug', 'description', 'monthly_price', 'yearly_price',
            'max_users', 'max_articles', 'max_storage_mb', 'features', 'is_active'
        ]


class AccountUserSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AccountUser
        fields = [
            'id', 'user', 'user_email', 'user_name', 'role', 'invited_by',
            'invited_at', 'joined_at', 'is_active'
        ]
        read_only_fields = ['id', 'invited_by', 'invited_at', 'joined_at']


class AccountSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    subscription_plan_id = serializers.UUIDField(write_only=True, required=False)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    account_users = AccountUserSerializer(source='account_users', many=True, read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'slug', 'description', 'owner', 'owner_email',
            'subscription_plan', 'subscription_plan_id', 'subscription_status',
            'trial_ends_at', 'subscription_ends_at', 'current_article_count',
            'current_storage_mb', 'current_user_count', 'custom_domain',
            'domain_verified', 'is_active', 'created_at', 'updated_at',
            'account_users'
        ]
        read_only_fields = [
            'id', 'owner', 'subscription_status', 'trial_ends_at',
            'subscription_ends_at', 'current_article_count', 'current_storage_mb',
            'current_user_count', 'domain_verified', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        # Set the owner from the current user
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class AccountCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for account creation"""
    class Meta:
        model = Account
        fields = ['name', 'slug', 'description']
    
    def create(self, validated_data):
        # Set the owner from the current user
        user = self.context['request'].user
        validated_data['owner'] = user
        
        # Set default trial period (14 days)
        from django.utils import timezone
        from datetime import timedelta
        validated_data['trial_ends_at'] = timezone.now() + timedelta(days=14)
        
        account = super().create(validated_data)
        
        # Create AccountUser relationship for the owner
        AccountUser.objects.create(
            account=account,
            user=user,
            role='admin',
            joined_at=timezone.now()
        )
        
        # Update user's default account
        user.default_account = account
        user.save()
        
        return account


class AccountUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating account settings"""
    class Meta:
        model = Account
        fields = ['name', 'description', 'custom_domain']
    
    def validate_custom_domain(self, value):
        if value:
            # Basic domain validation
            import re
            domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
            if not re.match(domain_pattern, value):
                raise serializers.ValidationError("Invalid domain format")
        return value
