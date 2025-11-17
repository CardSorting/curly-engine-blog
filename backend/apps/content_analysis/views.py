from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import JsonResponse

from .models import TextAnalysis, WritingSuggestion
from .serializers import (
    TextAnalysisSerializer,
    WritingSuggestionSerializer,
    TextAnalysisRequestSerializer,
    BulkTextAnalysisSerializer,
    SuggestionActionSerializer
)


class TextAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for text analysis operations
    """
    queryset = TextAnalysis.objects.all()
    serializer_class = TextAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by account if user has account context"""
        queryset = super().get_queryset()
        if hasattr(self.request, 'account') and self.request.account:
            queryset = queryset.filter(account=self.request.account)
        return queryset

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Analyze text content and return results
        Supports caching for repeated analyses
        """
        serializer = TextAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create or get cached analysis
        analysis = TextAnalysis(
            text_content=serializer.validated_data['text_content'],
            analysis_type=serializer.validated_data['analysis_type'],
            language=serializer.validated_data.get('language', 'en')
        )

        # Set account if available
        if hasattr(request, 'account') and request.account:
            analysis.account = request.account

        # Check for cached results
        cached = TextAnalysis.get_cached_analysis(
            analysis.text_content,
            analysis.analysis_type,
            analysis.account,
            analysis.language
        )

        if cached:
            cached.is_cached = True
            serializer = self.get_serializer(cached)
            return Response(serializer.data)

        # Perform new analysis
        analysis.save()
        results = analysis.perform_analysis()

        # Cache the results
        cache_key = f"text_analysis_{analysis.text_hash}_{analysis.analysis_type}_{analysis.language}"
        cache.set(cache_key, results, 86400)  # 24 hours

        serializer = self.get_serializer(analysis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_analyze(self, request):
        """
        Perform bulk text analysis (max 10 analyses per request)
        """
        serializer = BulkTextAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        results = []
        for analysis_data in serializer.validated_data['analyses']:
            # Create temporary analysis object for processing
            analysis = TextAnalysis(
                text_content=analysis_data['text_content'],
                analysis_type=analysis_data['analysis_type'],
                language=analysis_data.get('language', 'en')
            )

            if hasattr(request, 'account') and request.account:
                analysis.account = request.account

            # Perform analysis
            analysis.save()
            analysis.perform_analysis()

            results.append(self.get_serializer(analysis).data)

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def suggestions(self, request, pk=None):
        """
        Get AI-powered writing suggestions for this analysis
        """
        analysis = self.get_object()

        # Check if analysis is comprehensive and has results
        if analysis.analysis_type != 'comprehensive' or not analysis.results:
            return Response(
                {"detail": "Suggestions are only available for comprehensive analysis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate suggestions based on analysis results
        suggestions = self._generate_suggestions(analysis)

        return Response(suggestions)

    def _generate_suggestions(self, analysis):
        """
        Generate writing suggestions based on analysis results
        """
        suggestions_data = []
        results = analysis.results

        # Grammar suggestions
        if results.get('grammar', {}).get('issues'):
            for issue in results['grammar']['issues'][:3]:  # Limit to 3 suggestions
                suggestion = {
                    'type': 'grammar',
                    'title': f"Grammar: {issue['message']}",
                    'description': f"Potential grammar issue: {issue['message']}",
                    'severity': issue.get('severity', 'minor'),
                    'position': issue.get('position', 0)
                }
                suggestions_data.append(suggestion)

        # Readability suggestions
        readability = results.get('readability', {})
        if readability.get('flesch_reading_ease', 100) < 60:
            suggestions_data.append({
                'type': 'readability',
                'title': 'Improve Readability',
                'description': f"Your text has a readability level of {readability.get('readability_level', 'Unknown')}. Consider using shorter sentences and simpler words.",
                'severity': 'medium'
            })

        if readability.get('avg_words_per_sentence', 0) > 25:
            suggestions_data.append({
                'type': 'readability',
                'title': 'Shorten Sentences',
                'description': f"Average sentence length is {readability.get('avg_words_per_sentence', 0):.1f} words. Shorter sentences are easier to read.",
                'severity': 'low'
            })

        # SEO suggestions
        seo = results.get('seo', {})
        if seo.get('issues'):
            for issue in seo['issues'][:2]:  # Limit to 2 suggestions
                suggestions_data.append({
                    'type': 'seo',
                    'title': f"SEO: {issue['message']}",
                    'description': issue['message'],
                    'severity': issue.get('severity', 'medium')
                })

        return suggestions_data


class WritingSuggestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writing suggestions
    """
    queryset = WritingSuggestion.objects.all()
    serializer_class = WritingSuggestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by account"""
        queryset = super().get_queryset()
        if hasattr(self.request, 'account') and self.request.account:
            queryset = queryset.filter(account=self.request.account)
        return queryset

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a writing suggestion"""
        suggestion = self.get_object()
        suggestion.accept_suggestion()

        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a writing suggestion"""
        suggestion = self.get_object()
        suggestion.dismiss_suggestion()

        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply suggestion to text"""
        suggestion = self.get_object()
        original_text = request.data.get('original_text', '')

        if not original_text:
            return Response(
                {"detail": "Original text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        modified_text = suggestion.apply_to_text(original_text)

        return Response({
            'original_text': original_text,
            'modified_text': modified_text,
            'suggestion_applied': suggestion.title
        })


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint for content analysis service
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'content_analysis',
        'version': '1.0.0'
    })


@api_view(['POST'])
def real_time_check(request):
    """
    Lightweight endpoint for real-time text checking (no caching)
    Used by the editor for live validation feedback
    """
    text = request.data.get('text', '')
    check_type = request.data.get('type', 'grammar')

    if not text or len(text.strip()) < 5:
        return Response({'issues': [], 'score': 100})

    # Create temporary analysis object
    analysis = TextAnalysis(
        text_content=text,
        analysis_type=check_type,
        language=request.data.get('language', 'en')
    )

    # Perform analysis without saving to database
    if check_type == 'grammar':
        results = analysis._check_grammar()
    elif check_type == 'readability':
        results = analysis._calculate_readability()
    else:
        results = analysis._comprehensive_analysis()

    return Response({
        'issues': results.get('issues', []),
        'score': results.get('score') if 'score' in results else results.get('overall_score', 0),
        'metrics': results.get('metrics', {}),
        'level': results.get('readability_level', 'Unknown')
    })
