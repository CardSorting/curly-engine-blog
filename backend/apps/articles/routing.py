from django.urls import re_path
from .consumers import CollaborativeEditingConsumer

websocket_urlpatterns = [
    # Collaborative editing WebSocket endpoint
    # URL pattern: ws://host/articles/{article_id}/collaborate/
    re_path(r'ws/articles/(?P<article_id>[^/]+)/collaborate/$', CollaborativeEditingConsumer.as_asgi()),
]
