"""
URL configuration for Chronicle Django Backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('apps.users.urls')),  # This will handle auth endpoints
    path('api/media/', include('apps.media.urls')),
    path('api/', include('apps.articles.urls')),
    path('api/newsletter/', include('apps.newsletter.urls')),

    # Add other apps as they get implemented
    path('api/analytics/', include('apps.analytics.urls')),
    # SEO endpoints (no authentication required)
    path('', include('apps.seo.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
