from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
import secrets
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data (read-only, excludes sensitive info)"""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'bio', 'avatar', 'date_joined', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'bio'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password_confirm": _("Password confirmation doesn't match")}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        # Generate email verification token
        verification_token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)

        # Create user but keep inactive until email verified
        validated_data['email_verification_token'] = verification_token
        validated_data['email_verification_expires'] = expires_at
        validated_data['is_active'] = False

        user = User.objects.create_user(**validated_data)

        # Send verification email
        from apps.newsletter.email_service import email_service
        try:
            self._send_verification_email(user)
        except Exception as e:
            # Log error but don't fail registration - user can request new token
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to {user.email}: {e}")

        return user

    def _send_verification_email(self, user):
        """Send email verification email"""
        from django.conf import settings
        from django.template.loader import render_to_string

        subject = 'Verify your email address'
        context = {
            'user': user,
            'verification_url': f"{settings.FRONTEND_URL}/auth/verify-email/{user.email_verification_token}/"
        }

        html_message = render_to_string('auth/email_verification.html', context)
        text_message = render_to_string('auth/email_verification.txt', context)

        # Use the email service
        from apps.newsletter.email_service import email_service
        email_service._send_with_django(
            to_email=user.email,
            subject=subject,
            html_message=html_message,
            text_message=text_message
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'bio', 'avatar'
        ]
