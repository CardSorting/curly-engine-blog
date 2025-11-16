from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from apps.articles.models import Topic, Article, Page
from apps.users.models import User
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Create sample topics, articles, and pages for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Get or create admin user
        try:
            admin_user = User.objects.get(email='admin@example.com')
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                email='admin@example.com',
                username='admin_user',  # Unique username
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
        
        # Create sample topics
        topics_data = [
            {
                'name': 'Technology',
                'description': 'Latest in tech trends, AI, software development, and digital innovation',
                'color': '#007bff'
            },
            {
                'name': 'Business',
                'description': 'Business strategies, entrepreneurship, startups, and market insights',
                'color': '#28a745'
            },
            {
                'name': 'Design',
                'description': 'UI/UX design, graphic design, typography, and creative processes',
                'color': '#dc3545'
            },
            {
                'name': 'Productivity',
                'description': 'Time management, productivity tools, work-life balance, and personal growth',
                'color': '#ffc107'
            },
            {
                'name': 'Web Development',
                'description': 'Frontend, backend, full-stack development, and web technologies',
                'color': '#6f42c1'
            }
        ]
        
        created_topics = []
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults={
                    'description': topic_data['description'],
                    'color': topic_data['color'],
                    'slug': slugify(topic_data['name'])
                }
            )
            created_topics.append(topic)
            if created:
                self.stdout.write(f'Created topic: {topic.name}')
        
        # Create sample articles
        articles_data = [
            {
                'title': 'Getting Started with Django REST Framework',
                'content': '''# Getting Started with Django REST Framework

Django REST Framework (DRF) is a powerful and flexible toolkit for building Web APIs. In this article, we'll explore the fundamentals of DRF and how to build robust APIs.

## What is Django REST Framework?

DRF is a third-party package that extends Django's capabilities to help you build RESTful APIs. It provides features like:

- Serialization
- Authentication and permissions
- Viewsets and routers
- Pagination
- Filtering and searching

## Setting Up DRF

To get started, install DRF:

```bash
pip install djangorestframework
```

Add it to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
]
```

## Creating Your First API

Let's create a simple API for managing articles:

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
```

And the corresponding view:

```python
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

## Conclusion

Django REST Framework makes building APIs in Django incredibly straightforward. With its rich feature set and excellent documentation, you can build production-ready APIs in no time.
''',
                'topic': 'Web Development',
                'status': 'published'
            },
            {
                'title': 'The Future of Artificial Intelligence in Business',
                'content': '''# The Future of Artificial Intelligence in Business

Artificial Intelligence is no longer just a buzzword—it's transforming how businesses operate across all industries.

## Current Applications

AI is already making significant impacts in:

- Customer service with chatbots
- Predictive analytics for business intelligence
- Automated marketing campaigns
- Supply chain optimization

## Emerging Trends

Looking ahead, we can expect to see:

1. **Generative AI**: Tools like ChatGPT and DALL-E are just the beginning
2. **Edge AI**: Processing data locally on devices for faster responses
3. **Explainable AI**: Making AI decisions more transparent and understandable

## Challenges and Considerations

While AI offers tremendous potential, businesses must consider:

- Data privacy and security
- Ethical implications
- Implementation costs
- Workforce training and adaptation

## Getting Started

For businesses looking to adopt AI:

1. Start with clear business objectives
2. Identify specific problems AI can solve
3. Invest in quality data
4. Build cross-functional teams
5. Plan for continuous learning

The future of AI in business is bright, but success requires thoughtful implementation and strategic planning.
''',
                'topic': 'Technology',
                'status': 'published'
            },
            {
                'title': 'Essential Design Principles for Modern Web Apps',
                'content': '''# Essential Design Principles for Modern Web Apps

Great design isn't just about making things look pretty—it's about creating intuitive, effective user experiences.

## User-Centered Design

The foundation of good design is understanding your users:

- Conduct user research
- Create user personas
- Map user journeys
- Test with real users

## Visual Hierarchy

Guide users through your interface with clear visual hierarchy:

- Size matters: Larger elements draw more attention
- Color and contrast: Use color to highlight important elements
- Whitespace: Give elements room to breathe
- Typography: Choose fonts that enhance readability

## Consistency is Key

Maintain consistency across your application:

- Use a design system
- Standardize components
- Follow established patterns
- Document your decisions

## Mobile-First Approach

Design for mobile first, then scale up:

- Prioritize content
- Simplify navigation
- Optimize touch targets
- Consider performance

## Accessibility Matters

Design for everyone:

- Use semantic HTML
- Ensure keyboard navigation
- Provide alt text for images
- Maintain color contrast ratios

## Testing and Iteration

Great design evolves through testing:

- A/B test variations
- Gather user feedback
- Analyze usage data
- Iterate based on insights

Remember: Design is a process, not a destination. Stay curious and keep learning!
''',
                'topic': 'Design',
                'status': 'published'
            },
            {
                'title': 'Productivity Tips for Remote Developers',
                'content': '''# Productivity Tips for Remote Developers

Working remotely offers flexibility, but it also requires discipline and smart strategies to stay productive.

## Create a Dedicated Workspace

Having a separate space for work helps your brain switch into "work mode":

- Choose a quiet, comfortable location
- Invest in good equipment (chair, monitor, keyboard)
- Ensure proper lighting
- Minimize distractions

## Establish a Routine

Structure your day for maximum productivity:

- Start and end work at consistent times
- Take regular breaks
- Schedule deep work sessions
- Plan your day the night before

## Master Your Tools

Use tools that enhance your workflow:

- Communication: Slack, Teams, Zoom
- Project management: Jira, Trello, Asana
- Code collaboration: GitHub, GitLab
- Time tracking: Toggl, RescueTime

## Combat Isolation

Remote work can be lonely—stay connected:

- Virtual coffee breaks with colleagues
- Online communities and forums
- Local meetups and conferences
- Regular video calls with your team

## Health and Wellness

Take care of your physical and mental health:

- Exercise regularly
- Practice good ergonomics
- Get enough sleep
- Set boundaries between work and personal time

## Continuous Learning

Stay sharp and grow your skills:

- Online courses and tutorials
- Read technical blogs
- Join coding challenges
- Attend virtual conferences

Remember: Productivity isn't about working more—it's about working smarter. Find what works best for you and stick with it!
''',
                'topic': 'Productivity',
                'status': 'published'
            },
            {
                'title': 'Building Scalable Business Models',
                'content': '''# Building Scalable Business Models

A scalable business model is essential for long-term growth and success. Here's how to build one.

## Understanding Scalability

Scalability means your business can handle increased workload without compromising performance or revenue.

## Key Components of Scalable Models

### 1. Recurring Revenue

- Subscription models
- Maintenance contracts
- Licensing fees
- Membership programs

### 2. Low Marginal Costs

- Digital products
- Automation
- Outsourcing
- Standardized processes

### 3. Network Effects

- User-generated content
- Community building
- Referral programs
- Partnerships

## Common Scalable Business Models

### SaaS (Software as a Service)

- Predictable revenue streams
- High-profit margins
- Easy to scale globally
- Continuous improvement opportunities

### Marketplace Platforms

- Connect buyers and sellers
- Take percentage of transactions
- Network effects increase value
- Data-driven improvements

### Content Creation

- Create once, sell many times
- Multiple distribution channels
- Passive income potential
- Brand building opportunities

## Steps to Build Your Scalable Model

1. **Identify Your Value Proposition**: What problem do you solve?
2. **Research Your Market**: Understand customer needs and competition
3. **Design Your Revenue Model**: How will you make money?
4. **Build MVP**: Test your assumptions with minimal investment
5. **Iterate and Scale**: Refine based on feedback and data

## Metrics That Matter

Track these key indicators:

- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (CLV)
- Monthly Recurring Revenue (MRR)
- Churn Rate
- Net Promoter Score (NPS)

## Common Pitfalls to Avoid

- Overcomplicating your model
- Ignoring unit economics
- Failing to validate assumptions
- Not investing in technology
- Neglecting customer feedback

Building a scalable business takes time and patience, but the right model can lead to exponential growth and long-term success.
''',
                'topic': 'Business',
                'status': 'published'
            },
            {
                'title': 'Advanced Django Patterns and Best Practices',
                'content': '''# Advanced Django Patterns and Best Practices

As your Django projects grow, you need to adopt patterns that keep your code maintainable and scalable.

## Project Structure

Organize your project for maximum maintainability:

```
project/
├── apps/
│   ├── core/
│   ├── users/
│   └── articles/
├── config/
│   ├── settings/
│   └── urls.py
├── templates/
├── static/
└── requirements/
```

## Settings Management

Split settings by environment:

```python
# settings/base.py
INSTALLED_APPS = [
    # ...
]

# settings/development.py
from .base import *
DEBUG = True
ALLOWED_HOSTS = []

# settings/production.py
from .base import *
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
```

## Model Best Practices

### Use Abstract Base Classes

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Article(TimeStampedModel):
    title = models.CharField(max_length=200)
    # ...
```

### Custom Managers

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Article(models.Model):
    # ...
    objects = models.Manager()
    published = PublishedManager()
```

## Query Optimization

### Use select_related and prefetch_related

```python
# Bad: N+1 queries
articles = Article.objects.all()
for article in articles:
    print(article.author.name)

# Good: Single query
articles = Article.objects.select_related('author').all()
for article in articles:
    print(article.author.name)
```

### Bulk Operations

```python
# Bulk create
articles = [Article(title=f'Title {i}') for i in range(100)]
Article.objects.bulk_create(articles)

# Bulk update
Article.objects.filter(status='draft').update(status='published')
```

## API Design Patterns

### Use ViewSets for CRUD

```python
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```

### Custom Actions

```python
@action(detail=True, methods=['post'])
def publish(self, request, pk=None):
    article = self.get_object()
    article.status = 'published'
    article.save()
    return Response({'status': 'published'})
```

## Testing Strategies

### Factory Pattern for Tests

```python
import factory
from .models import Article

class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
    
    title = factory.Faker('sentence')
    content = factory.Faker('text')
    status = 'published'
```

### Integration Tests

```python
class ArticleAPITestCase(APITestCase):
    def test_create_article(self):
        data = {'title': 'Test', 'content': 'Content'}
        response = self.client.post('/api/articles/', data)
        self.assertEqual(response.status_code, 201)
```

## Performance Optimization

### Caching Strategies

```python
from django.core.cache import cache

def get_popular_articles():
    cache_key = 'popular_articles'
    articles = cache.get(cache_key)
    if articles is None:
        articles = Article.objects.order_by('-views')[:10]
        cache.set(cache_key, articles, 300)  # 5 minutes
    return articles
```

### Database Indexing

```python
class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    published_at = models.DateTimeField(db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['title', 'published_at']),
        ]
```

## Security Best Practices

- Use environment variables for sensitive data
- Implement proper authentication and authorization
- Validate all user input
- Use HTTPS in production
- Keep dependencies updated

## Deployment Considerations

- Use Docker for containerization
- Implement CI/CD pipelines
- Monitor application performance
- Set up proper logging
- Plan for scaling

Following these patterns will help you build robust, maintainable Django applications that can grow with your needs.
''',
                'topic': 'Web Development',
                'status': 'draft'
            }
        ]
        
        created_articles = []
        for article_data in articles_data:
            topic = next((t for t in created_topics if t.name == article_data['topic']), None)
            
            # Generate random published date for published articles
            published_at = None
            if article_data['status'] == 'published':
                days_ago = random.randint(1, 30)
                published_at = timezone.now() - timedelta(days=days_ago)
            
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    'content': article_data['content'],
                    'topic': topic,
                    'author': admin_user,
                    'status': article_data['status'],
                    'published_at': published_at,
                    'slug': slugify(article_data['title'])
                }
            )
            created_articles.append(article)
            if created:
                self.stdout.write(f'Created article: {article.title}')
        
        # Create sample pages
        pages_data = [
            {
                'title': 'About Us',
                'content': '''# About Our Blog

Welcome to our blog! We're passionate about sharing knowledge and insights on technology, business, design, and productivity.

## Our Mission

Our mission is to provide high-quality, practical content that helps developers, designers, and entrepreneurs grow their skills and achieve their goals.

## What We Cover

- **Technology**: Latest trends in software development, AI, and digital innovation
- **Business**: Strategies for startups, entrepreneurship, and market insights
- **Design**: UI/UX principles, graphic design, and creative processes
- **Productivity**: Time management, tools, and personal development

## Our Team

We're a team of experienced writers and practitioners who are passionate about our respective fields. Each article is crafted with care and based on real-world experience.

## Get in Touch

Have questions or suggestions? We'd love to hear from you. Reach out to us at [contact@ourblog.com](mailto:contact@ourblog.com).

Thank you for being part of our community!
''',
                'is_published': True
            },
            {
                'title': 'Contact',
                'content': '''# Get in Touch

We love hearing from our readers! Whether you have questions, feedback, or ideas for future articles, don't hesitate to reach out.

## Ways to Connect

### Email
Drop us a line at [contact@ourblog.com](mailto:contact@ourblog.com)

### Social Media
- Twitter: [@ourblog](https://twitter.com/ourblog)
- LinkedIn: [Our Blog](https://linkedin.com/company/ourblog)
- GitHub: [ourblog-org](https://github.com/ourblog-org)

### Newsletter
Subscribe to our newsletter for the latest articles and exclusive content delivered straight to your inbox.

## Guest Posts

Interested in writing for us? We're always looking for fresh perspectives! Check out our [guest post guidelines](/guest-guidelines) for more information.

## Business Inquiries

For partnerships, advertising, or other business opportunities, please email [business@ourblog.com](mailto:business@ourblog.com).

We typically respond within 24-48 hours. Looking forward to hearing from you!
''',
                'is_published': True
            },
            {
                'title': 'Privacy Policy',
                'content': '''# Privacy Policy

Your privacy is important to us. This policy explains how we collect, use, and protect your information.

## Information We Collect

### Personal Information
- Email addresses (for newsletter subscriptions)
- Names (when provided voluntarily)
- Usage data through analytics

### Automatically Collected Data
- IP addresses
- Browser information
- Access times and pages viewed

## How We Use Your Information

- To send newsletter content you've subscribed to
- To improve our website and content
- To analyze usage patterns
- To respond to your inquiries

## Data Protection

We use industry-standard security measures to protect your information. Email addresses are stored securely and never shared with third parties without your consent.

## Cookies

Our website uses cookies to enhance your experience. You can disable cookies in your browser settings.

## Third-Party Services

We use:
- Email service providers for newsletter delivery
- Analytics services to understand our audience
- Social media platforms for content sharing

## Your Rights

You have the right to:
- Access your personal data
- Correct inaccurate information
- Delete your account and data
- Unsubscribe from newsletters

## Contact Us

If you have questions about this privacy policy, contact us at [privacy@ourblog.com](mailto:privacy@ourblog.com).

Last updated: November 2024
''',
                'is_published': True
            }
        ]
        
        for page_data in pages_data:
            page, created = Page.objects.get_or_create(
                title=page_data['title'],
                defaults={
                    'content': page_data['content'],
                    'slug': slugify(page_data['title'])
                }
            )
            if created:
                self.stdout.write(f'Created page: {page.title}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(f'Created {len(created_topics)} topics')
        self.stdout.write(f'Created {len(created_articles)} articles')
        self.stdout.write(f'Created {len(pages_data)} pages')
