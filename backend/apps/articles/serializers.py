from rest_framework import serializers
from django.utils.text import slugify
from .models import (
    Topic, Article, Page, Series, Comment, ArticleReaction,
    ArticleAnnotation, BreakingNews, SearchQuery
)


class TopicSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'slug')

    def get_article_count(self, obj):
        return obj.articles.filter(status='published').count()

    def create(self, validated_data):
        # Set account from request context
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'account'):
            validated_data['account'] = request.user.account

        return super().create(validated_data)


class SeriesSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Series
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

    def get_article_count(self, obj):
        return obj.articles.filter(status='published').count()

    def create(self, validated_data):
        # Set account from request context
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'account'):
            validated_data['account'] = request.user.account

        return super().create(validated_data)


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    series_name = serializers.CharField(source='series.title', read_only=True)
    hero_image_url = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    reaction_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'status', 'published_at',
            'is_premium', 'premium_excerpt', 'word_count', 'reading_time',
            'view_count', 'engagement_score', 'author_name', 'topic_name',
            'series_name', 'series_order', 'hero_image_url', 'comment_count',
            'reaction_count', 'created_at'
        ]

    def get_hero_image_url(self, obj):
        if obj.hero_image:
            return obj.hero_image.file.url if hasattr(obj.hero_image, 'file') else None
        return None

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_reaction_count(self, obj):
        return obj.reactions.count()


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    topic = TopicSerializer(read_only=True)
    series = SeriesSerializer(read_only=True)
    related_articles = ArticleListSerializer(many=True, read_only=True)
    media_gallery = serializers.SerializerMethodField()
    hero_image_url = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'word_count', 'reading_time',
            'engagement_score', 'author', 'hero_image_url'
        )

    def get_author(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.author).data

    def get_hero_image_url(self, obj):
        if obj.hero_image:
            return obj.hero_image.file.url if hasattr(obj.hero_image, 'file') else None
        return None

    def get_media_gallery(self, obj):
        # Return media URLs
        media_urls = []
        for media in obj.media_gallery.all():
            if hasattr(media, 'file'):
                media_urls.append({
                    'id': media.id,
                    'url': media.file.url,
                    'type': media.media_type if hasattr(media, 'media_type') else 'image',
                    'filename': media.filename if hasattr(media, 'filename') else ''
                })
        return media_urls

    def get_comments(self, obj):
        # Return approved comments with replies
        comments = obj.comments.filter(is_approved=True).order_by('created_at')
        return CommentSerializer(comments, many=True).data

    def get_reactions(self, obj):
        # Aggregate reaction counts
        reaction_counts = {}
        for reaction in obj.reactions.all():
            reaction_type = reaction.reaction_type
            if reaction_type in reaction_counts:
                reaction_counts[reaction_type] += 1
            else:
                reaction_counts[reaction_type] = 1

        # Include user's reaction if authenticated
        request = self.context.get('request')
        user_reaction = None
        if request and request.user.is_authenticated:
            user_reaction_obj = obj.reactions.filter(user=request.user).first()
            if user_reaction_obj:
                user_reaction = user_reaction_obj.reaction_type

        return {
            'counts': reaction_counts,
            'user_reaction': user_reaction,
            'total': sum(reaction_counts.values())
        }


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'topic', 'series', 'series_order',
            'hero_image', 'is_premium', 'premium_excerpt', 'follow_up_links',
            'media_gallery', 'video_embed_url', 'related_articles'
        ]

    def create(self, validated_data):
        # Set account and author from request context
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['account'] = request.user.account
            validated_data['author'] = request.user

        return super().create(validated_data)


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'topic', 'series', 'series_order',
            'status', 'hero_image', 'is_premium', 'premium_excerpt',
            'follow_up_links', 'media_gallery', 'video_embed_url', 'related_articles'
        ]

    def validate_status(self, value):
        request = self.context.get('request')
        if request and value == 'published':
            # Check if user has permission to publish
            if not request.user.can_publish_articles:
                raise serializers.ValidationError("You don't have permission to publish articles.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    depth = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author_name', 'author_avatar', 'replies',
            'depth', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_author_avatar(self, obj):
        # Return user avatar if available
        if hasattr(obj.author, 'avatar') and obj.author.avatar:
            return obj.author.avatar.url
        return None

    def get_replies(self, obj):
        # Get nested replies (limit depth to avoid infinite recursion)
        if hasattr(obj, '_depth') and obj._depth >= 3:  # Max depth of 3
            return []
        replies = obj.replies.filter(is_approved=True).order_by('created_at')
        serializer = CommentSerializer(replies, many=True, context=self.context)
        return serializer.data

    def get_depth(self, obj):
        # Calculate reply depth
        depth = 0
        parent = obj.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

    def create(self, validated_data):
        # Set article from URL and author from request
        request = self.context.get('request')
        article_slug = self.context.get('article_slug')
        parent_id = self.context.get('parent_id')

        if article_slug:
            try:
                from .models import Article
                validated_data['article'] = Article.objects.get(
                    slug=article_slug,
                    account=request.user.account
                )
            except Article.DoesNotExist:
                raise serializers.ValidationError("Article not found.")

        if request and request.user.is_authenticated:
            validated_data['author'] = request.user

        if parent_id:
            try:
                validated_data['parent'] = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                raise serializers.ValidationError("Parent comment not found.")

        return super().create(validated_data)


class ArticleReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleReaction
        fields = ['id', 'reaction_type', 'created_at']
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        # Set article and user from context
        request = self.context.get('request')
        article_slug = self.context.get('article_slug')

        if article_slug:
            try:
                from .models import Article
                validated_data['article'] = Article.objects.get(
                    slug=article_slug,
                    account=request.user.account
                )
            except Article.DoesNotExist:
                raise serializers.ValidationError("Article not found.")

        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        # Ensure user hasn't already reacted (unique constraint will handle this)
        return super().create(validated_data)


class ArticleAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleAnnotation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Set article and user from context
        request = self.context.get('request')
        article_slug = self.context.get('article_slug')

        if article_slug:
            try:
                from .models import Article
                validated_data['article'] = Article.objects.get(
                    slug=article_slug,
                    account=request.user.account
                )
            except Article.DoesNotExist:
                raise serializers.ValidationError("Article not found.")

        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        return super().create(validated_data)


class BreakingNewsSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = BreakingNews
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'view_count', 'click_count')

    def create(self, validated_data):
        # Set account and created_by from request context
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['account'] = request.user.account
            validated_data['created_by'] = request.user

        return super().create(validated_data)


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'result_count')

    def create(self, validated_data):
        # Set account and user from request context
        request = self.context.get('request')
        if request:
            if hasattr(request.user, 'account'):
                validated_data['account'] = request.user.account
            if request.user.is_authenticated:
                validated_data['user'] = request.user

        return super().create(validated_data)


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Set account from request context
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'account'):
            validated_data['account'] = request.user.account

        return super().create(validated_data)
