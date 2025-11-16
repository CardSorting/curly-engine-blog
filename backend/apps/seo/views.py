from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.core.paginator import Paginator
from django.conf import settings
import json
from datetime import datetime, timedelta

from .models import SEOSettings, SitemapEntry, Redirect, MetaTag
from apps.articles.models import Article, Topic, Page


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["GET"])
@api_view(['GET'])
@permission_classes([AllowAny])
def sitemap_xml(request):
    """Generate XML sitemap for search engines"""
    site = get_current_site(request)
    base_url = f"https://{site.domain}"
    
    # Get all sitemap entries
    entries = []
    
    # Add homepage
    entries.append({
        'url': base_url,
        'lastmod': timezone.now().isoformat(),
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    # Add articles
    articles = Article.objects.filter(status='published')
    for article in articles:
        entries.append({
            'url': f"{base_url}/articles/{article.slug}/",
            'lastmod': article.updated_at.isoformat() if article.updated_at else article.published_at.isoformat(),
            'changefreq': 'weekly',
            'priority': '0.8'
        })
    
    # Add topics
    topics = Topic.objects.all()
    for topic in topics:
        entries.append({
            'url': f"{base_url}/topics/{topic.slug}/",
            'lastmod': topic.created_at.isoformat(),
            'changefreq': 'monthly',
            'priority': '0.6'
        })
    
    # Add pages
    pages = Page.objects.all()
    for page in pages:
        entries.append({
            'url': f"{base_url}/{page.slug}/",
            'lastmod': page.updated_at.isoformat() if page.updated_at else page.created_at.isoformat(),
            'changefreq': 'monthly',
            'priority': '0.7'
        })
    
    # Add custom sitemap entries
    custom_entries = SitemapEntry.objects.filter(content_type='custom')
    for entry in custom_entries:
        entries.append({
            'url': f"{base_url}{entry.url}",
            'lastmod': entry.last_modified.isoformat(),
            'changefreq': entry.changefreq,
            'priority': str(entry.priority)
        })
    
    # Generate XML
    template = loader.get_template('seo/sitemap.xml')
    context = {
        'entries': entries,
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
    }
    
    response = HttpResponse(template.render(context, request), content_type='application/xml')
    response['Content-Type'] = 'application/xml; charset=utf-8'
    return response


@require_http_methods(["GET"])
@api_view(['GET'])
@permission_classes([AllowAny])
def sitemap_index(request):
    """Generate sitemap index for multiple sitemaps"""
    site = get_current_site(request)
    base_url = f"https://{site.domain}"
    
    sitemaps = [
        {
            'url': f"{base_url}/sitemap.xml",
            'lastmod': timezone.now().isoformat()
        }
    ]
    
    template = loader.get_template('seo/sitemap_index.xml')
    context = {
        'sitemaps': sitemaps,
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
    }
    
    response = HttpResponse(template.render(context, request), content_type='application/xml')
    response['Content-Type'] = 'application/xml; charset=utf-8'
    return response


@require_http_methods(["GET"])
@api_view(['GET'])
@permission_classes([AllowAny])
def robots_txt(request):
    """Generate robots.txt file"""
    site = get_current_site(request)
    base_url = f"https://{site.domain}"
    
    # Get SEO settings for custom rules
    try:
        seo_settings = SEOSettings.objects.get(site=site)
        custom_rules = seo_settings.custom_robots if hasattr(seo_settings, 'custom_robots') else ''
    except SEOSettings.DoesNotExist:
        custom_rules = ''
    
    content = f"""User-agent: *
Allow: /

# Sitemaps
Sitemap: {base_url}/sitemap.xml
Sitemap: {base_url}/sitemap-index.xml

{custom_rules}
"""
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Type'] = 'text/plain; charset=utf-8'
    return response


@require_http_methods(["GET"])
@api_view(['GET'])
@permission_classes([AllowAny])
def rss_feed(request, feed_type='articles'):
    """Generate RSS feed for articles or topics"""
    site = get_current_site(request)
    base_url = f"https://{site.domain}"
    
    # Get SEO settings
    try:
        seo_settings = SEOSettings.objects.get(site=site)
        feed_title = seo_settings.meta_title or f"{site.name} Blog"
        feed_description = seo_settings.meta_description or f"Latest articles from {site.name}"
    except SEOSettings.DoesNotExist:
        feed_title = f"{site.name} Blog"
        feed_description = f"Latest articles from {site.name}"
    
    if feed_type == 'articles':
        items = Article.objects.filter(status='published').order_by('-published_at')[:20]
        feed_url = f"{base_url}/feed/articles/"
    elif feed_type == 'topics':
        items = Topic.objects.all().order_by('-created_at')[:20]
        feed_url = f"{base_url}/feed/topics/"
    else:
        return JsonResponse({'error': 'Invalid feed type'}, status=400)
    
    # Build feed items
    feed_items = []
    for item in items:
        if feed_type == 'articles':
            item_url = f"{base_url}/articles/{item.slug}/"
            item_title = item.title
            item_description = item.excerpt or item.content[:200] + '...'
            item_date = item.published_at
            item_author = item.author.get_full_name() or item.author.email
        else:  # topics
            item_url = f"{base_url}/topics/{item.slug}/"
            item_title = item.name
            item_description = item.description or ''
            item_date = item.created_at
            item_author = site.name
        
        feed_items.append({
            'title': item_title,
            'link': item_url,
            'description': item_description,
            'pubDate': item_date.strftime('%a, %d %b %Y %H:%M:%S %Z'),
            'guid': item_url,
            'author': item_author
        })
    
    template = loader.get_template('seo/rss.xml')
    context = {
        'title': feed_title,
        'description': feed_description,
        'link': base_url,
        'feed_url': feed_url,
        'items': feed_items,
        'build_date': timezone.now().strftime('%a, %d %b %Y %H:%M:%S %Z'),
        'language': 'en-us'
    }
    
    response = HttpResponse(template.render(context, request), content_type='application/rss+xml')
    response['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def seo_meta_tags(request):
    """Get SEO meta tags for a specific URL"""
    url = request.GET.get('url', '')
    if not url:
        return JsonResponse({'error': 'URL parameter required'}, status=400)
    
    site = get_current_site(request)
    base_url = f"https://{site.domain}"
    
    # Try to find matching meta tags
    meta_tags = None
    
    # Check for article
    if '/articles/' in url:
        slug = url.split('/articles/')[-1].strip('/')
        try:
            article = Article.objects.get(slug=slug)
            meta_tags = MetaTag.objects.filter(
                content_type='article',
                object_id=article.id,
                is_active=True
            ).first()
        except Article.DoesNotExist:
            pass
    
    # Check for topic
    elif '/topics/' in url:
        slug = url.split('/topics/')[-1].strip('/')
        try:
            topic = Topic.objects.get(slug=slug)
            meta_tags = MetaTag.objects.filter(
                content_type='topic',
                object_id=topic.id,
                is_active=True
            ).first()
        except Topic.DoesNotExist:
            pass
    
    # Check for page
    elif '/' in url and url != '/':
        slug = url.strip('/')
        try:
            page = Page.objects.get(slug=slug)
            meta_tags = MetaTag.objects.filter(
                content_type='page',
                object_id=page.id,
                is_active=True
            ).first()
        except Page.DoesNotExist:
            pass
    
    # Check for homepage
    elif url == '/' or url == '':
        meta_tags = MetaTag.objects.filter(
            content_type='home',
            is_active=True
        ).first()
    
    # Get default SEO settings
    try:
        seo_settings = SEOSettings.objects.get(site=site)
    except SEOSettings.DoesNotExist:
        seo_settings = None
    
    # Build meta tags response
    tags = {
        'title': '',
        'description': '',
        'keywords': '',
        'canonical': '',
        'og_title': '',
        'og_description': '',
        'og_image': '',
        'twitter_card': 'summary_large_image',
        'twitter_site': '',
        'twitter_creator': '',
        'robots_index': True,
        'robots_follow': True,
        'custom_meta': {}
    }
    
    # Apply specific meta tags if found
    if meta_tags:
        tags['title'] = meta_tags.meta_title or tags['title']
        tags['description'] = meta_tags.meta_description or tags['description']
        tags['keywords'] = meta_tags.meta_keywords or tags['keywords']
        tags['canonical'] = meta_tags.canonical_url or tags['canonical']
        tags['robots_index'] = meta_tags.robots_index
        tags['robots_follow'] = meta_tags.robots_follow
        tags['custom_meta'] = meta_tags.custom_meta or {}
    
    # Apply default SEO settings
    if seo_settings:
        tags['title'] = tags['title'] or seo_settings.meta_title
        tags['description'] = tags['description'] or seo_settings.meta_description
        tags['keywords'] = tags['keywords'] or seo_settings.meta_keywords
        tags['og_title'] = tags['og_title'] or seo_settings.og_title or tags['title']
        tags['og_description'] = tags['og_description'] or seo_settings.og_description or tags['description']
        tags['og_image'] = tags['og_image'] or (seo_settings.og_image.url if seo_settings.og_image else '')
        tags['twitter_card'] = seo_settings.twitter_card
        tags['twitter_site'] = seo_settings.twitter_site
        tags['twitter_creator'] = seo_settings.twitter_creator
    
    return JsonResponse(tags)


@api_view(['GET'])
@permission_classes([AllowAny])
def seo_schema_ld(request):
    """Get Schema.org JSON-LD structured data"""
    url = request.GET.get('url', '')
    if not url:
        return JsonResponse({'error': 'URL parameter required'}, status=400)
    
    site = get_current_site(request)
    base_url = f"https://{site.domain}"
    
    # Get SEO settings
    try:
        seo_settings = SEOSettings.objects.get(site=site)
    except SEOSettings.DoesNotExist:
        seo_settings = None
    
    schema = {}
    
    # Determine schema type based on URL
    if '/articles/' in url:
        slug = url.split('/articles/')[-1].strip('/')
        try:
            article = Article.objects.get(slug=slug)
            schema = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": article.title,
                "description": article.excerpt or article.content[:200] + '...',
                "author": {
                    "@type": "Person",
                    "name": article.author.get_full_name() or article.author.email
                },
                "datePublished": article.published_at.isoformat(),
                "dateModified": article.updated_at.isoformat() if article.updated_at else article.published_at.isoformat(),
                "url": f"{base_url}/articles/{article.slug}/",
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": f"{base_url}/articles/{article.slug}/"
                }
            }
            
            if article.hero_image:
                schema["image"] = article.hero_image.url
                
        except Article.DoesNotExist:
            pass
    
    elif url == '/' or url == '':
        # Homepage schema
        if seo_settings:
            schema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": seo_settings.organization_name,
                "url": seo_settings.organization_url,
                "logo": seo_settings.organization_logo.url if seo_settings.organization_logo else ""
            }
    
    return JsonResponse(schema)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_redirect(request):
    """Track redirect clicks for analytics"""
    try:
        data = json.loads(request.body) if request.body else {}
        path = data.get('path', '')
        
        if not path:
            return JsonResponse({'error': 'Path parameter required'}, status=400)
        
        # Find matching redirect
        try:
            redirect = Redirect.objects.get(old_path=path, is_active=True)
            
            # Log the redirect (you could integrate with analytics here)
            print(f"Redirect triggered: {path} → {redirect.new_path} ({redirect.status_code})")
            
            return JsonResponse({
                'status': 'found',
                'new_path': redirect.new_path,
                'status_code': redirect.status_code
            })
            
        except Redirect.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
