from rest_framework import serializers
from django.utils.text import slugify
from .models import Article, Topic, Page


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for article topics/categories"""
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'slug', 'description', 'color',
            'created_at', 'article_count'
        ]
        read_only_fields = ['id', 'created_at']

    def get_article_count(self, obj):
        return obj.articles.filter(status='published').count()

    def create(self, validated_data):
        # Set account from request tenant if available
        if hasattr(self.context['request'], 'tenant') and self.context['request'].tenant:
            validated_data['account'] = self.context['request'].tenant
        elif hasattr(self.context['request'].user, 'default_account') and self.context['request'].user.default_account:
            validated_data['account'] = self.context['request'].user.default_account
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("No account associated with this request.")
        
        return super().create(validated_data)


class PageSerializer(serializers.ModelSerializer):
    """Serializer for static pages"""
    content_html = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'content', 'content_html',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_content_html(self, obj):
        if obj.content:
            import markdown
            return markdown.markdown(obj.content)
        return ''

    def create(self, validated_data):
        # Set account from request tenant if available
        if hasattr(self.context['request'], 'tenant') and self.context['request'].tenant:
            validated_data['account'] = self.context['request'].tenant
        elif hasattr(self.context['request'].user, 'default_account') and self.context['request'].user.default_account:
            validated_data['account'] = self.context['request'].user.default_account
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("No account associated with this request.")
        
        return super().create(validated_data)


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for article listing (minimal data)"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    hero_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author_name',
            'topic_name', 'hero_image_url', 'status', 'published_at',
            'word_count', 'reading_time', 'view_count', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'word_count', 'reading_time', 'created_at']

    def get_hero_image_url(self, obj):
        if obj.hero_image:
            return obj.hero_image.file.url
        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for full article details"""
    author = serializers.SerializerMethodField()
    topic = TopicSerializer(read_only=True)
    hero_image_url = serializers.SerializerMethodField()
    content_html = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'content_html', 'excerpt',
            'author', 'topic', 'hero_image', 'hero_image_url', 'status',
            'published_at', 'word_count', 'reading_time', 'view_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'word_count', 'reading_time', 'view_count',
            'created_at', 'updated_at'
        ]

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'email': obj.author.email,
            'full_name': obj.author.get_full_name(),
            'bio': obj.author.bio,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }

    def get_hero_image_url(self, obj):
        if obj.hero_image:
            return obj.hero_image.file.url
        return None

    def get_content_html(self, obj):
        if obj.content:
            import markdown
            return markdown.markdown(obj.content)
        return ''


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating articles"""

    class Meta:
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'topic', 'hero_image', 'status'
        ]

    def create(self, validated_data):
        # Set author from request
        validated_data['author'] = self.context['request'].user
        
        # Set account from request tenant if available
        if hasattr(self.context['request'], 'tenant') and self.context['request'].tenant:
            validated_data['account'] = self.context['request'].tenant
        elif hasattr(self.context['request'].user, 'default_account') and self.context['request'].user.default_account:
            validated_data['account'] = self.context['request'].user.default_account
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("No account associated with this request.")
        
        return super().create(validated_data)


class ArticleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating articles"""

    class Meta:
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'topic', 'hero_image', 'status'
        ]

    def validate_status(self, value):
        """Only allow status changes to 'published' if publishing for the first time"""
        if value == 'published' and self.instance.status == 'draft':
            # Additional validation can be added here if needed
            pass
        elif value == 'draft' and self.instance.status == 'published':
            # Allow changing back to draft
            pass
        return value
