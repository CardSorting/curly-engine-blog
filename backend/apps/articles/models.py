from django.db import models
from django.utils.text import slugify
import uuid


class Topic(models.Model):
    """
    Content categories (Technology, Writing, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#0066FF')  # Hex color

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

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

    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField()  # Markdown format
    excerpt = models.TextField(blank=True, max_length=300)

    # Relationships
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='articles')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    hero_image = models.ForeignKey('media.Media', on_delete=models.SET_NULL, null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)

    # Auto-calculated fields
    word_count = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=0)  # minutes

    # Analytics
    view_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['author', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
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

        super().save(*args, **kwargs)


class Page(models.Model):
    """
    Static pages (About, Now, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField()  # Markdown

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
