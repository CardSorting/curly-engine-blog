from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Articles endpoints
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('detail/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('detail/<slug:slug>/publish/', views.publish_article, name='article-publish'),

    # Topics endpoints
    path('topics/', views.TopicListView.as_view(), name='topic-list'),
    path('topics/<slug:slug>/', views.TopicDetailView.as_view(), name='topic-detail'),
    path('topics/<slug:slug>/articles/', views.TopicArticlesView.as_view(), name='topic-articles'),

    # Pages endpoints
    path('pages/', views.PageListView.as_view(), name='page-list'),
    path('pages/<slug:slug>/', views.PageDetailView.as_view(), name='page-detail'),
]
