from django.urls import path
from . import views

app_name = 'media'

urlpatterns = [
    path('', views.MediaListView.as_view(), name='media-list'),
    path('upload/', views.MediaUploadView.as_view(), name='media-upload'),
    path('<uuid:id>/', views.MediaDetailView.as_view(), name='media-detail'),
    path('stats/', views.media_stats, name='media-stats'),
]
