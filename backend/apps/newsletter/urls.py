from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriberViewSet, NewsletterViewSet, SubscriberGroupViewSet,
    NewsletterSendViewSet, TrackingView
)

router = DefaultRouter()
router.register(r'subscribers', SubscriberViewSet)
router.register(r'newsletters', NewsletterViewSet)
router.register(r'groups', SubscriberGroupViewSet)
router.register(r'sends', NewsletterSendViewSet)

app_name = 'newsletter'

urlpatterns = [
    path('', include(router.urls)),
    path('tracking/<str:tracking_type>/<uuid:token>/', TrackingView.as_view(), name='tracking'),
]
