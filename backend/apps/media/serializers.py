from rest_framework import serializers
from .models import Media


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for media files"""
    file_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model = Media
        fields = [
            'id', 'file', 'file_url', 'filename', 'alt_text',
            'width', 'height', 'file_size', 'mime_type',
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'file_url', 'width', 'height', 'file_size',
            'mime_type', 'uploaded_by', 'uploaded_by_name', 'created_at'
        ]

    def get_file_url(self, obj):
        """Return the full URL to the media file"""
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            url = obj.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class MediaUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading media files"""

    class Meta:
        model = Media
        fields = ['file', 'alt_text']

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user

        # Set mime type from uploaded file
        file_obj = validated_data['file']
        validated_data['mime_type'] = file_obj.content_type or 'application/octet-stream'

        return super().create(validated_data)
