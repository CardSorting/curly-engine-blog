from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TextAnalysisViewSet,
    WritingSuggestionViewSet,
    real_time_check,
    health_check
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'text-analysis', TextAnalysisViewSet, basename='text-analysis')
router.register(r'suggestions', WritingSuggestionViewSet, basename='suggestions')

# URL patterns
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Additional endpoints
    path('health/', health_check, name='content-analysis-health'),
    path('realtime-check/', real_time_check, name='realtime-check'),
]
