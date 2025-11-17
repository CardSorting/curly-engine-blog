from rest_framework import serializers
from .models import TextAnalysis, WritingSuggestion


class TextAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for text analysis requests and responses"""

    class Meta:
        model = TextAnalysis
        fields = [
            'id', 'text_content', 'analysis_type', 'language',
            'results', 'created_at', 'is_cached'
        ]
        read_only_fields = ['id', 'results', 'created_at', 'is_cached']

    def create(self, validated_data):
        # Get or create cached analysis
        existing = TextAnalysis.get_cached_analysis(
            text_content=validated_data['text_content'],
            analysis_type=validated_data['analysis_type'],
            account=self.context.get('request').account if hasattr(self.context.get('request'), 'account') else None,
            language=validated_data.get('language', 'en')
        )

        if existing and existing.results:
            # Return cached results
            existing.is_cached = True
            return existing

        # Create new analysis
        analysis = TextAnalysis.objects.create(**validated_data)
        analysis.perform_analysis()
        return analysis


class WritingSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for writing suggestions"""

    class Meta:
        model = WritingSuggestion
        fields = [
            'id', 'suggestion_type', 'title', 'description',
            'original_text', 'suggested_text', 'start_position', 'end_position',
            'confidence_score', 'is_accepted', 'is_dismissed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TextAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for text analysis API requests"""
    text_content = serializers.CharField(required=True, max_length=100000)
    analysis_type = serializers.ChoiceField(
        choices=TextAnalysis.ANALYSIS_TYPES,
        default='comprehensive'
    )
    language = serializers.CharField(max_length=10, default='en')

    def validate_text_content(self, value):
        """Validate that text content is not empty and not too short"""
        if not value.strip():
            raise serializers.ValidationError("Text content cannot be empty")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Text content must be at least 10 characters long")
        return value


class BulkTextAnalysisSerializer(serializers.Serializer):
    """Serializer for bulk text analysis requests"""
    analyses = TextAnalysisRequestSerializer(many=True)

    def validate_analyses(self, value):
        """Validate that we don't exceed bulk limits"""
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 analyses per bulk request")
        return value


class AnalysisResultSerializer(serializers.Serializer):
    """Serializer for formatted analysis results"""

    # Core metrics
    word_count = serializers.IntegerField()
    sentence_count = serializers.IntegerField()
    character_count = serializers.IntegerField()

    # Readability metrics
    flesch_reading_ease = serializers.FloatField()
    flesch_kincaid_grade = serializers.FloatField()
    readability_level = serializers.CharField()

    # Grammar analysis
    grammar_issues = serializers.IntegerField()
    grammar_score = serializers.FloatField()

    # SEO metrics
    seo_score = serializers.FloatField()
    keyword_suggestions = serializers.ListField(child=serializers.CharField())

    # Overall
    overall_score = serializers.FloatField()
    summary = serializers.ListField(child=serializers.CharField())

    # Detailed breakdowns
    detailed_grammar = serializers.DictField()
    detailed_readability = serializers.DictField()
    detailed_seo = serializers.DictField()


class SuggestionActionSerializer(serializers.Serializer):
    """Serializer for suggestion actions (accept/dismiss)"""
    action = serializers.ChoiceField(choices=['accept', 'dismiss'])

    def validate_action(self, value):
        if value not in ['accept', 'dismiss']:
            raise serializers.ValidationError("Action must be 'accept' or 'dismiss'")
        return value
