from rest_framework import generics, permissions, status, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Article, Topic, Page, Series, CollaborativeSession, SessionParticipant
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    ArticleCreateSerializer, ArticleUpdateSerializer,
    TopicSerializer, PageSerializer, SeriesSerializer
)
from apps.accounts.permissions import IsAccountMember, IsArticleAuthorOrEditor, CanPublishArticles


class ArticleListView(generics.ListCreateAPIView):
    """List articles and create new articles"""
    serializer_class = ArticleListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'author']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'created_at', 'view_count']
    ordering = ['-published_at']

    def get_queryset(self):
        # For public requests, only show published articles
        if not self.request.user or not self.request.user.is_authenticated:
            return Article.objects.filter(status='published')
        
        # For authenticated users, filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Article.objects.filter(account=self.request.tenant)
        else:
            queryset = Article.objects.all()
        
        # Non-staff users can only see their own drafts
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(status='published') | models.Q(author=self.request.user)
            )
        return queryset

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAccountMember()]
        return [permissions.AllowAny()]


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an article"""
    lookup_field = 'slug'
    permission_classes = [IsAccountMember]

    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Article.objects.filter(account=self.request.tenant)
        else:
            queryset = Article.objects.all()
        
        # For non-authenticated users, only show published articles
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        return queryset

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ArticleUpdateSerializer
        return ArticleDetailSerializer

    def get_permissions(self):
        """Allow authenticated users to view drafts, others only published"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAccountMember, IsArticleAuthorOrEditor()]
        return [IsAccountMember]

    def check_object_permissions(self, request, obj):
        """Authors can edit their own articles, others can't modify"""
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Check if user can edit this article (author or editor/admin)
            if not (hasattr(request, 'account_user') and request.account_user):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You don't have permission to edit articles in this account.")
            
            # Allow if user can edit all articles or is the author
            if not (request.account_user.can_edit_all_articles or obj.author == request.user):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only edit your own articles.")
        super().check_object_permissions(request, obj)

    def retrieve(self, request, *args, **kwargs):
        """Override to increment view count"""
        instance = self.get_object()

        # Increment view count for published articles
        if instance.status == 'published':
            instance.view_count += 1
            instance.save(update_fields=['view_count'])

        # Check if user has permission to view draft
        if instance.status == 'draft' and instance.author != request.user:
            if not request.user.is_staff:
                from rest_framework.exceptions import NotFound
                raise NotFound()

        return super().retrieve(request, *args, **kwargs)


@api_view(['PATCH'])
@permission_classes([IsAccountMember, CanPublishArticles])
def publish_article(request, slug):
    """Publish a draft article"""
    article = get_object_or_404(Article, slug=slug)

    # Check if user can publish this article
    if not (hasattr(request, 'account_user') and request.account_user):
        return Response(
            {'error': 'You don\'t have permission to publish articles in this account.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if not request.account_user.can_publish_articles:
        return Response(
            {'error': 'You don\'t have permission to publish articles.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if article.status == 'published':
        return Response(
            {'error': 'Article is already published.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    article.status = 'published'
    from django.utils import timezone
    article.published_at = timezone.now()
    article.save()

    serializer = ArticleDetailSerializer(article)
    return Response(serializer.data)


class TopicListView(generics.ListCreateAPIView):
    """List topics and create new topics"""
    def get_queryset(self):
        # For public requests, show all topics
        if not self.request.user or not self.request.user.is_authenticated:
            return Topic.objects.all()
        
        # For authenticated users, filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Topic.objects.filter(account=self.request.tenant)
        else:
            queryset = Topic.objects.all()
        return queryset
    
    serializer_class = TopicSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAccountMember()]
        return [permissions.AllowAny()]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']


class TopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a topic"""
    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Topic.objects.filter(account=self.request.tenant)
        else:
            queryset = Topic.objects.all()
        return queryset
    serializer_class = TopicSerializer
    permission_classes = [IsAccountMember]
    lookup_field = 'slug'


class TopicArticlesView(generics.ListAPIView):
    """List articles for a specific topic"""
    serializer_class = ArticleListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['published_at', 'created_at', 'view_count']
    ordering = ['-published_at']

    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            topic = get_object_or_404(Topic, slug=self.kwargs['slug'], account=self.request.tenant)
        else:
            topic = get_object_or_404(Topic, slug=self.kwargs['slug'])
        
        queryset = topic.articles.all()
        # For non-authenticated users, only show published articles
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        return queryset


class PageListView(generics.ListCreateAPIView):
    """List pages and create new pages"""
    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Page.objects.filter(account=self.request.tenant)
        else:
            queryset = Page.objects.all()
        return queryset
    serializer_class = PageSerializer
    permission_classes = [IsAccountMember]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']


class PageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a page"""
    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Page.objects.filter(account=self.request.tenant)
        else:
            queryset = Page.objects.all()
        return queryset
    serializer_class = PageSerializer
    permission_classes = [IsAccountMember]
    lookup_field = 'slug'


class SeriesListView(generics.ListCreateAPIView):
    """List series and create new series"""
    serializer_class = SeriesSerializer
    permission_classes = [IsAccountMember]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Series.objects.filter(account=self.request.tenant)
        else:
            queryset = Series.objects.all()
        return queryset


class SeriesDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a series"""
    serializer_class = SeriesSerializer
    permission_classes = [IsAccountMember]

    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Series.objects.filter(account=self.request.tenant)
        else:
            queryset = Series.objects.all()
        return queryset


class SeriesArticlesView(generics.ListAPIView):
    """List articles in a specific series (ordered by series_order)"""
    serializer_class = ArticleListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering = ['series_order', '-published_at']

    def get_queryset(self):
        # Filter by tenant and get series
        if hasattr(self.request, 'tenant') and self.request.tenant:
            series = get_object_or_404(Series, id=self.kwargs['pk'], account=self.request.tenant)
        else:
            series = get_object_or_404(Series, id=self.kwargs['pk'])

        queryset = series.articles.all()

        # For non-authenticated users, only show published articles
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')

        return queryset.order_by('series_order', '-published_at')
