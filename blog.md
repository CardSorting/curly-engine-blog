# Chronicle Django Backend - Technical Specification

## Purpose
RESTful API backend that serves a decoupled React frontend. Handles content management, newsletter system, and auto-generates SEO data.

---

## Core Requirements

### Python & Django Versions
- Python 3.11 or 3.12
- Django 5.0+
- PostgreSQL 15+

### Required Python Packages

```txt
# requirements/base.txt

# Django Core
Django==5.0.3
psycopg2-binary==2.9.9          # PostgreSQL adapter

# REST API
djangorestframework==3.14.0      # REST framework
djangorestframework-simplejwt==5.3.1  # JWT authentication
django-cors-headers==4.3.1       # CORS handling
django-filter==24.1              # API filtering

# File Storage
django-storages==1.14.2          # S3 integration
boto3==1.34.51                   # AWS SDK
Pillow==10.2.0                   # Image processing

# Email
resend==0.7.0                    # Email API

# Content Processing
markdown==3.5.2                  # Markdown to HTML
bleach==6.1.0                    # HTML sanitization

# Utilities
python-decouple==3.8             # Environment variables
python-slugify==8.0.4            # Slug generation
```

```txt
# requirements/development.txt

-r base.txt

# Testing
pytest==8.0.2
pytest-django==4.8.0
pytest-cov==4.1.0
factory-boy==3.3.0               # Test fixtures

# Code Quality
black==24.2.0                    # Code formatting
flake8==7.0.0                    # Linting
isort==5.13.2                    # Import sorting

# Development Tools
django-extensions==3.2.3         # Management commands
ipython==8.22.1                  # Better shell
```

---

## Project Structure

```
backend/
├── config/                          # Project configuration
│   ├── __init__.py
│   ├── settings.py                  # Main settings
│   ├── urls.py                      # Root URL config
│   ├── wsgi.py                      # WSGI config
│   └── asgi.py                      # ASGI config
│
├── apps/                            # Django apps
│   ├── __init__.py
│   │
│   ├── users/                       # User management
│   │   ├── __init__.py
│   │   ├── models.py               # User model
│   │   ├── serializers.py          # User serializers
│   │   ├── views.py                # Auth views
│   │   ├── urls.py                 # User URLs
│   │   └── admin.py                # Admin config
│   │
│   ├── articles/                    # Article management
│   │   ├── __init__.py
│   │   ├── models.py               # Article, Topic models
│   │   ├── serializers.py          # Article serializers
│   │   ├── views.py                # Article views
│   │   ├── urls.py                 # Article URLs
│   │   ├── admin.py                # Admin config
│   │   ├── signals.py              # Auto-generation logic
│   │   └── tests/
│   │       ├── test_models.py
│   │       └── test_api.py
│   │
│   ├── media/                       # Media library
│   │   ├── __init__.py
│   │   ├── models.py               # Media model
│   │   ├── serializers.py          # Media serializers
│   │   ├── views.py                # Upload views
│   │   ├── urls.py                 # Media URLs
│   │   └── utils.py                # Image processing
│   │
│   ├── newsletter/                  # Newsletter system
│   │   ├── __init__.py
│   │   ├── models.py               # Subscriber, Newsletter models
│   │   ├── serializers.py          # Newsletter serializers
│   │   ├── views.py                # Newsletter views
│   │   ├── urls.py                 # Newsletter URLs
│   │   ├── services.py             # Email sending logic
│   │   └── templates/
│   │       ├── confirmation.html   # Confirmation email
│   │       └── newsletter.html     # Newsletter email
│   │
│   ├── analytics/                   # Simple analytics
│   │   ├── __init__.py
│   │   ├── models.py               # PageView model
│   │   ├── views.py                # Analytics views
│   │   └── urls.py                 # Analytics URLs
│   │
│   └── seo/                         # SEO generation
│       ├── __init__.py
│       ├── generators.py           # Sitemap, RSS, Schema
│       ├── views.py                # Sitemap/RSS views
│       └── urls.py                 # SEO URLs
│
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── pytest.ini
├── .env.example
└── README.md
```

