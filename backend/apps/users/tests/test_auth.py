import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserAuthTestCase(APITestCase):
    """Test user authentication endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client = self.client_class()

    def test_user_registration(self):
        """Test user registration endpoint"""
        register_data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(reverse('register'), register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Verify user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_staff)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email fails"""
        register_data = {
            'email': 'test@example.com',  # Same as existing user
            'password': 'newpass123',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }

        response = self.client.post(reverse('register'), register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login(self):
        """Test user login endpoint"""
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(reverse('token_obtain_pair'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials fails"""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(reverse('token_obtain_pair'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh endpoint"""
        # First get tokens
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('token_obtain_pair'), login_data, format='json')
        refresh_token = response.data['refresh']

        # Then refresh
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(reverse('token_refresh'), refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_current_user_authenticated(self):
        """Test getting current user info when authenticated"""
        # Authenticate client
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')

    def test_get_current_user_unauthenticated(self):
        """Test getting current user info when not authenticated"""
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_update(self):
        """Test updating user profile"""
        # Authenticate client
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }

        response = self.client.patch(reverse('profile'), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        self.assertEqual(response.data['bio'], 'Updated bio')

        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.bio, 'Updated bio')


class UserModelTestCase(TestCase):
    """Test User model functionality"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'email': 'modeltest@example.com',
            'password': 'testpass123',
            'first_name': 'Model',
            'last_name': 'Test',
            'bio': 'Test bio'
        }

    def test_user_creation(self):
        """Test creating a user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'modeltest@example.com')
        self.assertEqual(user.first_name, 'Model')
        self.assertEqual(user.last_name, 'Test')
        self.assertEqual(user.bio, 'Test bio')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.first_name} {user.last_name} ({user.email})"
        self.assertEqual(str(user), expected)

    def test_superuser_creation(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            email='super@example.com',
            password='superpass123',
            first_name='Super',
            last_name='User'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_email_uniqueness(self):
        """Test email uniqueness constraint"""
        User.objects.create_user(**self.user_data)

        with self.assertRaises(Exception):
            User.objects.create_user(
                email='modeltest@example.com',  # Same email
                password='differentpass',
                first_name='Different',
                last_name='User'
            )
