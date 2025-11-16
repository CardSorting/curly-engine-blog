from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
import time
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer
)

User = get_user_model()


def rate_limit(max_requests=5, window_seconds=300):  # 5 requests per 5 minutes by default
    """
    Rate limiting decorator for auth endpoints
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get client IP
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()

            if not ip:
                ip = 'unknown'

            # Create cache key
            cache_key = f"ratelimit:{ip}:{func.__name__}"

            # Get current requests
            current_requests = cache.get(cache_key, [])

            # Remove expired requests
            current_time = time.time()
            current_requests = [req_time for req_time in current_requests if current_time - req_time < window_seconds]

            # Check if over limit
            if len(current_requests) >= max_requests:
                return Response(
                    {
                        'error': 'Too many requests. Please try again later.',
                        'retry_after': window_seconds
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Add current request
            current_requests.append(current_time)
            cache.set(cache_key, current_requests, window_seconds)

            # Call the function
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that includes user data in response with rate limiting
    """
    def dispatch(self, request, *args, **kwargs):
        # Apply rate limiting to login attempts
        result = rate_limit(max_requests=5, window_seconds=300)(lambda r: None)(request)
        if hasattr(result, 'status_code') and result.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return result
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Additional rate limiting for failed login attempts
        email = request.data.get('email', '')
        if email:
            # Check for failed attempts on this email
            cache_key = f"login_attempts:{email}"
            attempts = cache.get(cache_key, 0)

            if attempts >= 3:  # Lock out after 3 failed attempts
                return Response(
                    {'error': 'Too many failed login attempts. Please try again later.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Reset failed attempts on success
            if email:
                cache.delete(f"login_attempts:{email}")

            # Get the authenticated user
            serializer = self.get_serializer(data=request.data)
            token_data = serializer.validated_data

            # Decode access token to get user info (alternative approach)
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token_data['access'])
            user_id = access_token['user_id']

            user = User.objects.get(id=user_id)
            user_data = UserSerializer(user).data

            # Add user data to response
            response.data['user'] = user_data

        else:
            # Increment failed attempts on failure
            if email:
                attempts = cache.get(f"login_attempts:{email}", 0) + 1
                cache.set(f"login_attempts:{email}", attempts, 3600)  # 1 hour

        return response


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """
    Refresh JWT access token
    """
    refresh_token = request.data.get('refresh')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token),
        })
    except Exception as e:
        return Response(
            {'error': 'Invalid refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user info
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserRegisterView(generics.CreateAPIView):
    """
    User registration endpoint with rate limiting
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        # Apply rate limiting to registration attempts to prevent abuse
        result = rate_limit(max_requests=3, window_seconds=3600)(lambda r: None)(request)  # 3 registrations per hour
        if hasattr(result, 'status_code') and result.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return result
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view (get and update current user)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class EmailVerificationView(generics.GenericAPIView):
    """
    Email verification endpoint
    """
    permission_classes = [AllowAny]

    def get(self, request, token):
        """Verify email with token"""
        try:
            user = User.objects.get(
                email_verification_token=token,
                email_verification_expires__gt=timezone.now()
            )

            user.email_verified = True
            user.is_active = True
            user.email_verification_token = None
            user.email_verification_expires = None
            user.save()

            return Response({
                'message': 'Email verified successfully. You can now log in.',
                'user': UserSerializer(user).data
            })

        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(generics.GenericAPIView):
    """
    Resend email verification
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Resend verification email"""
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, email_verified=False, is_active=False)
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                'message': 'If an unverified account exists with this email, a verification email has been sent.'
            })

        # Generate new token
        import secrets
        from datetime import timedelta

        verification_token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)

        user.email_verification_token = verification_token
        user.email_verification_expires = expires_at
        user.save()

        # Send verification email
        try:
            serializer = UserCreateSerializer()
            serializer._send_verification_email(user)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to resend verification email to {user.email}: {e}")
            return Response(
                {'error': 'Failed to send verification email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message': 'Verification email sent successfully.'
        })
