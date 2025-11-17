from django.db import models
import uuid
from django.utils import timezone
from django.core.cache import cache
import json
import re


class TextAnalysis(models.Model):
    """
    Text analysis results for grammar checking and readability scoring
    """

    ANALYSIS_TYPES = [
        ('grammar', 'Grammar Check'),
        ('readability', 'Readability Analysis'),
        ('seo', 'SEO Analysis'),
        ('comprehensive', 'Comprehensive Analysis'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tenant relationship
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE,
                                related_name='text_analyses', null=True, blank=True)

    # Text being analyzed
    text_content = models.TextField(help_text="The text content being analyzed")
    text_hash = models.CharField(max_length=64, db_index=True,
                                help_text="SHA256 hash of text for caching")

    # Analysis metadata
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES, default='comprehensive')
    language = models.CharField(max_length=10, default='en', help_text="Language code (en, es, fr, etc.)")

    # Analysis results stored as JSON
    results = models.JSONField(default=dict, help_text="Analysis results and metrics")

    # Caching and performance
    is_cached = models.BooleanField(default=False)
    cache_expires_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'text_hash', 'analysis_type']),
            models.Index(fields=['analysis_type', 'language']),
            models.Index(fields=['created_at']),
            models.Index(fields=['cache_expires_at']),
        ]
        unique_together = [['account', 'text_hash', 'analysis_type']]

    def __str__(self):
        return f"{self.analysis_type.title()} for {self.account.name if self.account else 'System'}"

    def save(self, *args, **kwargs):
        # Generate text hash if not provided
        if not self.text_hash and self.text_content:
            import hashlib
            self.text_hash = hashlib.sha256(self.text_content.encode()).hexdigest()

        # Set cache expiration (24 hours from now)
        if not self.cache_expires_at:
            self.cache_expires_at = timezone.now() + timezone.timedelta(hours=24)

        super().save(*args, **kwargs)

    @classmethod
    def get_cached_analysis(cls, text_content, analysis_type, account=None, language='en'):
        """Get cached analysis results if available"""
        import hashlib
        text_hash = hashlib.sha256(text_content.encode()).hexdigest()

        # Check cache first
        cache_key = f"text_analysis_{text_hash}_{analysis_type}_{language}"
        cached_results = cache.get(cache_key)

        if cached_results:
            # Try to get existing analysis instance
            try:
                analysis = cls.objects.get(
                    text_hash=text_hash,
                    analysis_type=analysis_type,
                    language=language,
                    account=account
                )
                return analysis
            except cls.DoesNotExist:
                pass

        return None

    def perform_analysis(self):
        """Perform the requested text analysis"""
        if self.analysis_type == 'grammar':
            self.results = self._check_grammar()
        elif self.analysis_type == 'readability':
            self.results = self._calculate_readability()
        elif self.analysis_type == 'seo':
            self.results = self._analyze_seo()
        elif self.analysis_type == 'comprehensive':
            self.results = self._comprehensive_analysis()

        self.save()
        return self.results

    def _check_grammar(self):
        """Basic grammar checking (expandable to use external services)"""
        issues = []

        # Basic punctuation checks
        sentences = re.split(r'[.!?]+', self.text_content)
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Check for double spaces
                if '  ' in sentence:
                    issues.append({
                        'type': 'double_space',
                        'message': 'Double spaces found',
                        'severity': 'minor',
                        'position': sentence.find('  ')
                    })

                # Check for missing spaces after punctuation
                if re.search(r'[.!?][A-Z]', sentence):
                    issues.append({
                        'type': 'spacing_after_punctuation',
                        'message': 'Missing space after punctuation',
                        'severity': 'minor'
                    })

        # Check for repeated words
        words = re.findall(r'\b\w+\b', self.text_content.lower())
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and len(words[i]) > 3:  # Ignore short words
                issues.append({
                    'type': 'repeated_word',
                    'message': f'Repeated word: "{words[i]}"',
                    'severity': 'warning',
                    'word': words[i]
                })

        return {
            'issues': issues,
            'issue_count': len(issues),
            'score': max(0, 100 - (len(issues) * 5))  # Deduct points for issues
        }

    def _calculate_readability(self):
        """Calculate readability scores"""
        text = self.text_content

        # Basic metrics
        sentences = len(re.findall(r'[.!?]+', text)) or 1
        words = len(re.findall(r'\b\w+\b', text)) or 1
        syllables = self._count_syllables(text)
        characters = len(text)

        # Average words per sentence
        avg_words_per_sentence = words / sentences

        # Average syllables per word
        avg_syllables_per_word = syllables / words

        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))

        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59

        # Determine readability level
        readability_level = self._get_readability_level(flesch_score)

        return {
            'flesch_reading_ease': round(flesch_score, 1),
            'flesch_kincaid_grade': round(fk_grade, 1),
            'readability_level': readability_level,
            'metrics': {
                'total_sentences': sentences,
                'total_words': words,
                'total_syllables': syllables,
                'total_characters': characters,
                'avg_words_per_sentence': round(avg_words_per_sentence, 1),
                'avg_syllables_per_word': round(avg_syllables_per_word, 1)
            }
        }

    def _count_syllables(self, text):
        """Count syllables in text (basic implementation)"""
        text = text.lower()
        syllables = 0

        # Simple syllable counting
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            word_syllables = 0
            vowels = "aeiouy"
            prev_char_was_vowel = False

            for char in word:
                if char in vowels:
                    if not prev_char_was_vowel:
                        word_syllables += 1
                    prev_char_was_vowel = True
                else:
                    prev_char_was_vowel = False

            # Handle silent 'e'
            if word.endswith('e') and word_syllables > 1:
                word_syllables -= 1

            # Every word has at least one syllable
            syllables += max(1, word_syllables)

        return syllables

    def _get_readability_level(self, flesch_score):
        """Determine readability level from Flesch score"""
        if flesch_score >= 90:
            return 'Very Easy'
        elif flesch_score >= 80:
            return 'Easy'
        elif flesch_score >= 70:
            return 'Fairly Easy'
        elif flesch_score >= 60:
            return 'Standard'
        elif flesch_score >= 50:
            return 'Fairly Difficult'
        elif flesch_score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'

    def _analyze_seo(self):
        """Basic SEO analysis"""
        issues = []
        suggestions = []

        # Title analysis (assuming first line is title)
        lines = self.text_content.split('\n')
        title = lines[0] if lines else ''

        if len(title) < 30:
            issues.append({
                'type': 'title_too_short',
                'message': 'Title is too short for SEO',
                'severity': 'warning'
            })
        elif len(title) > 60:
            issues.append({
                'type': 'title_too_long',
                'message': 'Title is too long for SEO',
                'severity': 'warning'
            })

        # Keyword density (very basic)
        words = re.findall(r'\b\w+\b', self.text_content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Find potential keywords (words appearing more than 3 times)
        keywords = [word for word, count in word_freq.items() if count > 3 and len(word) > 3]

        # Readability check
        readability = self._calculate_readability()
        if readability['flesch_reading_ease'] < 60:
            suggestions.append('Consider simplifying your language for better SEO reach')

        return {
            'issues': issues,
            'suggestions': suggestions,
            'keywords': keywords[:10],  # Top 10 potential keywords
            'title_length': len(title),
            'optimal_title_length': (30, 60),
            'readability_score': readability['flesch_reading_ease']
        }

    def _comprehensive_analysis(self):
        """Run all analyses"""
        grammar = self._check_grammar()
        readability = self._calculate_readability()
        seo = self._analyze_seo()

        # Overall score (weighted average)
        weights = {'grammar': 0.3, 'readability': 0.4, 'seo': 0.3}
        overall_score = (
            grammar['score'] * weights['grammar'] +
            readability['flesch_reading_ease'] * weights['readability'] +
            min(100, seo['readability_score'] + 20) * weights['seo']  # SEO boost
        )

        return {
            'overall_score': round(overall_score, 1),
            'grammar': grammar,
            'readability': readability,
            'seo': seo,
            'summary': self._generate_analysis_summary(grammar, readability, seo)
        }

    def _generate_analysis_summary(self, grammar, readability, seo):
        """Generate a human-readable summary"""
        summary = []

        # Grammar summary
        if grammar['issue_count'] == 0:
            summary.append("No grammar issues detected.")
        else:
            summary.append(f"Found {grammar['issue_count']} potential grammar issues.")

        # Readability summary
        level = readability['readability_level']
        grade = readability['flesch_kincaid_grade']
        summary.append(f"Readability level: {level} (Grade {grade:.1f})")

        # SEO summary
        if seo['issues']:
            summary.append(f"Found {len(seo['issues'])} SEO optimization opportunities.")
        else:
            summary.append("Basic SEO requirements met.")

        return summary


class WritingSuggestion(models.Model):
    """
    AI-powered writing suggestions and improvements
    """

    SUGGESTION_TYPES = [
        ('grammar', 'Grammar Suggestion'),
        ('style', 'Writing Style'),
        ('clarity', 'Clarity Improvement'),
        ('seo', 'SEO Optimization'),
        ('tone', 'Tone Adjustment'),
        ('length', 'Length Optimization'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relationship to text analysis
    text_analysis = models.ForeignKey(TextAnalysis, on_delete=models.CASCADE,
                                     related_name='suggestions', null=True, blank=True)

    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE,
                               related_name='writing_suggestions', null=True, blank=True)

    # Suggestion details
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Text location
    original_text = models.TextField(help_text="The original text being suggested for change")
    suggested_text = models.TextField(help_text="The suggested replacement text")
    start_position = models.IntegerField(help_text="Character position where suggestion starts")
    end_position = models.IntegerField(help_text="Character position where suggestion ends")

    # Metadata
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.50,
                                          help_text="AI confidence in this suggestion (0-1)")
    is_accepted = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['text_analysis', 'suggestion_type']),
            models.Index(fields=['account', 'is_accepted', 'is_dismissed']),
            models.Index(fields=['confidence_score']),
        ]

    def __str__(self):
        return f"{self.suggestion_type.title()}: {self.title}"

    def accept_suggestion(self):
        """Mark suggestion as accepted"""
        self.is_accepted = True
        self.is_dismissed = False
        self.save()

    def dismiss_suggestion(self):
        """Mark suggestion as dismissed"""
        self.is_dismissed = True
        self.is_accepted = False
        self.save()

    def apply_to_text(self, original_text):
        """Apply this suggestion to the original text"""
        if not original_text:
            return self.suggested_text

        start = min(self.start_position, len(original_text))
        end = min(self.end_position, len(original_text))

        return (
            original_text[:start] +
            self.suggested_text +
            original_text[end:]
        )
