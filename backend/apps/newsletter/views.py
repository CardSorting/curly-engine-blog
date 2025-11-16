import uuid
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Subscriber, Newsletter, SubscriberGroup, NewsletterSend
from .serializers import (
    SubscriberSerializer, NewsletterSerializer, SubscriberGroupSerializer,
    NewsletterSendSerializer, NewsletterSubscriptionSerializer
)


class SubscriberViewSet(viewsets.ModelViewSet):
    """API endpoint for managing newsletter subscribers"""
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_confirmed']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def subscribe(self, request):
        """Subscribe to newsletter with double opt-in"""
        serializer = NewsletterSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            first_name = serializer.validated_data.get('first_name', '')
            last_name = serializer.validated_data.get('last_name', '')
            
            # Check if subscriber already exists
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            
            if not created and subscriber.is_confirmed:
                return Response(
                    {'detail': 'Email is already subscribed and confirmed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Send confirmation email
            try:
                subscriber.send_confirmation_email()
                return Response({
                    'detail': 'Confirmation email sent. Please check your inbox.',
                    'subscriber_id': str(subscriber.id)
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'detail': f'Error sending confirmation email: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def confirm(self, request):
        """Confirm subscription via token"""
        token = request.data.get('token')
        if not token:
            return Response(
                {'detail': 'Confirmation token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscriber = get_object_or_404(Subscriber, confirmation_token=token)
            if subscriber.is_confirmed:
                return Response(
                    {'detail': 'Subscription already confirmed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscriber.confirm_subscription()
            return Response({
                'detail': 'Subscription confirmed successfully!',
                'subscriber': SubscriberSerializer(subscriber).data
            })
        except Exception as e:
            return Response(
                {'detail': f'Error confirming subscription: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def unsubscribe(self, request):
        """Unsubscribe via token"""
        token = request.data.get('token')
        if not token:
            return Response(
                {'detail': 'Unsubscribe token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
            subscriber.unsubscribe()
            return Response({
                'detail': 'Successfully unsubscribed from newsletter.'
            })
        except Exception as e:
            return Response(
                {'detail': f'Error unsubscribing: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NewsletterViewSet(viewsets.ModelViewSet):
    """API endpoint for managing newsletters"""
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['title', 'subject']
    ordering_fields = ['created_at', 'scheduled_at', 'sent_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send newsletter to subscribers"""
        newsletter = self.get_object()
        
        if newsletter.status != 'draft':
            return Response(
                {'detail': 'Only draft newsletters can be sent.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            newsletter.send_newsletter()
            return Response({
                'detail': f'Newsletter sent to {newsletter.total_sent} subscribers.',
                'newsletter': NewsletterSerializer(newsletter).data
            })
        except Exception as e:
            return Response(
                {'detail': f'Error sending newsletter: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a newsletter"""
        newsletter = self.get_object()
        
        new_newsletter = Newsletter.objects.create(
            title=f'{newsletter.title} (Copy)',
            subject=newsletter.subject,
            preview_text=newsletter.preview_text,
            content_html=newsletter.content_html,
            content_text=newsletter.content_text,
            created_by=request.user,
            target_all_subscribers=newsletter.target_all_subscribers,
        )
        new_newsletter.target_groups.set(newsletter.target_groups.all())
        
        return Response({
            'detail': 'Newsletter duplicated successfully.',
            'newsletter': NewsletterSerializer(new_newsletter).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview newsletter content"""
        newsletter = self.get_object()
        return Response({
            'html': newsletter.content_html,
            'text': newsletter.content_text,
            'subject': newsletter.subject,
            'preview_text': newsletter.preview_text
        })


class SubscriberGroupViewSet(viewsets.ModelViewSet):
    """API endpoint for managing subscriber groups"""
    queryset = SubscriberGroup.objects.all()
    serializer_class = SubscriberGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class NewsletterSendViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing newsletter sends"""
    queryset = NewsletterSend.objects.all()
    serializer_class = NewsletterSendSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['newsletter', 'subscriber', 'status']
    ordering_fields = ['created_at', 'sent_at', 'opened_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related('newsletter', 'subscriber')


class TrackingView(APIView):
    """Handle email tracking (opens and clicks)"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, tracking_type, token):
        """Handle tracking pixel or click tracking"""
        if tracking_type == 'open':
            try:
                send_record = get_object_or_404(NewsletterSend, open_token=token)
                if send_record.status != 'opened':
                    send_record.status = 'opened'
                    send_record.opened_at = timezone.now()
                    send_record.save()
                    
                    # Update newsletter metrics
                    newsletter = send_record.newsletter
                    newsletter.total_opened += 1
                    newsletter.save()
                
                # Return 1x1 transparent pixel
                from django.http import HttpResponse
                response = HttpResponse(content_type='image/png')
                response.content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82'
                return response
                
            except Exception as e:
                return Response({'detail': 'Invalid tracking token'}, status=status.HTTP_404_NOT_FOUND)
        
        elif tracking_type == 'click':
            try:
                send_record = get_object_or_404(NewsletterSend, click_token=token)
                if send_record.status != 'clicked':
                    send_record.status = 'clicked'
                    send_record.clicked_at = timezone.now()
                    send_record.save()
                    
                    # Update newsletter metrics
                    newsletter = send_record.newsletter
                    newsletter.total_clicked += 1
                    newsletter.save()
                
                # Redirect to the URL specified in query params or home
                redirect_url = request.GET.get('url', '/')
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect(redirect_url)
                
            except Exception as e:
                return Response({'detail': 'Invalid tracking token'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'detail': 'Invalid tracking type'}, status=status.HTTP_400_BAD_REQUEST)
