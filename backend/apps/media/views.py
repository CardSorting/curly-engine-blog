from rest_framework import generics, permissions, status, parsers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Media
from .serializers import MediaSerializer, MediaUploadSerializer


class MediaListView(generics.ListAPIView):
    """List media files for authenticated users"""
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['mime_type', 'uploaded_by']
    search_fields = ['filename', 'alt_text']
    ordering = ['-created_at']

    def get_queryset(self):
        # Users can only see their own uploads, unless staff
        if self.request.user.is_staff:
            return Media.objects.all()
        return Media.objects.filter(uploaded_by=self.request.user)


class MediaDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a media file"""
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Users can only access their own uploads, unless staff
        if self.request.user.is_staff:
            return Media.objects.all()
        return Media.objects.filter(uploaded_by=self.request.user)


class MediaUploadView(generics.CreateAPIView):
    """Upload a new media file"""
    serializer_class = MediaUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def media_stats(request):
    """Get media upload statistics for current user"""
    queryset = Media.objects.filter(uploaded_by=request.user)

    if request.user.is_staff:
        queryset = Media.objects.all()

    stats = {
        'total_files': queryset.count(),
        'total_size': sum(media.file_size for media in queryset),
        'images': queryset.filter(mime_type__startswith='image/').count(),
        'other_files': queryset.exclude(mime_type__startswith='image/').count(),
    }

    return Response(stats)
