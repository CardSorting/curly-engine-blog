from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]
