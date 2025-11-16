from django.urls import path
from . import views

app_name = 'seo'

urlpatterns = [
    # Sitemap endpoints
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('sitemap-index.xml', views.sitemap_index, name='sitemap_index'),
    
    # Robots.txt
    path('robots.txt', views.robots_txt, name='robots_txt'),
    
    # RSS feeds
    path('feed/articles/', views.rss_feed, kwargs={'feed_type': 'articles'}, name='rss_articles'),
    path('feed/topics/', views.rss_feed, kwargs={'feed_type': 'topics'}, name='rss_topics'),
    
    # SEO meta tags and structured data
    path('api/seo/meta-tags/', views.seo_meta_tags, name='seo_meta_tags'),
    path('api/seo/schema/', views.seo_schema_ld, name='seo_schema_ld'),
    
    # Redirect tracking
    path('api/seo/redirect/', views.track_redirect, name='track_redirect'),
]