---

## Database Models

### User Model (apps/users/models.py)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    """
    Extended user model for authors.
    Uses email as username.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # For createsuperuser
    
    def __str__(self):
        return self.email
```

**Why**: Single author system needs basic user with bio and avatar for about page.

---

### Article Models (apps/articles/models.py)

```python
from django.db import models
from django.utils.text import slugify
import uuid

class Topic(models.Model):
    """
    Content categories (Technology, Writing, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#0066FF')  # Hex color
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """
    Core content model - blog posts/articles
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField()  # Markdown format
    excerpt = models.TextField(blank=True, max_length=300)
    
    # Relationships
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='articles')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    hero_image = models.ForeignKey('media.Media', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-calculated fields
    word_count = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=0)  # minutes
    
    # Analytics
    view_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['author', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-generate excerpt from content
        if not self.excerpt and self.content:
            self.excerpt = self.content[:300]
        
        # Calculate word count
        self.word_count = len(self.content.split())
        
        # Calculate reading time (avg 200 words/min)
        self.reading_time = max(1, self.word_count // 200)
        
        # Set published_at on first publish
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)


class Page(models.Model):
    """
    Static pages (About, Now, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField()  # Markdown
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

**Why**: Core content models. Article handles all blog posts with auto-calculations. Topic for categorization. Page for static content.

---

### Media Model (apps/media/models.py)

```python
from django.db import models
from PIL import Image
import uuid

class Media(models.Model):
    """
    Uploaded images and files
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # File
    file = models.ImageField(upload_to='uploads/%Y/%m/')
    filename = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    
    # Metadata (auto-filled)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField()  # bytes
    mime_type = models.CharField(max_length=100)
    
    # Owner
    uploaded_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Media'
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        # Extract image dimensions
        if self.file and not self.width:
            img = Image.open(self.file)
            self.width, self.height = img.size
        
        # Set file size
        if self.file and not self.file_size:
            self.file_size = self.file.size
        
        # Set filename if not provided
        if not self.filename:
            self.filename = self.file.name
        
        super().save(*args, **kwargs)
```

**Why**: Stores uploaded images with automatic metadata extraction.

---

### Newsletter Models (apps/newsletter/models.py)

```python
from django.db import models
import uuid
import secrets

class Subscriber(models.Model):
    """
    Newsletter subscribers with double opt-in
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),     # Awaiting confirmation
        ('active', 'Active'),       # Confirmed and subscribed
        ('unsubscribed', 'Unsubscribed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Security tokens
    confirm_token = models.CharField(max_length=64, unique=True, db_index=True)
    unsubscribe_token = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Generate tokens on creation
        if not self.confirm_token:
            self.confirm_token = secrets.token_urlsafe(32)
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class Newsletter(models.Model):
    """
    Sent newsletters (history tracking)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=200)
    custom_message = models.TextField(blank=True)
    
    # Articles included (many-to-many)
    articles = models.ManyToManyField('articles.Article', blank=True)
    
    # Sending metadata
    recipient_count = models.IntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.subject} ({self.sent_at})"
```

**Why**: Subscriber model handles email collection with secure tokens. Newsletter model tracks what was sent and when.

---

### Analytics Model (apps/analytics/models.py)

```python
from django.db import models

