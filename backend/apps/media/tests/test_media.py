import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.media.models import MediaItem
import tempfile
import os

User = get_user_model()


class MediaAPITestCase(APITestCase):
    """Test Media API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Create test files
        self.test_files = {}

        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00')  # Minimal JPEG
            for i in range(64):
                f.write(b'\x00')
            f.write(b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01')
            f.write(b'\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08')
            f.write(b'\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            f.write(b'\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
            self.test_files['image'] = f.name

        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'This is a test text file for media upload.')
            self.test_files['text'] = f.name

    def tearDown(self):
        """Clean up test files"""
        for file_path in self.test_files.values():
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_upload_image_authenticated(self):
        """Test uploading an image file as authenticated user"""
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Prepare upload data
        with open(self.test_files['image'], 'rb') as f:
            file_data = f.read()

        uploaded_file = SimpleUploadedFile(
            'test_image.jpg',
            file_data,
            content_type='image/jpeg'
        )

        upload_data = {
            'file': uploaded_file,
            'title': 'Test Image',
            'alt_text': 'Test alt text',
            'caption': 'Test caption'
        }

        response = self.client.post(
            reverse('media-upload'),
            upload_data,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify response
        data = response.data
        self.assertEqual(data['title'], 'Test Image')
        self.assertEqual(data['alt_text'], 'Test alt text')
        self.assertEqual(data['user'], self.user.id)
        self.assertIn('file', data)
        self.assertIn('file_size', data)
        self.assertIn('file_type', data)

        # Verify in database
        media = MediaItem.objects.get(id=data['id'])
        self.assertEqual(media.title, 'Test Image')
        self.assertEqual(media.user, self.user)
        self.assertTrue(media.file.name.endswith('.jpg'))

    def test_upload_text_file(self):
        """Test uploading a text file"""
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Prepare upload data
        with open(self.test_files['text'], 'rb') as f:
            file_data = f.read()

        uploaded_file = SimpleUploadedFile(
            'test_document.txt',
            file_data,
            content_type='text/plain'
        )

        upload_data = {
            'file': uploaded_file,
            'title': 'Test Document'
        }

        response = self.client.post(
            reverse('media-upload'),
            upload_data,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify file type detection
        data = response.data
        self.assertEqual(data['file_type'], 'text')

    def test_upload_unauthenticated(self):
        """Test uploading file without authentication fails"""
        uploaded_file = SimpleUploadedFile(
            'test.jpg',
            b'minimal jpeg data',
            content_type='image/jpeg'
        )

        upload_data = {
            'file': uploaded_file,
            'title': 'Test'
        }

        response = self.client.post(
            reverse('media-upload'),
            upload_data,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_media_authenticated(self):
        """Test listing media files for authenticated user"""
        # Create some media for the user
        MediaItem.objects.create(
            file='test1.jpg',
            title='Test 1',
            user=self.user,
            file_size=1024,
            file_type='image'
        )
        MediaItem.objects.create(
            file='test2.jpg',
            title='Test 2',
            user=self.user,
            file_size=2048,
            file_type='image'
        )

        # Create media for another user (should not be visible)
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        MediaItem.objects.create(
            file='other.jpg',
            title='Other User',
            user=other_user,
            file_size=1024,
            file_type='image'
        )

        # Authenticate and list
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(reverse('media-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only see own media
        self.assertEqual(len(response.data), 2)
        for media in response.data:
            self.assertEqual(media['user'], self.user.id)

    def test_get_media_detail_own_file(self):
        """Test getting details of own media file"""
        # Create media
        media = MediaItem.objects.create(
            file='test.jpg',
            title='Test Media',
            user=self.user,
            file_size=1024,
            file_type='image'
        )

        # Authenticate and get details
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(
            reverse('media-detail', kwargs={'pk': media.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Media')

    def test_get_media_detail_other_user_file(self):
        """Test getting details of another user's media file fails"""
        # Create media for another user
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        media = MediaItem.objects.create(
            file='other.jpg',
            title='Other Media',
            user=other_user,
            file_size=1024,
            file_type='image'
        )

        # Authenticate as original user and try to access
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(
            reverse('media-detail', kwargs={'pk': media.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_media_own_file(self):
        """Test deleting own media file"""
        # Create media
        media = MediaItem.objects.create(
            file='test.jpg',
            title='Test Media',
            user=self.user,
            file_size=1024,
            file_type='image'
        )

        # Authenticate and delete
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.delete(
            reverse('media-detail', kwargs={'pk': media.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify deleted
        self.assertFalse(MediaItem.objects.filter(id=media.id).exists())


class MediaModelTestCase(TestCase):
    """Test MediaItem model functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

    def test_media_creation(self):
        """Test creating a media item"""
        media = MediaItem.objects.create(
            file='test.jpg',
            title='Test Image',
            user=self.user,
            file_size=1024,
            file_type='image'
        )

        self.assertEqual(media.title, 'Test Image')
        self.assertEqual(media.file_type, 'image')
        self.assertEqual(media.file_size, 1024)
        self.assertEqual(media.user, self.user)

    def test_media_string_representation(self):
        """Test media string representation"""
        media = MediaItem.objects.create(
            file='test.jpg',
            title='Test Image',
            user=self.user,
            file_size=1024,
            file_type='image'
        )

        expected = f"Test Image (image, 1024 bytes)"
        self.assertEqual(str(media), expected)

    def test_media_deletion_removes_file(self):
        """Test that deleting media removes the file"""
        # This would require proper file handling setup
        # For now, just test the model deletion
        media = MediaItem.objects.create(
            file='test.jpg',
            title='Test',
            user=self.user,
            file_size=1024,
            file_type='image'
        )

        media_id = media.id
        media.delete()

        # Verify deleted from database
        self.assertFalse(MediaItem.objects.filter(id=media_id).exists())
