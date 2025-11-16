from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserRegisterView.as_view(), name='register'),
    path('verify-email/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
]
