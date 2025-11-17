from django.db import models
from django.utils.text import slugify
import uuid
import json
from datetime import timedelta
from django.utils import timezone


class ContentTemplate(models.Model):
    """
    Reusable content templates for consistent article structure
    Enterprise-grade template management system
    """
    TEMPLATE_TYPES = [
        ('article', 'Article'),
        ('guide', 'Guide/Tutorial'),
        ('feature', 'Feature Story'),
        ('news', 'News Article'),
        ('opinion', 'Opinion Piece'),
        ('announcement', 'Announcement'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tenant relationship
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='content_templates', null=True, blank=True)

    name = models.CharField(max_length=200, help_text="Template display name")
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, help_text="Template description and usage guidelines")

    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='article')

    # Template structure
    title_template = models.CharField(
        max_length=500,
        blank=True,
        help_text="Title template with placeholders (e.g., '{Topic}: {Main Point}')"
    )
    content_structure = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured content sections with placeholders"
    )
    default_content = models.TextField(
        blank=True,
        help_text="Default content with placeholders that users can customize"
    )
    default_excerpt = models.TextField(
        blank=True,
        max_length=300,
        help_text="Default excerpt template"
    )

    # Template metadata
    estimated_word_count = models.IntegerField(
        default=0,
        help_text="Estimated word count for content using this template"
    )

    # Usage analytics
    usage_count = models.IntegerField(default=0, help_text="Number of times this template has been used")
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Template settings
    is_default = models.BooleanField(default=False, help_text="Default template for this account")
    is_public = models.BooleanField(default=False, help_text="Available to all users")
    is_active = models.BooleanField(default=True)

    # Audit
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-usage_count', 'name']
        unique_together = [['account', 'slug']] if None else [['slug']]  # Account-specific uniqueness
        indexes = [
            models.Index(fields=['account', 'is_active']),
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['usage_count']),
            models.Index(fields=['is_default']),
        ]



    def __str__(self):
        return f"{self.account.name if self.account else 'System'}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_example_content(self):
        """
        Generate example content based on template structure
        """
        if self.default_content:
            return self.default_content

        # Generate example based on template type
        examples = {
            'article': """# Introduction

[Brief introduction to hook readers and establish the topic's importance]

## Main Section 1

[Detailed exploration of the first major point]

### Supporting Evidence

- Point 1 with explanation
- Point 2 with supporting data
- Point 3 with real-world examples

## Main Section 2

[Second major aspect with analysis]

## Conclusion

[Summarize key points and provide actionable takeaways]

---

**Resources:** [Relevant links and further reading]""",

            'guide': """# Complete Guide to [Topic]

## Overview

[Brief introduction explaining what readers will learn and why it's important]

## Prerequisites

What readers should know or have before starting:

- Prerequisite 1
- Prerequisite 2
- Prerequisite 3

## Step-by-Step Instructions

### Step 1: Preparation
[Detailed instructions for the first step]

### Step 2: Execution
[Main implementation steps with code/examples]

### Step 3: Testing & Validation
[How to verify everything works correctly]

### Step 4: Optimization
[Performance tips and best practices]

## Common Issues & Solutions

**Problem 1:** [Description]
**Solution:** [Step-by-step fix]

## Advanced Usage

[Advanced techniques for experienced users]

## Summary

[Key takeaways and next steps]""",

            'opinion': """# [Strong Opinion Statement]

## The Current State

[Current situation analysis and context]

## The Problem

[What's wrong with the current approach]

## A Better Way

[Proposed solution with reasoning]

## Why This Matters

[Broader implications and impact]

## Counterarguments Addressed

**Counterpoint 1:** [Common objection]
**Response:** [Why this objection doesn't hold]

## Conclusion

[Final thoughts and call to action]""",

            'news': """# [Breaking/Headline News]

## What Happened

[Factual summary of events in chronological order]

## The Details

[Expanded context and background information]

## Impact & Analysis

[What this means for affected parties]

## Quotes & Reactions

> "Relevant quote from key person" - Source, Title

## Next Steps

[What's happening next and expected developments]

**Updated:** [Latest developments as they occur]

---

*Full coverage continues as more information becomes available.*"""
        }

        return examples.get(self.template_type, self.default_content or "")

    @classmethod
    def create_default_templates(cls, account=None):
        """
        Create default templates for an account
        """
        templates_data = [
            {
                'name': 'Standard Article',
                'template_type': 'article',
                'description': 'Classic article format with introduction, body, and conclusion',
                'estimated_word_count': 800,
                'is_default': True,
                'is_public': True,
            },
            {
                'name': 'Guide/Tutorial',
                'template_type': 'guide',
                'description': 'Step-by-step instructional content',
                'estimated_word_count': 1500,
                'is_public': True,
            },
            {
                'name': 'Opinion Piece',
                'template_type': 'opinion',
                'description': 'Personal or editorial opinion format',
                'estimated_word_count': 600,
                'is_public': True,
            },
            {
                'name': 'News Release',
                'template_type': 'news',
                'description': 'Breaking news and announcements',
                'estimated_word_count': 400,
                'is_public': True,
            },
            {
                'name': 'Feature Story',
                'template_type': 'feature',
                'description': 'In-depth feature articles with rich multimedia',
                'estimated_word_count': 1200,
                'is_public': True,
            },
        ]

        created_templates = []
        for template_data in templates_data:
            template, created = cls.objects.get_or_create(
                account=account,
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_templates.append(template)

        return created_templates


class Topic(models.Model):
    """
    Content categories (Technology, Writing, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tenant relationship
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='topics', null=True, blank=True)

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#0066FF')  # Hex color

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = [['account', 'slug']]  # Ensure unique slugs per account
        indexes = [
            models.Index(fields=['account', 'slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class Article(models.Model):
    """
    Core content model - blog posts/articles
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tenant relationship
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='articles', null=True, blank=True)

    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField()  # Markdown format
    excerpt = models.TextField(blank=True, max_length=300)

    # Relationships
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='articles')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    hero_image = models.ForeignKey('media.Media', on_delete=models.SET_NULL, null=True, blank=True)

    # Content relationships
    series = models.ForeignKey('Series', on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    series_order = models.PositiveIntegerField(default=0)  # Order within series
    related_articles = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_to')

    # Follow-up content
    follow_up_links = models.JSONField(default=list, blank=True)  # [{'title': str, 'url': str}]

    # Multimedia content
    media_gallery = models.ManyToManyField('media.Media', blank=True, related_name='article_galleries')
    video_embed_url = models.URLField(blank=True, help_text="YouTube, Vimeo, or direct video URL")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)

    # Premium content
    is_premium = models.BooleanField(default=False)
    premium_excerpt = models.TextField(blank=True, help_text="Preview content for non-subscribers")

    # Auto-calculated fields
    word_count = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=0)  # minutes

    # Analytics
    view_count = models.IntegerField(default=0)
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # For recommendations

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['account', 'status', 'published_at']),
            models.Index(fields=['account', 'slug']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['account', 'author']),
            models.Index(fields=['is_premium']),
            models.Index(fields=['engagement_score']),
            models.Index(fields=['series', 'series_order']),
        ]
        unique_together = [['account', 'slug']]  # Ensure unique slugs per account

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Track if this is a new article
        is_new = self.pk is None

        # Get the current instance before saving (for version comparison)
        if not is_new:
            old_instance = Article.objects.get(pk=self.pk)
        else:
            old_instance = None

        # Auto-generate slug from title
        if not self.slug or (old_instance and old_instance.title != self.title):
            self.slug = slugify(self.title)

        # Auto-generate excerpt from content
        if not self.excerpt and self.content:
            self.excerpt = self.content[:300]

        # Calculate word count
        self.word_count = len(self.content.split())

        # Calculate reading time (avg 200 words/min)
        self.reading_time = max(1, self.word_count // 200)

        # Set published_at on first publish
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

        # Calculate engagement score for recommendations
        self.engagement_score = self.calculate_engagement_score()

        super().save(*args, **kwargs)

        # Version control - automatically create versions (except for new articles)
        if not is_new and hasattr(self, '_create_version') and self._create_version:
            # Only create version if significant changes were made
            if self._has_significant_changes(old_instance):
                ArticleVersion.create_version(
                    article=self,
                    user=getattr(self, '_version_user', None),
                    change_summary=getattr(self, '_version_summary', ''),
                    is_auto_saved=getattr(self, '_auto_saved', False)
                )

        # Reset version control flags
        self._create_version = False
        self._version_user = None
        self._version_summary = ''
        self._auto_saved = False

        # Ensure workflow exists for new articles
        if is_new and hasattr(self, '_ensure_workflow'):
            self._create_or_get_workflow()

    def _has_significant_changes(self, old_instance):
        """
        Check if the changes are significant enough to warrant a version
        """
        if not old_instance:
            return True

        # Always create version for status changes
        if old_instance.status != self.status:
            return True

        # Check content changes (more than just whitespace/formatting)
        content_changed = len(self.content.strip()) != len(old_instance.content.strip())
        if content_changed:
            # Check if it's a meaningful change (not just formatting)
            import difflib
            similarity = difflib.SequenceMatcher(None, self.content, old_instance.content).ratio()
            if similarity < 0.95:  # Less than 95% similar
                return True

        # Check title changes
        if old_instance.title != self.title:
            return True

        # Check topic changes
        if old_instance.topic != self.topic:
            return True

        return False

    def _create_or_get_workflow(self):
        """
        Ensure an EditorialWorkflow exists for this article
        """
        if not hasattr(self, 'workflow'):
            EditorialWorkflow.objects.get_or_create(article=self)

    def create_version(self, user=None, summary="", auto_save=False):
        """
        Manually create a version with specific metadata
        """
        self._create_version = True
        self._version_user = user
        self._version_summary = summary
        self._auto_saved = auto_save
        self.save()

    def get_version_history(self, limit=20):
        """
        Get version history for this article
        """
        return self.versions.order_by('-version_number')[:limit]

    def restore_version(self, version_number, user=None):
        """
        Restore article to a specific version
        """
        try:
            version = self.versions.get(version_number=version_number)
            return version.restore_to_article(user)
        except ArticleVersion.DoesNotExist:
            raise ValueError(f"Version {version_number} not found for this article")

    def submit_for_review(self, user, assign_to=None, due_date=None, priority='normal'):
        """
        Submit article for editorial review
        """
        self.status = 'draft'  # Ensure it's in draft status
        workflow, created = EditorialWorkflow.objects.get_or_create(article=self)

        if workflow.status == 'draft':
            workflow.request_review(
                requested_by=user,
                assign_to=assign_to,
                due_date=due_date,
                priority=priority
            )

        self.save()

    def can_be_edited_by(self, user):
        """
        Check if a user can edit this article
        """
        # Authors can always edit their own articles if not published
        if self.author == user and self.status == 'draft':
            return True

        # Check workflow permissions if workflow exists
        if hasattr(self, 'workflow') and self.workflow:
            return self.workflow.can_be_edited_by(user)

        # Fallback: users with content management permissions
        return user.has_perm('articles.change_article')

    def can_be_published_by(self, user):
        """
        Check if a user can publish this article
        """
        # Check workflow permissions
        if hasattr(self, 'workflow') and self.workflow:
            return 'publish' in self.workflow.get_available_actions(user)

        # Fallback: publishing permissions
        return user.has_perm('articles.can_publish')

    def calculate_engagement_score(self):
        """
        Calculate engagement score for content recommendations
        """
        if not self.published_at:
            return 0.00

        hours_since_publish = (timezone.now() - self.published_at).total_seconds() / 3600

        if hours_since_publish <= 0:
            return 0.00

        # Simple engagement scoring: views per hour, with decay over time
        score = (self.view_count / max(1, hours_since_publish)) * 10

        # Cap at 100 for performance
        return min(100.00, round(score, 2))

    def get_related_articles(self, limit=5):
        """
        Get related articles based on topic, author, and content similarity
        """
        from django.db.models import Q

        related = Article.objects.filter(
            account=self.account,
            status='published'
        ).exclude(id=self.id)

        # Priority: same series > same topic > same author > high engagement
        related = related.annotate(
            relevance_score=models.Case(
                models.When(series=self.series, then=models.Value(10)),
                models.When(topic=self.topic, then=models.Value(7)),
                models.When(author=self.author, then=models.Value(5)),
                default=models.Value(1),
                output_field=models.IntegerField()
            )
        ).order_by('-relevance_score', '-engagement_score', '-published_at')

        return related[:limit]


class ArticleVersion(models.Model):
    """
    Version control system for articles - tracks changes and enables restoration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='versions')

    # Version metadata
    version_number = models.PositiveIntegerField()
    change_summary = models.CharField(max_length=500, blank=True, help_text="Brief description of changes")
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='article_versions')
    is_auto_saved = models.BooleanField(default=False, help_text="True for automatic saves, False for manual saves")

    # Content snapshots
    title = models.CharField(max_length=200)
    content = models.TextField()  # Full content at time of save
    excerpt = models.TextField(blank=True, max_length=300)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)

    # Metadata snapshots
    word_count = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('published', 'Published')])

    # File attachments snapshot
    media_files = models.JSONField(default=list, blank=True)  # List of media file references
    hero_image = models.ForeignKey('media.Media', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = [['article', 'version_number']]
        indexes = [
            models.Index(fields=['article', 'version_number']),
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Version {self.version_number} of {self.article.title}"

    @classmethod
    def create_version(cls, article, user=None, change_summary="", is_auto_saved=False):
        """
        Create a new version of an article
        """
        # Get the latest version number
        latest_version = cls.objects.filter(article=article).order_by('-version_number').first()
        version_number = (latest_version.version_number + 1) if latest_version else 1

        # Get current media files
        media_files = list(article.media_gallery.values_list('id', flat=True))

        # Create the version
        version = cls.objects.create(
            article=article,
            version_number=version_number,
            change_summary=change_summary,
            created_by=user,
            is_auto_saved=is_auto_saved,
            title=article.title,
            content=article.content,
            excerpt=article.excerpt,
            topic=article.topic,
            word_count=article.word_count,
            reading_time=article.reading_time,
            status=article.status,
            media_files=media_files,
            hero_image=article.hero_image
        )

        return version

    def restore_to_article(self, user=None):
        """
        Restore this version to the current article
        """
        article = self.article

        # Update article with version content
        article.title = self.title
        article.content = self.content
        article.excerpt = self.excerpt
        article.topic = self.topic
        article.word_count = self.word_count
        article.reading_time = self.reading_time
        article.status = self.status
        article.hero_image = self.hero_image

        # Restore media gallery
        from apps.media.models import MediaItem
        media_items = MediaItem.objects.filter(id__in=self.media_files)
        article.media_gallery.set(media_items)

        # Save the article (this will create a new version automatically)
        article.save()

        # Log the restoration in the new version
        ArticleVersion.create_version(
            article=article,
            user=user,
            change_summary=f"Restored from version {self.version_number}",
            is_auto_saved=False
        )

        return article

    def get_changes_summary(self, previous_version=None):
        """
        Generate a summary of changes from previous version
        """
        if not previous_version:
            # Get the previous version
            previous_version = ArticleVersion.objects.filter(
                article=self.article,
                version_number__lt=self.version_number
            ).order_by('-version_number').first()

        if not previous_version:
            return "Initial version"

        changes = []

        if self.title != previous_version.title:
            changes.append(f"Title changed from '{previous_version.title}' to '{self.title}'")

        if self.status != previous_version.status:
            changes.append(f"Status changed from {previous_version.status} to {self.status}")

        if self.topic != previous_version.topic:
            old_topic = previous_version.topic.name if previous_version.topic else "None"
            new_topic = self.topic.name if self.topic else "None"
            changes.append(f"Topic changed from {old_topic} to {new_topic}")

        content_changed = len(self.content) != len(previous_version.content)
        if content_changed:
            changes.append(f"Content modified ({len(self.content)} vs {len(previous_version.content)} characters)")

        media_changed = set(self.media_files) != set(previous_version.media_files)
        if media_changed:
            changes.append(f"Media files updated ({len(self.media_files)} vs {len(previous_version.media_files)})")

        return "; ".join(changes) if changes else "Minor content updates"


class EditorialWorkflow(models.Model):
    """
    Editorial workflow management system for content approval
    """
    WORKFLOW_STATUS = [
        ('draft', 'Draft - Author Working'),
        ('review_requested', 'Review Requested'),
        ('in_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected - Needs Revision'),
        ('published', 'Published'),
    ]

    REVIEW_STATUS = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='workflow')

    # Current status
    status = models.CharField(max_length=20, choices=WORKFLOW_STATUS, default='draft')
    current_reviewer = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='assigned_reviews', help_text="User currently assigned to review")

    # Assignment tracking
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='workflow_assignments')
    assigned_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    # Publishing permissions
    can_publish_directly = models.BooleanField(default=False, help_text="Skip review process for senior authors")
    auto_publish_on_approval = models.BooleanField(default=False, help_text="Automatically publish when approved")

    # Review history
    review_history = models.JSONField(default=list, blank=True)  # [{"reviewer": user_id, "status": "", "comment": "", "timestamp": ""}]

    # Metadata
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')], default='normal')
    internal_notes = models.TextField(blank=True, help_text="Internal editorial notes")
    revision_count = models.PositiveIntegerField(default=0)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['current_reviewer']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Workflow for {self.article.title} ({self.get_status_display()})"

    def request_review(self, requested_by, assign_to=None, due_date=None, priority='normal'):
        """
        Request review for the article
        """
        from django.utils import timezone

        self.status = 'review_requested'
        self.current_reviewer = assign_to
        self.assigned_by = requested_by
        self.assigned_at = timezone.now()
        self.due_date = due_date
        self.priority = priority
        self.save()

        # Log the review request
        self._add_review_history('requested', f"Review requested by {requested_by.get_full_name()}", requested_by)

    def assign_reviewer(self, assign_to, assigned_by, due_date=None):
        """
        Assign a reviewer to this workflow
        """
        from django.utils import timezone

        self.current_reviewer = assign_to
        self.assigned_by = assigned_by
        self.assigned_at = timezone.now()
        self.due_date = due_date
        self.status = 'in_review'
        self.save()

        # Log the assignment
        self._add_review_history('assigned', f"Assigned to {assign_to.get_full_name()}", assigned_by)

    def submit_review(self, reviewer, status, comment=""):
        """
        Submit a review decision
        """
        from django.utils import timezone

        self.last_reviewed_at = timezone.now()

        # Log the review
        status_display = dict(self.REVIEW_STATUS)[status]
        self._add_review_history(status, f"{status_display}: {comment}", reviewer)

        # Update status based on review
        if status == 'accepted':
            if self.auto_publish_on_approval:
                self._publish_article(reviewer)
            else:
                self.status = 'approved'
        elif status == 'rejected':
            self.status = 'rejected'
        elif status == 'changes_requested':
            self.status = 'draft'
            self.revision_count += 1

        self.save()

    def approve_for_publication(self, approved_by):
        """
        Approve article for publication
        """
        from django.utils import timezone

        if self.status not in ['approved', 'in_review']:
            raise ValueError("Article must be approved or under review to publish")

        self.status = 'approved'
        self._add_review_history('approved', f"Approved for publication by {approved_by.get_full_name()}", approved_by)
        self.save()

    def publish_now(self, published_by):
        """
        Publish the article immediately
        """
        self._publish_article(published_by)

    def _publish_article(self, published_by):
        """
        Publish the article and update workflow
        """
        from django.utils import timezone

        article = self.article
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()

        self.status = 'published'
        self.published_at = timezone.now()
        self._add_review_history('published', f"Published by {published_by.get_full_name()}", published_by)
        self.save()

    def _add_review_history(self, action, comment, user):
        """
        Add an entry to the review history
        """
        from django.utils import timezone

        history_entry = {
            'action': action,
            'comment': comment,
            'user_id': str(user.id) if user else None,
            'user_name': user.get_full_name() if user else 'System',
            'timestamp': timezone.now().isoformat()
        }

        self.review_history.append(history_entry)

    def can_be_edited_by(self, user):
        """
        Check if a user can edit this article
        """
        # Authors can always edit their own articles
        if self.article.author == user:
            return True

        # Users with management permissions can edit
        from django.contrib.auth.models import Permission
        manage_content = user.has_perm('articles.manage_content')
        if manage_content:
            return True

        # Reviewers can edit when in review
        if self.status in ['in_review', 'changes_requested'] and self.current_reviewer == user:
            return True

        return False

    def get_available_actions(self, user):
        """
        Get available actions for a user on this workflow
        """
        actions = []

        if self.can_be_edited_by(user):
            actions.append('edit')

        # Review actions
        if self.current_reviewer == user and self.status == 'in_review':
            actions.extend(['accept', 'reject', 'request_changes'])

        # Publishing actions
        if user.has_perm('articles.can_publish'):
            if self.status == 'approved':
                actions.append('publish')
            elif self.can_publish_directly and self.article.author == user:
                actions.append('publish_direct')

        # Assignment actions
        if user.has_perm('articles.can_assign_reviewers'):
            actions.append('assign_reviewer')

        return actions

    def get_recent_reviews(self, limit=5):
        """
        Get the most recent review history
        """
        return self.review_history[-limit:] if self.review_history else []

    def is_overdue(self):
        """
        Check if this workflow is overdue
        """
        if not self.due_date:
            return False

        from django.utils import timezone
        return timezone.now() > self.due_date

    @property
    def time_since_last_update(self):
        """
        Get human-readable time since last update
        """
        from django.utils.timesince import timesince
        return timesince(self.updated_at)

    @property
    def days_overdue(self):
        """
        Get number of days overdue, or None if not overdue
        """
        if not self.is_overdue():
            return None

        from django.utils import timezone
        return (timezone.now() - self.due_date).days


class Series(models.Model):
    """
    Collection of related articles (series, guides, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tenant relationship
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='series', null=True, blank=True)

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    # Series metadata
    cover_image = models.ForeignKey('media.Media', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['account']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def article_count(self):
        return self.articles.filter(status='published').count()

    def get_articles_in_order(self):
        """Get all articles in series order"""
        return self.articles.filter(status='published').order_by('series_order', 'published_at')


class Comment(models.Model):
    """
    Social reading - comments on articles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')

    # Content
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    # Status
    is_approved = models.BooleanField(default=True)  # For moderation
    is_spam = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', 'is_approved']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title}"


class ArticleReaction(models.Model):
    """
    Social reading - reactions to articles
    """
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('laugh', 'Laugh'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='article_reactions')

    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['article', 'user']  # One reaction per user per article
        indexes = [
            models.Index(fields=['article', 'reaction_type']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.reaction_type}d {self.article.title}"


class ArticleAnnotation(models.Model):
    """
    Social reading - user annotations/highlights
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='annotations')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='annotations')

    # Annotation data
    selected_text = models.TextField()
    note = models.TextField(blank=True)

    # Implementation note: In a full implementation, you'd store selection ranges
    # For simplicity, we'll store the text selection
    selection_start = models.IntegerField()  # Character position in content
    selection_end = models.IntegerField()

    # Optional: store annotation position for display
    position_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', 'user']),
        ]

    def __str__(self):
        return f"Annotation by {self.user.username} on {self.article.title}"


