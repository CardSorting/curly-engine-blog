from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Sites framework
SITE_ID = 1

# Apps
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'csp',
    'django_filters',
    'storages',
    'channels',  # WebSocket support
    # 'drf_spectacular',  # Commented out for testing

    # Local apps
    'apps.core',  # Core management commands
    'apps.accounts',  # SAAS account management
    'apps.users',
    'apps.articles',
    'apps.media',
    'apps.newsletter',
    'apps.analytics',
    'apps.seo',
    'apps.content_analysis',  # Content analysis and AI writing suggestions
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Before CommonMiddleware
    'csp.middleware.CSPMiddleware',  # Content Security Policy
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Security enhancements
    'django.middleware.security.SecurityMiddleware',

    # SAAS tenant middleware
    'apps.accounts.middleware.TenantMiddleware',
    'apps.accounts.middleware.TenantPermissionMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.accounts.context_processors.tenant_context',  # SAAS tenant context
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
import sys
if 'pytest' in sys.modules or any('pytest' in arg for arg in sys.argv):
    # Use SQLite for tests
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# SQLite configuration (commented out)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Auth
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.users.validators.CustomPasswordValidator',
    },
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Commented out for testing
}

# JWT Settings - Enhanced Security Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    # Enhanced security settings
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    #'ISSUER': SITE_URL,  # Commented out to fix import order
    'JSON_ENCODER': None,

    # Token security features
    'JWK_URL': None,
    'LEEWAY': 0,

    # Authentication rules
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    # Token claims
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    # Additional security
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',

    # Sliding token settings (optional but more secure)
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=24),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# CORS
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173,http://localhost:8001'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# File Storage
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # AWS settings
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Email (Resend)
RESEND_API_KEY = config('RESEND_API_KEY', default='')
FROM_EMAIL = config('FROM_EMAIL', default='noreply@example.com')

# Stripe Billing
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')
STRIPE_WEBHOOK_IP_WHITELIST_ENABLED = config('STRIPE_WEBHOOK_IP_WHITELIST_ENABLED', default=False, cast=bool)
STRIPE_WEBHOOK_IP_WHITELIST = config('STRIPE_WEBHOOK_IP_WHITELIST', default=[
    '54.187.174.169/32',  # Stripe webhook IPs (test mode)
    '54.187.205.235/32',
    '54.187.216.72/32',
    '35.154.171.200/32',  # Additional Stripe IPs
    '3.130.192.231/32',
    '13.235.14.237/32',
    '13.235.122.149/32',
    '18.211.135.69/32',
    '99.79.142.11/32',
]).split(',') if config('STRIPE_WEBHOOK_IP_WHITELIST', default=None) else [
    # Default Stripe webhook IP ranges
    '54.187.174.169/32', '54.187.205.235/32', '54.187.216.72/32',
    '35.154.171.200/32', '3.130.192.231/32', '13.235.14.237/32',
    '13.235.122.149/32', '18.211.135.69/32', '99.79.142.11/32'
]

# Site URL (for email links) - Used for email verification links
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
SITE_URL = config('SITE_URL', default='http://localhost:3000')

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# DRF Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Chronicle Blog API',
    'DESCRIPTION': 'A RESTful API for a content management system with blog functionality, user authentication, media management, newsletter system, and SEO optimization.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
    'COMPONENT_SPLIT_REQUEST': True,
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
    ],
    'SECURITY': [
        {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    ],
    'SECURITY_REQUIREMENTS': [
        {
            'BearerAuth': []
        }
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and profile management'},
        {'name': 'Articles', 'description': 'Article and content management'},
        {'name': 'Topics', 'description': 'Content categorization'},
        {'name': 'Pages', 'description': 'Static page content'},
        {'name': 'Media', 'description': 'File upload and media management'},
        {'name': 'Analytics', 'description': 'Page view tracking and analytics'},
        {'name': 'Newsletter', 'description': 'Newsletter subscription and campaigns'},
        {'name': 'SEO', 'description': 'Search engine optimization'},
    ],
}

# Cache configuration for rate limiting (production ready)
CACHE_BACKEND = config('CACHE_BACKEND', default='locmem://')
if CACHE_BACKEND.startswith('redis://') or CACHE_BACKEND.startswith('rediss://'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': CACHE_BACKEND,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True if not DEBUG else False,
            }
        }
    }
elif CACHE_BACKEND.startswith('memcached://'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': CACHE_BACKEND,
        }
    }
else:
    # Default to locmem for development/local testing
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Security Headers - Enterprise-grade CSP and security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = not DEBUG  # Only enforce HTTPS in production

# Content Security Policy (CSP) - Enterprise-grade protection
# Enhanced CSP policies for comprehensive XSS protection
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'strict-dynamic'",  # Allow scripts with valid nonces
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
    "*.googletagmanager.com",
    "*.google-analytics.com",
    "*.stripe.com",
)
CSP_SCRIPT_SRC_ELEM = (
    "'self'",
    "'unsafe-inline'",  # For inline scripts with nonces
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
    "*.googletagmanager.com",
    "*.google-analytics.com",
    "*.stripe.com",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",  # Allow inline styles for dynamic content
    "https://fonts.googleapis.com",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
)
CSP_STYLE_SRC_ELEM = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
    "data:",
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "blob:",
    "https://*.amazonaws.com",
    "https://*.cloudflare.com",
    "*.googletagmanager.com",
    "*.google-analytics.com",
    "*.stripe.com",
    "*.gravatar.com",  # For user avatars
)
CSP_CONNECT_SRC = (
    "'self'",
    "https://*.amazonaws.com",
    "https://api.stripe.com",
    "https://js.stripe.com",
    "*.googletagmanager.com",
    "*.google-analytics.com",
    "https://api.resend.com",  # Email service
)
CSP_FRAME_SRC = (
    "'self'",
    "*.stripe.com",
)
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'", "*.stripe.com")
CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']

# Additional CSP directives for enhanced security
CSP_WORKER_SRC = ("'self'",)  # For service workers
CSP_MANIFEST_SRC = ("'self'",)
CSP_MEDIA_SRC = ("'self'", "data:")
CSP_CHILD_SRC = ("'self'",)  # For web workers

# Frame ancestors for clickjacking protection (more restrictive than X-Frame-Options)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_UPGRADE_INSECURE_REQUESTS = True if not DEBUG else False

# CSRF Protection
CSRF_FAILURE_VIEW = 'apps.accounts.views.csrf_failure'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG

# Feature Policy / Permissions Policy
FEATURE_POLICY = {
    "geolocation": "'none'",
    "camera": "'none'",
    "microphone": "'none'",
    "payment": "'self'",
    "usb": "'none'",
}

# Security middleware settings
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Celery Configuration - Enterprise Background Task Processing
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=config('REDIS_URL', default='redis://localhost:6379/0'))
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=config('REDIS_URL', default='redis://localhost:6379/0'))
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart worker after 1000 tasks

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Channels Configuration - WebSocket Support for Collaborative Editing
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL', default='redis://localhost:6379/1')],
            'capacity': 1000,  # Number of messages that can be stored
            'expiry': 60,  # Message expiry in seconds
            'group_expiry': 86400,  # Group expiry in seconds (24 hours)
            'capacity': 2000,  # Increased capacity for collaborative sessions
        },
    },
}
