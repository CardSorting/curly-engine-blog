from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.articles.models import Article, Topic
from apps.users.models import User


class Command(BaseCommand):
    help = 'Create sample articles and topics for testing'

    def handle(self, *args, **options):
        # Create sample topics
        topics_data = [
            {'name': 'Technology', 'description': 'Tech articles and tutorials', 'color': '#0066FF'},
            {'name': 'Writing', 'description': 'Writing tips and techniques', 'color': '#FF6600'},
            {'name': 'Productivity', 'description': 'Productivity hacks and tools', 'color': '#00AA44'},
        ]
        
        created_topics = []
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults=topic_data
            )
            if created:
                self.stdout.write(f'Created topic: {topic.name}')
            created_topics.append(topic)

        # Create a sample user if needed
        user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write('Created sample user: admin@example.com')

        # Create sample articles
        articles_data = [
            {
                'title': 'Getting Started with Vue 3',
                'content': '''Vue 3 is the latest version of the popular JavaScript framework. 
                It brings many improvements over Vue 2, including better performance, 
                smaller bundle sizes, and improved TypeScript support.''',
                'topic': created_topics[0],
            },
            {
                'title': 'The Art of Technical Writing',
                'content': '''Technical writing is a skill that combines clear communication 
                with technical expertise. Good technical writing helps users understand 
                complex concepts and procedures.''',
                'topic': created_topics[1],
            },
            {
                'title': '10 Productivity Tips for Developers',
                'content': '''As developers, we're always looking for ways to be more productive. 
                Here are 10 tips that can help you write better code faster.''',
                'topic': created_topics[2],
            },
        ]

        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                author=user,
                defaults={
                    **article_data,
                    'status': 'published',
                    'published_at': timezone.now(),
                }
            )
            if created:
                self.stdout.write(f'Created article: {article.title}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