class CollaborativeSession(models.Model):
    """
    Manages collaborative editing sessions for articles
    Tracks multiple users editing simultaneously with real-time synchronization
    """
    SESSION_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
        ('locked', 'Locked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Session relationship
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='collaborative_session')

    # Session metadata
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    session_name = models.CharField(max_length=200, blank=True, help_text="Optional session name for group collaboration")

    # Participants tracking
    participants = models.ManyToManyField('users.User', through='SessionParticipant', related_name='collaborative_sessions')

    # Document state
    current_content = models.TextField(blank=True, help_text="Current collaborative content state")
    current_title = models.CharField(max_length=200, blank=True, help_text="Current collaborative title")
    base_version = models.IntegerField(default=0, help_text="Article version this session started from")

    # Operation tracking
    operations = models.JSONField(default=list, blank=True, help_text="List of operational transforms applied")
    operation_sequence = models.PositiveIntegerField(default=0, help_text="Sequential counter for operations")

    # Session settings
    allow_anonymous = models.BooleanField(default=False, help_text="Allow anonymous contributors")
    max_participants = models.PositiveIntegerField(default=10, help_text="Maximum number of participants")
    auto_save_interval = models.PositiveIntegerField(default=30, help_text="Auto-save interval in seconds")

    # Session management
    is_locked = models.BooleanField(default=False, help_text="Lock session to prevent new joins")
    locked_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='locked_sessions')

    # Session creator
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_sessions')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Session expiration time")

    class Meta:
        indexes = [
            models.Index(fields=['status', 'last_activity']),
            models.Index(fields=['article', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Session for {self.article.title} ({self.get_status_display()})"

    def is_expired(self):
        """Check if session has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def is_active(self):
        """Check if session is currently active"""
        return (
            self.status == 'active' and
            not self.is_expired() and
            not self.is_locked
        )

    def add_participant(self, user):
        """Add a participant to the session"""
        if self.participants.count() >= self.max_participants:
            raise ValueError("Session is full")

        participant, created = SessionParticipant.objects.get_or_create(
            session=self,
            user=user,
            defaults={'joined_at': timezone.now()}
        )

        if not created:
            # Update last activity
            participant.last_activity = timezone.now()
            participant.save()

        return participant

    def remove_participant(self, user):
        """Remove a participant from the session"""
        SessionParticipant.objects.filter(session=self, user=user).delete()

    def get_active_participants(self):
        """Get currently active participants"""
        cutoff_time = timezone.now() - timedelta(minutes=5)  # Consider inactive after 5 minutes
        return self.participants.filter(
            sessionparticipant__last_activity__gte=cutoff_time
        )

    def apply_operation(self, operation, user, sequence_number=None):
        """Apply an operational transform"""
        if sequence_number is None:
            sequence_number = self.operation_sequence + 1

        # Validate sequence number
        if sequence_number != self.operation_sequence + 1:
            raise ValueError(f"Invalid sequence number. Expected {self.operation_sequence + 1}, got {sequence_number}")

        # Apply the operation to current content
        self.current_content = self._apply_operation_to_content(operation, self.current_content)
        self.current_title = self._apply_operation_to_title(operation, self.current_title)

        # Store the operation
        operation_data = {
            'sequence': sequence_number,
            'user_id': str(user.id),
            'user_name': user.get_full_name() or user.username,
            'operation': operation,
            'applied_at': timezone.now().isoformat()
        }

        self.operations.append(operation_data)
        self.operation_sequence = sequence_number
        self.save()

        return operation_data

    def _apply_operation_to_content(self, operation, content):
        """Apply operation to content using OT principles"""
        op_type = operation.get('type')
        position = operation.get('position', 0)

        if op_type == 'insert':
            text = operation.get('text', '')
            return content[:position] + text + content[position:]
        elif op_type == 'delete':
            length = operation.get('length', 0)
            return content[:position] + content[position + length:]
        elif op_type == 'replace':
            old_text = operation.get('old_text', '')
            new_text = operation.get('new_text', '')
            # Simple text replacement
            return content.replace(old_text, new_text, 1) if old_text in content else content

        return content

    def _apply_operation_to_title(self, operation, title):
        """Apply operation to title (subset of content operations)"""
        op_type = operation.get('type')

        # Only allow insert/delete operations on title
        if op_type in ['insert', 'delete']:
            return self._apply_operation_to_content(operation, title)

        return title

    def save_to_article(self, user=None, create_version=True):
        """Save current collaborative state back to the article"""
        self.article.title = self.current_title or self.article.title
        self.article.content = self.current_content or self.article.content
        self.article.updated_at = timezone.now()

        if create_version:
            self.article._create_version = True
            self.article._version_user = user
            self.article._version_summary = f"Collaborative edit from session {self.id}"

        self.article.save()

        # Mark session as completed
        self.status = 'completed'
        self.save()

        return self.article

    def get_operations_since(self, sequence_number):
        """Get operations since a given sequence number"""
        return [op for op in self.operations if op['sequence'] > sequence_number]

    def can_join(self, user):
        """Check if a user can join this session"""
        if self.status != 'active':
            return False

        if self.is_expired() or self.is_locked:
            return False

        if self.participants.count() >= self.max_participants:
            return False

        # Check user permissions
        return self.article.can_be_edited_by(user)

    @classmethod
    def create_session(cls, article, created_by, session_name="", expires_hours=24):
        """Create a new collaborative session for an article"""
        expires_at = timezone.now() + timedelta(hours=expires_hours) if expires_hours else None

        session = cls.objects.create(
            article=article,
            session_name=session_name or f"Collaborative editing: {article.title}",
            current_content=article.content,
            current_title=article.title,
            base_version=article.versions.count(),
            created_by=created_by,
            expires_at=expires_at
        )

        # Add creator as first participant
        session.add_participant(created_by)

        return session

    @classmethod
    def cleanup_expired_sessions(cls):
        """Clean up expired or inactive sessions"""
        cutoff_time = timezone.now() - timedelta(hours=1)  # Sessions inactive > 1 hour

        # Mark expired sessions as inactive
        expired_sessions = cls.objects.filter(
            models.Q(expires_at__lt=timezone.now()) |
            models.Q(last_activity__lt=cutoff_time),
            status='active'
        )

        expired_sessions.update(status='inactive')

        return expired_sessions.count()


class SessionParticipant(models.Model):
    """
    Tracks participants in collaborative editing sessions
    """
    USER_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('disconnected', 'Disconnected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(CollaborativeSession, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    # Participation tracking
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=USER_STATUS, default='active')

    # User position/cursor tracking
    cursor_position = models.IntegerField(default=0, help_text="Current cursor position in document")
    selection_start = models.IntegerField(default=0)
    selection_end = models.IntegerField(default=0)

    # User's color for UI highlighting
    user_color = models.CharField(max_length=7, default='#0066FF', help_text="Hex color for user identification")

    class Meta:
        unique_together = [['session', 'user']]
        indexes = [
            models.Index(fields=['session', 'status']),
            models.Index(fields=['user', 'last_activity']),
        ]

    def __str__(self):
        return f"{self.user.username} in session {self.session.id}"

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def update_cursor(self, position, selection_start=0, selection_end=0):
        """Update user's cursor position"""
        self.cursor_position = position
        self.selection_start = selection_start
        self.selection_end = selection_end
        self.update_activity()

    def disconnect(self):
        """Mark user as disconnected"""
        self.status = 'disconnected'
        self.save()

    @property
    def is_active(self):
        """Check if participant is currently active"""
        cutoff_time = timezone.now() - timedelta(minutes=5)
        return self.status == 'active' and self.last_activity >= cutoff_time


class OperationTransform(models.Model):
    """
    Stores operational transforms for collaborative editing history
    Advanced conflict resolution using Operational Transformation (OT)
    """
    OPERATION_TYPES = [
        ('insert', 'Insert Text'),
        ('delete', 'Delete Text'),
        ('replace', 'Replace Text'),
        ('format', 'Format Change'),
        ('undo', 'Undo Operation'),
        ('redo', 'Redo Operation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(CollaborativeSession, on_delete=models.CASCADE, related_name='operation_history')

    # Operation metadata
    sequence_number = models.PositiveIntegerField(help_text="Sequential operation number")
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)

    # User information
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='collaborative_operations')

    # Operation data
    operation_data = models.JSONField(help_text="Complete operation details")

    # State before operation (for undo/redo)
    previous_state = models.JSONField(default=dict, blank=True, help_text="Document state before this operation")

    # Conflict resolution
    conflicts_resolved = models.JSONField(default=list, blank=True, help_text="List of conflicts that were resolved")
    parent_operations = models.JSONField(default=list, blank=True, help_text="Operations this one depends on")

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    client_id = models.CharField(max_length=100, blank=True, help_text="Client identifier for conflict resolution")

    class Meta:
        ordering = ['session', 'sequence_number']
        unique_together = [['session', 'sequence_number']]
        indexes = [
            models.Index(fields=['session', 'sequence_number']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['client_id']),
        ]

    def __str__(self):
        return f"Op {self.sequence_number} by {self.user.username} in {self.session.article.title}"

    def transform_against(self, other_operation):
        """
        Transform this operation against another concurrent operation
        Implements basic Operational Transformation principles
        """
        # Basic OT transformation logic
        if self.operation_type == 'insert' and other_operation.operation_type == 'insert':
            return self._transform_insert_insert(other_operation)
        elif self.operation_type == 'insert' and other_operation.operation_type == 'delete':
            return self._transform_insert_delete(other_operation)
        elif self.operation_type == 'delete' and other_operation.operation_type == 'insert':
            return self._transform_delete_insert(other_operation)
        elif self.operation_type == 'delete' and other_operation.operation_type == 'delete':
            return self._transform_delete_delete(other_operation)

        # For other cases, return self unchanged (simplified OT)
        return self

    def _transform_insert_insert(self, other):
        """Transform insert operation against another insert"""
        my_pos = self.operation_data.get('position', 0)
        other_pos = other.operation_data.get('position', 0)

        if my_pos <= other_pos:
            # Other insert comes after mine, no change needed
            return self
        else:
            # Other insert comes before mine, adjust my position
            other_length = len(other.operation_data.get('text', ''))
            self.operation_data['position'] = my_pos + other_length
            return self

    def _transform_insert_delete(self, other):
        """Transform insert operation against delete"""
        my_pos = self.operation_data.get('position', 0)
        other_pos = other.operation_data.get('position', 0)
        other_length = other.operation_data.get('length', 0)

        if my_pos <= other_pos:
            # Insert before delete, no change needed
            return self
        elif my_pos < other_pos + other_length:
            # Insert within deleted range, adjust position to before delete
            self.operation_data['position'] = other_pos
            return self
        else:
            # Insert after delete, adjust position
            self.operation_data['position'] = my_pos - other_length
            return self

    def _transform_delete_insert(self, other):
        """Transform delete operation against insert"""
        my_pos = self.operation_data.get('position', 0)
        my_length = self.operation_data.get('length', 0)
        other_pos = other.operation_data.get('position', 0)
        other_length = len(other.operation_data.get('text', ''))

        if other_pos <= my_pos:
            # Insert before delete, adjust delete position
            self.operation_data['position'] = my_pos + other_length
            return self
        elif other_pos < my_pos + my_length:
            # Insert within delete range, split delete or adjust
            self.operation_data['length'] = my_length + other_length
            return self
        else:
            # Insert after delete, no change needed
            return self

    def _transform_delete_delete(self, other):
        """Transform delete operation against another delete"""
        my_pos = self.operation_data.get('position', 0)
        my_length = self.operation_data.get('length', 0)
        other_pos = other.operation_data.get('position', 0)
        other_length = other.operation_data.get('length', 0)

        # Complex overlapping delete transformation
        # Simplified: adjust positions based on overlap
        my_end = my_pos + my_length
        other_end = other_pos + other_length

        if my_pos < other_pos:
            if my_end <= other_pos:
                # No overlap, other delete after mine
                return self
            else:
                # Overlap: extend my delete to include other's range
                self.operation_data['length'] = max(my_end, other_end) - my_pos
                return self
        else:
            if other_end <= my_pos:
                # No overlap, other delete before mine
                self.operation_data['position'] = max(0, my_pos - other_length)
                return self
            else:
                # Overlap: adjust my position and possibly length
                self.operation_data['position'] = other_pos
                self.operation_data['length'] = max(my_end, other_end) - other_pos
                return self

    @classmethod
    def create_operation(cls, session, user, operation_type, operation_data, client_id="", parent_operation_ids=None):
        """Create a new operation with proper sequencing"""
        sequence_number = session.operation_sequence + 1

        operation = cls.objects.create(
            session=session,
            sequence_number=sequence_number,
            operation_type=operation_type,
            user=user,
            operation_data=operation_data,
            client_id=client_id,
            parent_operations=parent_operation_ids or []
        )

        # Update session sequence
        session.operation_sequence = sequence_number
        session.save(update_fields=['operation_sequence'])

        return operation


class BreakingNews(models.Model):
    """
    Editorial alerts - breaking news items
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('breaking', 'Breaking'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='breaking_news', null=True, blank=True)

    headline = models.CharField(max_length=300)
    subheadline = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    # Links
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True)
    external_url = models.URLField(blank=True)

    # Timing
    published_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Analytics
    click_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['priority', 'is_active']),
            models.Index(fields=['expires_at', 'is_active']),
            models.Index(fields=['account']),
        ]

    def __str__(self):
        return self.headline

    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class SearchQuery(models.Model):
    """
    Advanced search - track user search queries for analytics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='search_queries', null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    query = models.CharField(max_length=500)
    result_count = models.IntegerField(default=0)

    # Search metadata (for semantic search)
    query_vector = models.JSONField(default=list, blank=True)  # For vector embeddings
    filters_applied = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['account', 'user']),
        ]

    def __str__(self):
        return f"Search: '{self.query}'"


class Page(models.Model):
    """
    Static pages (About, Now, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tenant relationship
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='pages', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField()  # Markdown
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['account', 'slug']]  # Ensure unique slugs per account
        indexes = [
            models.Index(fields=['account', 'slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
