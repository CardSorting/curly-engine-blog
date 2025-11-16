"""
URL configuration for Chronicle Django Backend.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/', include('apps.articles.urls')),
    path('api/media/', include('apps.media.urls')),
    path('api/newsletter/', include('apps.newsletter.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/seo/', include('apps.seo.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
