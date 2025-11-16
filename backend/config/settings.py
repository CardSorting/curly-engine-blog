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
    'django_filters',
    'storages',
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
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

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
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

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
