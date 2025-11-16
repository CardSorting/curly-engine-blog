from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, SubscriptionPlanViewSet
from .webhooks import stripe_webhook

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')

app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
]
