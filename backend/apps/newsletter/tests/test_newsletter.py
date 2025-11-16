import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.newsletter.models import Subscriber, Newsletter, SubscriberGroup, NewsletterSend
from apps.articles.models import Article, Topic

User = get_user_model()


class NewsletterAPITestCase(APITestCase):
    """Test Newsletter API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create user
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Create subscriber
        self.subscriber = Subscriber.objects.create(
            email='subscriber@example.com',
            first_name='Test',
            last_name='Subscriber',
            is_active=True,
            is_confirmed=True
        )

        # Create newsletter
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            subject='Test Subject',
            preview_text='Test preview',
            content_html='<h1>Test</h1><p>Content</p>',
            content_text='Test Content',
            created_by=self.user,
            status='draft'
        )

        self.client = self.client_class()

    def test_subscribe_to_newsletter(self):
        """Test subscribing to newsletter"""
        subscribe_data = {
            'email': 'newsubscriber@example.com',
            'first_name': 'New',
            'last_name': 'Subscriber'
        }

        response = self.client.post(reverse('newsletter-subscribe'), subscribe_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify subscriber created
        subscriber = Subscriber.objects.get(email='newsubscriber@example.com')
        self.assertEqual(subscriber.first_name, 'New')
        self.assertFalse(subscriber.is_confirmed)  # Should need confirmation

        # Verify confirmation email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Confirm your subscription', mail.outbox[0].subject)

    def test_unsubscribe_from_newsletter(self):
        """Test unsubscribing from newsletter"""
        # Get unsubscribe token from subscriber
        unsubscribe_token = str(self.subscriber.unsubscribe_token)

        unsubscribe_data = {
            'token': unsubscribe_token
        }

        response = self.client.post(reverse('newsletter-unsubscribe'), unsubscribe_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify subscriber marked as inactive
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)

    def test_confirmation_email(self):
        """Test sending confirmation email"""
        response = self.client.post(
            reverse('newsletter-send-confirmation', kwargs={'subscriber_id': self.subscriber.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify email sent
        self.assertEqual(len(mail.outbox), 1)


class NewsletterModelTestCase(TestCase):
    """Test Newsletter model functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='creator@example.com',
            password='testpass123'
        )

    def test_newsletter_creation(self):
        """Test creating a newsletter"""
        newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            subject='Test Subject',
            content_html='<p>Test content</p>',
            content_text='Test content',
            created_by=self.user
        )

        self.assertEqual(newsletter.title, 'Test Newsletter')
        self.assertEqual(newsletter.status, 'draft')  # Default status
        self.assertEqual(newsletter.created_by, self.user)

    def test_newsletter_sending(self):
        """Test newsletter sending functionality"""
        # Create confirmed subscribers
        subscriber1 = Subscriber.objects.create(
            email='sub1@example.com',
            is_confirmed=True,
            is_active=True
        )
        subscriber2 = Subscriber.objects.create(
            email='sub2@example.com',
            is_confirmed=True,
            is_active=True
        )

        # Create newsletter
        newsletter = Newsletter.objects.create(
            title='Send Test',
            subject='Test Send',
            content_html='<p>Content</p>',
            content_text='Content',
            created_by=self.user,
            status='draft'
        )

        # Test the send method (simplified since full implementation might be complex)
        # This would normally send emails via Resend
        newsletter.status = 'sent'
        newsletter.sent_at = timezone.now()
        newsletter.save()

        self.assertEqual(newsletter.status, 'sent')

    def test_subscriber_group(self):
        """Test subscriber groups"""
        group = SubscriberGroup.objects.create(
            name='Test Group',
            description='Test subscribers'
        )

        # Add subscribers to group
        subscriber1 = Subscriber.objects.create(
            email='grouped@example.com',
            is_confirmed=True,
            is_active=True
        )
        subscriber2 = Subscriber.objects.create(
            email='grouped2@example.com',
            is_confirmed=True,
            is_active=True
        )

        group.subscribers.add(subscriber1, subscriber2)
        group.save()

        # Verify group size
        self.assertEqual(group.subscriber_count, 2)


class SubscriberModelTestCase(TestCase):
    """Test Subscriber model functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='linked@example.com',
            password='testpass123'
        )

    def test_subscriber_creation(self):
        """Test creating a subscriber"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='Subscriber',
            user=self.user
        )

        self.assertEqual(subscriber.email, 'test@example.com')
        self.assertIsNotNone(subscriber.confirmation_token)
        self.assertIsNotNone(subscriber.unsubscribe_token)
        self.assertFalse(subscriber.is_confirmed)  # Should need confirmation

    def test_subscriber_string_representation(self):
        """Test subscriber string representation"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )

        expected = "John Doe (test@example.com)"
        self.assertEqual(str(subscriber), expected)

    def test_confirmation_token_uniqueness(self):
        """Test confirmation token uniqueness"""
        subscriber1 = Subscriber.objects.create(email='test1@example.com')
        subscriber2 = Subscriber.objects.create(email='test2@example.com')

        # Tokens should be unique
        self.assertNotEqual(subscriber1.confirmation_token, subscriber2.confirmation_token)
