import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.articles.models import Article, Topic, Page
from decimal import Decimal

User = get_user_model()


class ArticleAPITestCase(APITestCase):
    """Test Article API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.user = User.objects.create_user(
            email='author@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Author'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )

        # Create topic
        self.topic = Topic.objects.create(
            name='Technology',
            slug='technology',
            description='Tech articles',
            color='#007acc'
        )

        # Create articles
        self.published_article = Article.objects.create(
            title='Published Article',
            slug='published-article',
            excerpt='This is a published article',
            content='# Published Content\n\nThis is the full content.',
            status='published',
            author=self.user,
            topic=self.topic,
            word_count=50,
            reading_time=3
        )

        self.draft_article = Article.objects.create(
            title='Draft Article',
            slug='draft-article',
            excerpt='This is a draft article',
            content='Draft content',
            status='draft',
            author=self.user,
            topic=self.topic
        )

        # Create page
        self.page = Page.objects.create(
            title='About Us',
            slug='about',
            content='About our company',
            author=self.user
        )

        self.client = self.client_class()

    def test_list_articles_unauthenticated(self):
        """Test listing articles without authentication"""
        response = self.client.get(reverse('article-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only published
        self.assertEqual(response.data['results'][0]['title'], 'Published Article')

    def test_list_articles_authenticated(self):
        """Test listing articles as authenticated user"""
        # Authenticate as author
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(reverse('article-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see both published and draft (own articles)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_get_published_article_detail(self):
        """Test getting published article detail"""
        response = self.client.get(
            reverse('article-detail', kwargs={'slug': 'published-article'})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Published Article')
        self.assertEqual(response.data['status'], 'published')

    def test_create_article_authenticated(self):
        """Test creating article as authenticated user"""
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        article_data = {
            'title': 'New Article',
            'excerpt': 'New article excerpt',
            'content': 'New article content',
            'status': 'draft',
            'topic': self.topic.id
        }

        response = self.client.post(reverse('article-list'), article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Article')
        self.assertEqual(response.data['status'], 'draft')

        # Verify in database
        article = Article.objects.get(slug__startswith='new-article')
        self.assertEqual(article.author, self.user)

    def test_update_own_article(self):
        """Test updating own article"""
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        update_data = {
            'title': 'Updated Title',
            'excerpt': 'Updated excerpt'
        }

        response = self.client.patch(
            reverse('article-detail', kwargs={'slug': 'draft-article'}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_publish_article_admin(self):
        """Test publishing article as admin"""
        # Authenticate as admin
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.patch(
            reverse('article-publish', kwargs={'slug': 'draft-article'}),
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify published
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.status, 'published')
        self.assertIsNotNone(self.draft_article.published_at)

    def test_delete_article_admin(self):
        """Test deleting article as admin"""
        # Authenticate as admin
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.delete(
            reverse('article-detail', kwargs={'slug': 'draft-article'})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify deleted
        with self.assertRaises(Article.DoesNotExist):
            Article.objects.get(slug='draft-article')


class TopicAPITestCase(APITestCase):
    """Test Topic API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.topic1 = Topic.objects.create(
            name='Technology',
            slug='technology',
            description='Tech articles',
            color='#007acc'
        )
        self.topic2 = Topic.objects.create(
            name='Business',
            slug='business',
            description='Business articles',
            color='#28a745'
        )

    def test_list_topics(self):
        """Test listing topics"""
        response = self.client.get(reverse('topic-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_topic_detail(self):
        """Test getting topic detail"""
        response = self.client.get(
            reverse('topic-detail', kwargs={'slug': 'technology'})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology')

    def test_get_topic_articles(self):
        """Test getting articles for a topic"""
        # Create an article in the topic
        user = User.objects.create_user(
            email='author@example.com',
            password='testpass123'
        )
        Article.objects.create(
            title='Tech Article',
            slug='tech-article',
            content='Content',
            status='published',
            author=user,
            topic=self.topic1
        )

        response = self.client.get(
            reverse('topic-articles', kwargs={'slug': 'technology'})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class PageAPITestCase(APITestCase):
    """Test Page API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='author@example.com',
            password='testpass123'
        )
        self.page = Page.objects.create(
            title='About Us',
            slug='about',
            content='About content',
            author=self.user
        )

    def test_list_pages(self):
        """Test listing pages"""
        response = self.client.get(reverse('page-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_page_detail(self):
        """Test getting page detail"""
        response = self.client.get(
            reverse('page-detail', kwargs={'slug': 'about'})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'About Us')


class ArticleModelTestCase(TestCase):
    """Test Article model functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='author@example.com',
            password='testpass123'
        )
        self.topic = Topic.objects.create(
            name='Test Topic',
            slug='test-topic'
        )

    def test_article_creation(self):
        """Test creating an article"""
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article content.',
            author=self.user,
            topic=self.topic
        )

        # Check auto-generated fields
        self.assertIsNotNone(article.slug)
        self.assertGreater(article.word_count, 0)
        self.assertGreater(article.reading_time, 0)

    def test_article_slug_uniqueness(self):
        """Test slug uniqueness within same publish date"""
        article1 = Article.objects.create(
            title='Test Article',
            content='Content 1',
            author=self.user,
            topic=self.topic,
            status='published'
        )

        article2 = Article.objects.create(
            title='Test Article',
            content='Content 2',
            author=self.user,
            topic=self.topic,
            status='published'
        )

        # Should have different slugs
        self.assertNotEqual(article1.slug, article2.slug)

    def test_article_string_representation(self):
        """Test article string representation"""
        article = Article.objects.create(
            title='Test Title',
            content='Test content',
            author=self.user,
            topic=self.topic
        )
        self.assertEqual(str(article), 'Test Title')
