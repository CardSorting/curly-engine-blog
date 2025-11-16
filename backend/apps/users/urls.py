from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/token/', views.token_obtain_pair, name='token_obtain_pair'),
    path('auth/token/refresh/', views.token_refresh, name='token_refresh'),
    path('auth/me/', views.get_current_user, name='current_user'),

    # Registration and profile
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]
