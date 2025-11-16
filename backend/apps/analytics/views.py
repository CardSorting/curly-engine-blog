from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Avg, Q, F, Sum
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import json

from .models import PageView, DailyAnalytics, ArticleAnalytics

User = get_user_model()


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST'])
@permission_classes([AllowAny])
def track_page_view(request):
    """Track a page view"""
    try:
        data = json.loads(request.body) if request.body else {}
        
        # Extract tracking data
        content_type = data.get('content_type', 'other')
        object_id = data.get('object_id')
        url = data.get('url', request.path)
        session_id = data.get('session_id', '')
        referrer = data.get('referrer', '')
        time_on_page = data.get('time_on_page')
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Create page view record
        page_view = PageView.objects.create(
            content_type=content_type,
            object_id=object_id,
            url=url,
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=session_id,
            referrer=referrer,
            time_on_page=time_on_page,
            is_bounce=data.get('is_bounce', False)
        )
        
        # Update daily analytics asynchronously (simplified for now)
        try:
            update_daily_analytics(content_type, object_id, timezone.now().date())
        except Exception as e:
            print(f"Error updating daily analytics: {e}")
        
        # Update article analytics if applicable
        if content_type == 'article' and object_id:
            try:
                update_article_analytics(object_id)
            except Exception as e:
                print(f"Error updating article analytics: {e}")
        
        return Response({'status': 'tracked', 'id': str(page_view.id)}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    """Get dashboard analytics overview"""
    try:
        # Date ranges
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        last_90_days = today - timedelta(days=90)
        
        # Overall stats
        total_views = PageView.objects.count()
        total_unique_views = PageView.objects.values('session_id').distinct().count()
        
        # Recent period stats
        views_last_7_days = PageView.objects.filter(timestamp__date__gte=last_7_days).count()
        views_last_30_days = PageView.objects.filter(timestamp__date__gte=last_30_days).count()
        views_last_90_days = PageView.objects.filter(timestamp__date__gte=last_90_days).count()
        
        # Content type breakdown
        content_stats = PageView.objects.values('content_type').annotate(
            views=Count('id'),
            unique_views=Count('session_id', distinct=True)
        ).order_by('-views')
        
        # Top articles
        top_articles = PageView.objects.filter(
            content_type='article'
        ).values('object_id').annotate(
            views=Count('id'),
            unique_views=Count('session_id', distinct=True)
        ).order_by('-views')[:10]
        
        # Traffic sources
        traffic_sources = PageView.objects.exclude(referrer='').values('referrer').annotate(
            views=Count('id')
        ).order_by('-views')[:10]
        
        # Daily trend for last 30 days
        daily_trend = []
        for i in range(30):
            date = today - timedelta(days=i)
            views = PageView.objects.filter(timestamp__date=date).count()
            daily_trend.append({
                'date': date.isoformat(),
                'views': views
            })
        
        data = {
            'overview': {
                'total_views': total_views,
                'total_unique_views': total_unique_views,
                'views_last_7_days': views_last_7_days,
                'views_last_30_days': views_last_30_days,
                'views_last_90_days': views_last_90_days,
            },
            'content_breakdown': list(content_stats),
            'top_articles': list(top_articles),
            'traffic_sources': list(traffic_sources),
            'daily_trend': daily_trend,
        }
        
        return Response(data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def article_analytics(request, article_id):
    """Get detailed analytics for a specific article"""
    try:
        # Get article analytics record
        try:
            analytics = ArticleAnalytics.objects.get(article_id=article_id)
        except ArticleAnalytics.DoesNotExist:
            return Response({'error': 'Article analytics not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get daily views for last 30 days
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        
        daily_views = PageView.objects.filter(
            content_type='article',
            object_id=article_id,
            timestamp__date__gte=last_30_days
        ).extra({
            'date': "date(timestamp)"
        }).values('date').annotate(
            views=Count('id'),
            unique_views=Count('session_id', distinct=True)
        ).order_by('date')
        
        # Traffic sources for this article
        traffic_sources = PageView.objects.filter(
            content_type='article',
            object_id=article_id
        ).exclude(referrer='').values('referrer').annotate(
            views=Count('id')
        ).order_by('-views')[:10]
        
        data = {
            'analytics': {
                'total_views': analytics.total_views,
                'unique_views': analytics.unique_views,
                'avg_reading_time': analytics.avg_reading_time,
                'completion_rate': analytics.completion_rate,
                'shares_count': analytics.shares_count,
                'likes_count': analytics.likes_count,
                'comments_count': analytics.comments_count,
                'search_views': analytics.search_views,
                'direct_views': analytics.direct_views,
                'referral_views': analytics.referral_views,
                'views_last_7_days': analytics.views_last_7_days,
                'views_last_30_days': analytics.views_last_30_days,
                'views_last_90_days': analytics.views_last_90_days,
            },
            'daily_views': list(daily_views),
            'traffic_sources': list(traffic_sources),
        }
        
        return Response(data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Helper functions (would typically be in a separate tasks.py file for Celery)
def update_daily_analytics(content_type, object_id, date):
    """Update daily analytics for a content item"""
    try:
        daily, created = DailyAnalytics.objects.get_or_create(
            content_type=content_type,
            object_id=object_id,
            date=date,
            defaults={
                'total_views': 0,
                'unique_views': 0,
                'avg_time_on_page': 0.0,
                'bounce_rate': 0.0,
            }
        )
        
        # Get all page views for this day
        views = PageView.objects.filter(
            content_type=content_type,
            object_id=object_id,
            timestamp__date=date
        )
        
        # Update metrics
        daily.total_views = views.count()
        daily.unique_views = views.values('session_id').distinct().count()
        
        # Calculate average time on page
        times = views.exclude(time_on_page__isnull=True).values_list('time_on_page', flat=True)
        if times:
            daily.avg_time_on_page = sum(times) / len(times)
        
        # Calculate bounce rate
        bounces = views.filter(is_bounce=True).count()
        if daily.total_views > 0:
            daily.bounce_rate = (bounces / daily.total_views) * 100
        
        daily.save()
        
    except Exception as e:
        print(f"Error updating daily analytics: {e}")


def update_article_analytics(article_id):
    """Update article analytics"""
    try:
        from apps.articles.models import Article
        
        # Get or create article analytics
        article = Article.objects.get(id=article_id)
        analytics, created = ArticleAnalytics.objects.get_or_create(
            article=article,
            defaults={
                'total_views': 0,
                'unique_views': 0,
                'avg_reading_time': 0.0,
                'completion_rate': 0.0,
            }
        )
        
        today = timezone.now().date()
        
        # Overall stats
        all_views = PageView.objects.filter(
            content_type='article',
            object_id=article_id
        )
        
        analytics.total_views = all_views.count()
        analytics.unique_views = all_views.values('session_id').distinct().count()
        
        # Time periods
        last_7 = today - timedelta(days=7)
        last_30 = today - timedelta(days=30)
        last_90 = today - timedelta(days=90)
        
        analytics.views_last_7_days = all_views.filter(timestamp__date__gte=last_7).count()
        analytics.views_last_30_days = all_views.filter(timestamp__date__gte=last_30).count()
        analytics.views_last_90_days = all_views.filter(timestamp__date__gte=last_90).count()
        
        # Traffic source breakdown
        analytics.search_views = all_views.filter(
            referrer__icontains='google'
        ).count() + all_views.filter(
            referrer__icontains='bing'
        ).count()
        
        analytics.direct_views = all_views.filter(referrer='').count()
        analytics.referral_views = all_views.exclude(referrer='').exclude(
            referrer__icontains='google'
        ).exclude(
            referrer__icontains='bing'
        ).count()
        
        analytics.save()
        
    except Exception as e:
        print(f"Error updating article analytics: {e}")
