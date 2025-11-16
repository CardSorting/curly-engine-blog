from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Analytics tracking endpoint
    path('track/', views.track_page_view, name='track_page_view'),
    
    # Analytics dashboard and reporting
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('article/<uuid:article_id>/', views.article_analytics, name='article_analytics'),
]
