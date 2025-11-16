from rest_framework import serializers
from .models import Subscriber, Newsletter, SubscriberGroup, NewsletterSend, NewsletterTemplate


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = [
            'id', 'email', 'first_name', 'last_name', 'is_active', 'is_confirmed',
            'created_at', 'confirmed_at', 'unsubscribed_at', 'user'
        ]
        read_only_fields = [
            'id', 'created_at', 'confirmed_at', 'unsubscribed_at', 'confirmation_token',
            'unsubscribe_token'
        ]


class NewsletterSubscriptionSerializer(serializers.Serializer):
    """Serializer for newsletter subscription endpoint"""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)


class SubscriberGroupSerializer(serializers.ModelSerializer):
    subscriber_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriberGroup
        fields = ['id', 'name', 'description', 'created_at', 'subscriber_count']
        read_only_fields = ['id', 'created_at']
    
    def get_subscriber_count(self, obj):
        # This would require a related_name on the Subscriber model
        # For now, return 0 as placeholder
        return 0


class NewsletterSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    recipient_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'subject', 'preview_text', 'content_html', 'content_text',
            'status', 'scheduled_at', 'sent_at', 'target_all_subscribers', 'target_groups',
            'total_sent', 'total_opened', 'total_clicked', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'recipient_count'
        ]
        read_only_fields = [
            'id', 'total_sent', 'total_opened', 'total_clicked', 'created_by',
            'created_at', 'updated_at', 'sent_at'
        ]
    
    def get_recipient_count(self, obj):
        """Get count of recipients for this newsletter"""
        if obj.target_all_subscribers:
            return Subscriber.objects.filter(is_active=True, is_confirmed=True).count()
        else:
            return Subscriber.objects.filter(
                is_active=True, 
                is_confirmed=True,
                groups__in=obj.target_groups.all()
            ).distinct().count()


class NewsletterSendSerializer(serializers.ModelSerializer):
    newsletter_title = serializers.CharField(source='newsletter.title', read_only=True)
    subscriber_email = serializers.CharField(source='subscriber.email', read_only=True)
    
    class Meta:
        model = NewsletterSend
        fields = [
            'id', 'newsletter', 'newsletter_title', 'subscriber', 'subscriber_email',
            'status', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'open_token', 'click_token', 'created_at'
        ]
        read_only_fields = [
            'id', 'open_token', 'click_token', 'created_at', 'sent_at',
            'delivered_at', 'opened_at', 'clicked_at'
        ]


class NewsletterTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterTemplate
        fields = [
            'id', 'name', 'description', 'subject_template', 'html_template',
            'text_template', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NewsletterCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating newsletters with simplified fields"""
    class Meta:
        model = Newsletter
        fields = [
            'title', 'subject', 'preview_text', 'content_html', 'content_text',
            'target_all_subscribers', 'target_groups'
        ]
    
    def create(self, validated_data):
        target_groups = validated_data.pop('target_groups', [])
        newsletter = Newsletter.objects.create(**validated_data)
        if target_groups:
            newsletter.target_groups.set(target_groups)
        return newsletter


class NewsletterUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating newsletters"""
    class Meta:
        model = Newsletter
        fields = [
            'title', 'subject', 'preview_text', 'content_html', 'content_text',
            'status', 'scheduled_at', 'target_all_subscribers', 'target_groups'
        ]
    
    def validate_status(self, value):
        """Prevent changing status from 'sent' back to 'draft'"""
        if self.instance and self.instance.status == 'sent' and value != 'sent':
            raise serializers.ValidationError(
                "Cannot change status of sent newsletter"
            )
        return value
