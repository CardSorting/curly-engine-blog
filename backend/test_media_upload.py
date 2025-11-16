#!/usr/bin/env python3
"""
Test script for media upload functionality
"""
import requests
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api/media"

def test_media_upload():
    """Test uploading a media file"""
    
    # Create a test image file
    test_image_path = "test_image.jpg"
    
    # Create a simple test image (1x1 pixel JPEG)
    # For a real test, you would use an actual image file
    if not os.path.exists(test_image_path):
        # Create a minimal JPEG file for testing
        with open(test_image_path, 'wb') as f:
            # Minimal JPEG header
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00')
            for i in range(64):
                f.write(b'\x00')
            f.write(b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
    
    # Test upload
    upload_url = f"{BASE_URL}/upload/"
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': (test_image_path, f, 'image/jpeg')}
            data = {
                'title': 'Test Image',
                'alt_text': 'A test image for upload testing',
                'caption': 'This is a test image uploaded via API'
            }
            
            response = requests.post(upload_url, files=files, data=data)
            
            print(f"Upload Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"Upload successful! Media ID: {result.get('id')}")
                return result.get('id')
            else:
                print(f"Upload failed: {response.text}")
                return None
                
    except Exception as e:
        print(f"Error during upload: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_media_list():
    """Test listing media files"""
    list_url = f"{BASE_URL}/"
    
    try:
        response = requests.get(list_url)
        print(f"\nList Status: {response.status_code}")
        
        if response.status_code == 200:
            media_list = response.json()
            print(f"Found {len(media_list)} media files:")
            for media in media_list:
                print(f"  - {media['title']} ({media['file_type']})")
        else:
            print(f"List failed: {response.text}")
            
    except Exception as e:
        print(f"Error during list: {e}")

def test_media_detail(media_id):
    """Test getting media details"""
    if not media_id:
        print("No media ID to test")
        return
        
    detail_url = f"{BASE_URL}/{media_id}/"
    
    try:
        response = requests.get(detail_url)
        print(f"\nDetail Status: {response.status_code}")
        
        if response.status_code == 200:
            media = response.json()
            print(f"Media Details:")
            print(f"  Title: {media['title']}")
            print(f"  Type: {media['file_type']}")
            print(f"  Size: {media['file_size']} bytes")
            print(f"  URL: {media['file']}")
        else:
            print(f"Detail failed: {response.text}")
            
    except Exception as e:
        print(f"Error during detail: {e}")

if __name__ == "__main__":
    print("Testing Media Upload API...")
    print("Make sure the Django server is running on localhost:8000")
    
    # Test upload
    media_id = test_media_upload()
    
    # Test list
    test_media_list()
    
    # Test detail
    test_media_detail(media_id)
    
    print("\nTesting completed!")