class PageView(models.Model):
    """
    Simple page view tracking (aggregated by day)
    """
    date = models.DateField()
    article = models.ForeignKey('articles.Article', on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['date', 'article']
        indexes = [
            models.Index(fields=['date', 'article']),
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"{self.article.title} - {self.date}: {self.views} views"
```

**Why**: Simple daily aggregation. No user tracking, just counts.

---

## Django Settings Configuration

### Base Settings (config/settings.py)

```python
from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Apps
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'storages',
    
    # Local apps
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
]

ROOT_URLCONF = 'config.urls'

# Database
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

# Auth
AUTH_USER_MODEL = 'users.User'

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
    default='http://localhost:3000,http://localhost:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True
    
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

# Site URL (for email links)
SITE_URL = config('SITE_URL', default='http://localhost:3000')
```

**Why**: Centralizes all configuration with environment variables. Supports both local

---

## API Endpoints Structure

### Authentication Endpoints

```
POST   /api/auth/token/           # Get JWT token (login)
POST   /api/auth/token/refresh/   # Refresh token
GET    /api/auth/me/              # Get current user info
```

### Article Endpoints

```
GET    /api/articles/             # List published articles (public)
POST   /api/articles/             # Create article (auth required)
GET    /api/articles/{slug}/      # Get single article
PUT    /api/articles/{slug}/      # Update article (auth)
DELETE /api/articles/{slug}/      # Delete article (auth)
PATCH  /api/articles/{slug}/publish/  # Publish draft (auth)
```

### Topic Endpoints

```
GET    /api/topics/               # List all topics
POST   /api/topics/               # Create topic (auth)
GET    /api/topics/{slug}/        # Get topic details + articles
PUT    /api/topics/{slug}/        # Update topic (auth)
DELETE /api/topics/{slug}/        # Delete topic (auth)
```

### Media Endpoints

```
GET    /api/media/                # List media (auth)
POST   /api/media/upload/         # Upload file (auth)
GET    /api/media/{id}/           # Get media details (auth)
DELETE /api/media/{id}/           # Delete media (auth)
```

### Newsletter Endpoints

```
# Public
POST   /api/newsletter/subscribe/              # Subscribe
GET    /api/newsletter/confirm/{token}/        # Confirm subscription
GET    /api/newsletter/unsubscribe/{token}/    # Unsubscribe

# Admin only
GET    /api/newsletter/subscribers/            # List subscribers
POST   /api/newsletter/subscribers/export/     # Export CSV
DELETE /api/newsletter/subscribers/{id}/       # Delete subscriber
POST   /api/newsletter/send/                   # Send newsletter
GET    /api/newsletter/history/                # Sent newsletters
```

### Analytics Endpoints

```
POST   /api/analytics/track/      # Track page view (public)
GET    /api/analytics/dashboard/  # Dashboard stats (auth)
GET    /api/analytics/articles/   # Article performance (auth)
```

### SEO Endpoints

```
GET    /sitemap.xml               # XML sitemap
GET    /rss.xml                   # RSS feed (all articles)
GET    /rss/topic/{slug}.xml      # Topic-specific RSS feed
```

---

## Key Backend Services

### Email Service (apps/newsletter/services.py)

**Purpose**: Send emails via Resend API

```python
import resend
from django.conf import settings
from django.template.loader import render_to_string

resend.api_key = settings.RESEND_API_KEY

class EmailService:
    @staticmethod
    def send_confirmation_email(subscriber):
        """Send double opt-in confirmation email"""
        confirm_url = f"{settings.SITE_URL}/confirm/{subscriber.confirm_token}"
        
        html = render_to_string('newsletter/confirmation.html', {
            'confirm_url': confirm_url,
        })
        
        resend.Emails.send({
            'from': settings.FROM_EMAIL,
            'to': subscriber.email,
            'subject': 'Confirm your subscription',
            'html': html,
        })
    
    @staticmethod
    def send_newsletter(newsletter, subscribers):
        """Send newsletter to active subscribers"""
        for subscriber in subscribers:
            unsubscribe_url = f"{settings.SITE_URL}/unsubscribe/{subscriber.unsubscribe_token}"
            
            html = render_to_string('newsletter/newsletter.html', {
                'subject': newsletter.subject,
                'custom_message': newsletter.custom_message,
                'articles': newsletter.articles.all(),
                'unsubscribe_url': unsubscribe_url,
            })
            
            resend.Emails.send({
                'from': settings.FROM_EMAIL,
                'to': subscriber.email,
                'subject': newsletter.subject,
                'html': html,
            })
```

**Why**: Centralizes email sending logic. Uses templates for consistent formatting.

---

### SEO Generators (apps/seo/generators.py)

**Purpose**: Auto-generate sitemap, RSS feeds, schema markup

```python
from django.urls import reverse
from apps.articles.models import Article
import xml.etree.ElementTree as ET

class SitemapGenerator:
    @staticmethod
    def generate():
        """Generate XML sitemap"""
        urlset = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        
        # Add published articles
        articles = Article.objects.filter(status='published')
        for article in articles:
            url = ET.SubElement(urlset, 'url')
            ET.SubElement(url, 'loc').text = f"https://yoursite.com/{article.slug}"
            ET.SubElement(url, 'lastmod').text = article.updated_at.isoformat()
            ET.SubElement(url, 'changefreq').text = 'monthly'
            ET.SubElement(url, 'priority').text = '0.8'
        
        return ET.tostring(urlset, encoding='unicode')

class SchemaGenerator:
    @staticmethod
    def generate_article_schema(article):
        """Generate Article schema JSON-LD"""
        return {
            '@context': 'https://schema.org',
            '@type': 'Article',
            'headline': article.title,
            'description': article.excerpt,
            'datePublished': article.published_at.isoformat() if article.published_at else None,
            'dateModified': article.updated_at.isoformat(),
            'author': {
                '@type': 'Person',
                'name': article.author.get_full_name() or article.author.username,
            },
            'wordCount': article.word_count,
        }
```

**Why**: Automatically generates SEO assets. No manual maintenance needed.

---

## Environment Variables

### Required Variables (.env.example)

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=chronicle
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# CORS (comma-separated)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# File Storage
USE_S3=False
# If USE_S3=True:
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=chronicle-media
AWS_S3_REGION_NAME=us-east-1

# Email
RESEND_API_KEY=re_your_key_here
FROM_EMAIL=you@yoursite.com

# Frontend URL (for email links)
SITE_URL=http://localhost:3000
```

---

## Setup & Installation

### 1. Create Project

```bash
# Create directory
mkdir backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Django
pip install Django==5.0.3

# Create project
django-admin startproject config .

# Create apps
python manage.py startapp apps/users
python manage.py startapp apps/articles
python manage.py startapp apps/media
python manage.py startapp apps/newsletter
python manage.py startapp apps/analytics
python manage.py startapp apps/seo
```

### 2. Install Dependencies

```bash
# Install all packages
pip install -r requirements/development.txt
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb chronicle

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

**Backend runs at**: `http://localhost:8000`

---

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=apps

# Specific app
pytest apps/articles/tests/

# Verbose
pytest -v
```

### Example Test (apps/articles/tests/test_api.py)

```python
import pytest
from rest_framework.test import APIClient
from apps.articles.models import Article, Topic
from apps.users.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
def test_list_articles(api_client):
    response = api_client.get('/api/articles/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_create_article_requires_auth(api_client):
    response = api_client.post('/api/articles/', {
        'title': 'Test Article',
        'content': 'Content here'
    })
    assert response.status_code == 401

@pytest.mark.django_db
def test_create_article_authenticated(authenticated_client):
    response = authenticated_client.post('/api/articles/', {
        'title': 'Test Article',
        'content': 'Content here'
    })
    assert response.status_code == 201
    assert response.data['slug'] == 'test-article'
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] S3 bucket configured (production)
- [ ] Resend account setup
- [ ] Domain configured

### Production Settings

```python
# config/settings.py (production overrides)

DEBUG = False
ALLOWED_HOSTS = ['api.yoursite.com']

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# CORS
CORS_ALLOWED_ORIGINS = ['https://yoursite.com']