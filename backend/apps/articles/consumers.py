import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied
from .models import (
    Article, CollaborativeSession, SessionParticipant,
    OperationTransform
)
from .utils import OperationalTransform

logger = logging.getLogger(__name__)


class CollaborativeEditingConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time collaborative editing
    Handles operational transformations, user presence, and conflict resolution
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article_id = None
        self.article = None
        self.session = None
        self.participant = None
        self.user = None
        self.ot = OperationalTransform()

    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Get article ID from URL
            self.article_id = self.scope['url_route']['kwargs']['article_id']

            # Extract user from scope (set by AuthMiddlewareStack)
            self.user = self.scope.get('user')
            if not self.user or not self.user.is_authenticated:
                await self.close(code=4003)  # Close with "try again later" code
                return

            # Check permissions and setup session
            await self._setup_session()

            # Accept connection
            await self.accept()

            # Send initial state and join session
            await self._send_initial_state()
            await self._broadcast_user_joined()

        except PermissionDenied:
            await self.close(code=4003)
        except Exception as e:
            logger.error(f"Error connecting to collaborative session: {e}")
            await self.close(code=1011)  # Internal error

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if self.participant:
                await self._update_participant_status('disconnected')
                await self._broadcast_user_left()
        except Exception as e:
            logger.error(f"Error handling disconnect: {e}")

    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        try:
            message_type = content.get('type')

            handler_map = {
                'operation': self._handle_operation,
                'cursor_update': self._handle_cursor_update,
                'ping': self._handle_ping,
                'save_request': self._handle_save_request,
                'session_info': self._handle_session_info_request,
            }

            handler = handler_map.get(message_type)
            if handler:
                await handler(content)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_json({
                'type': 'error',
                'message': 'Failed to process message'
            })

    async def _setup_session(self):
        """Setup collaborative session for the user"""
        # Get article
        self.article = await self._get_article()

        # Check if user can edit this article
        await self._check_edit_permissions()

        # Get or create collaborative session
        self.session = await self._get_or_create_session()

        # Add user as participant
        self.participant = await self._add_participant()

    async def _send_initial_state(self):
        """Send initial session state to newly connected user"""
        # Get active participants
        participants = await self._get_active_participants()

        # Get recent operations
        operations = await self._get_recent_operations()

        # Send initial state
        await self.send_json({
            'type': 'initial_state',
            'session': {
                'id': str(self.session.id),
                'name': self.session.session_name,
                'status': self.session.status,
                'is_locked': self.session.is_locked,
                'max_participants': self.session.max_participants,
                'current_content': self.session.current_content,
                'current_title': self.session.current_title,
                'base_version': self.session.base_version,
                'operation_sequence': self.session.operation_sequence,
            },
            'article': {
                'id': str(self.article.id),
                'title': self.article.title,
                'content': self.article.content,
            },
            'participants': participants,
            'recent_operations': operations,
            'your_participant_id': str(self.participant.id),
        })

    async def _handle_operation(self, content):
        """Handle operational transform"""
        try:
            operation_data = content.get('operation', {})
            sequence_number = content.get('sequence_number')
            client_id = content.get('client_id', f"user_{self.user.id}")

            # Apply operation to session
            result = await self._apply_operation(operation_data, sequence_number)

            # Broadcast operation to other participants
            await self._broadcast_operation(result, exclude_channel=self.channel_name)

            # Send acknowledgment
            await self.send_json({
                'type': 'operation_ack',
                'sequence_number': result['sequence_number'],
                'applied_at': result['applied_at']
            })

        except ValueError as e:
            await self.send_json({
                'type': 'operation_rejected',
                'reason': str(e)
            })

    async def _handle_cursor_update(self, content):
        """Handle cursor position updates"""
        cursor_data = content.get('cursor', {})
        position = cursor_data.get('position', 0)
        selection_start = cursor_data.get('selection_start', 0)
        selection_end = cursor_data.get('selection_end', 0)

        # Update participant cursor position
        await self._update_cursor_position(position, selection_start, selection_end)

        # Broadcast cursor update to other participants
        await self._broadcast_cursor_update()

    async def _handle_ping(self, content):
        """Handle ping messages to keep connection alive"""
        await self._update_participant_activity()

        # Send pong response
        await self.send_json({
            'type': 'pong',
            'timestamp': content.get('timestamp')
        })

    async def _handle_save_request(self, content):
        """Handle manual save request"""
        try:
            await self._save_session_to_article()
            await self.send_json({
                'type': 'save_success',
                'message': 'Session saved successfully'
            })
        except Exception as e:
            await self.send_json({
                'type': 'save_error',
                'message': str(e)
            })

    async def _handle_session_info_request(self, content):
        """Handle request for current session info"""
        participants = await self._get_active_participants()
        session_info = await self._get_session_info()

        await self.send_json({
            'type': 'session_info',
            'session': session_info,
            'participants': participants
        })

    # Database operations (synchronous)
    @database_sync_to_async
    def _get_article(self):
        """Get article by ID"""
        try:
            return Article.objects.get(id=self.article_id)
        except Article.DoesNotExist:
            raise PermissionDenied("Article not found")

    @database_sync_to_async
    def _check_edit_permissions(self):
        """Check if user can edit this article"""
        if not self.article.can_be_edited_by(self.user):
            raise PermissionDenied("You don't have permission to edit this article")

    @database_sync_to_async
    def _get_or_create_session(self):
        """Get existing session or create new one"""
        session, created = CollaborativeSession.objects.get_or_create(
            article=self.article,
            status='active',
            defaults={
                'session_name': f"Collaborative editing: {self.article.title}",
                'current_content': self.article.content,
                'current_title': self.article.title,
                'created_by': self.user,
            }
        )
        return session

    @database_sync_to_async
    def _add_participant(self):
        """Add user as session participant"""
        return self.session.add_participant(self.user)

    @database_sync_to_async
    def _get_active_participants(self):
        """Get active participants with their status"""
        participants = []
        for participant in self.session.participants.filter(
            sessionparticipant__status='active'
        ).prefetch_related('sessionparticipant'):
            participant_data = participant.sessionparticipant_set.first()
            if participant_data and participant_data.is_active:
                participants.append({
                    'id': str(participant_data.id),
                    'user_id': str(participant.id),
                    'username': participant.username,
                    'full_name': participant.get_full_name() or participant.username,
                    'cursor_position': participant_data.cursor_position,
                    'selection_start': participant_data.selection_start,
                    'selection_end': participant_data.selection_end,
                    'user_color': participant_data.user_color,
                    'last_activity': participant_data.last_activity.isoformat(),
                })
        return participants

    @database_sync_to_async
    def _get_recent_operations(self, limit=50):
        """Get recent operations for this session"""
        operations = list(self.session.operations.order_by('-sequence')[:limit])
        return operations[::-1]  # Return in chronological order

    @database_sync_to_async
    def _apply_operation(self, operation_data, sequence_number, client_version=None):
        """Apply operation to session with proper OT transformation and validation"""
        try:
            # Validate operation first
            current_content = self.session.current_content or ""
            if not self.ot.validate_operation(operation_data, len(current_content)):
                raise ValueError(f"Invalid operation: {operation_data}")

            # Apply the operation to the session
            result = self.session.apply_operation(operation_data, self.user, sequence_number)

            logger.info(f"Applied operation seq {sequence_number} by {self.user.username}: {operation_data.get('type')}")
            return result

        except Exception as e:
            logger.error(f"Failed to apply operation {sequence_number}: {e}")
            raise ValueError(f"Operation application failed: {str(e)}")

    @database_sync_to_async
    def _update_cursor_position(self, position, selection_start, selection_end):
        """Update participant's cursor position"""
        if self.participant:
            self.participant.update_cursor(position, selection_start, selection_end)

    @database_sync_to_async
    def _update_participant_activity(self):
        """Update participant's activity timestamp"""
        if self.participant:
            self.participant.update_activity()

    @database_sync_to_async
    def _update_participant_status(self, status):
        """Update participant's status"""
        if self.participant:
            if status == 'disconnected':
                self.participant.disconnect()
            else:
                # Update status
                self.participant.status = status
                self.participant.save()

    @database_sync_to_async
    def _save_session_to_article(self):
        """Save collaborative session back to article"""
        return self.session.save_to_article(self.user)

    @database_sync_to_async
    def _get_session_info(self):
        """Get current session information"""
        return {
            'id': str(self.session.id),
            'name': self.session.session_name,
            'status': self.session.status,
            'is_locked': self.session.is_locked,
            'max_participants': self.session.max_participants,
            'participant_count': self.session.participants.count(),
            'created_at': self.session.created_at.isoformat(),
            'last_activity': self.session.last_activity.isoformat(),
        }

    # Broadcasting methods
    async def _broadcast_user_joined(self):
        """Broadcast user joined event to session group"""
        await self.channel_layer.group_send(
            f"collaborative_{self.article_id}",
            {
                'type': 'user_joined',
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username,
                    'full_name': self.user.get_full_name() or self.user.username,
                },
                'participant_id': str(self.participant.id),
                'timestamp': self.participant.joined_at.isoformat(),
            }
        )

    async def _broadcast_user_left(self):
        """Broadcast user left event to session group"""
        await self.channel_layer.group_send(
            f"collaborative_{self.article_id}",
            {
                'type': 'user_left',
                'user_id': str(self.user.id),
                'participant_id': str(self.participant.id),
                'timestamp': self.participant.last_activity.isoformat(),
            }
        )

    async def _broadcast_operation(self, operation_result, exclude_channel=None):
        """Broadcast operation to all participants"""
        message = {
            'type': 'operation_applied',
            'operation': operation_result,
        }

        await self.channel_layer.group_send(
            f"collaborative_{self.article_id}",
            message
        )

    async def _broadcast_cursor_update(self):
        """Broadcast cursor update to other participants"""
        if self.participant:
            await self.channel_layer.group_send(
                f"collaborative_{self.article_id}",
                {
                    'type': 'cursor_updated',
                    'participant_id': str(self.participant.id),
                    'cursor_position': self.participant.cursor_position,
                    'selection_start': self.participant.selection_start,
                    'selection_end': self.participant.selection_end,
                    'user_id': str(self.user.id),
                }
            )

    # Channel layer message handlers (called by group_send)
    async def user_joined(self, event):
        """Handle user joined message"""
        if self.channel_name != event.get('exclude_channel'):
            await self.send_json({
                'type': 'user_joined',
                'user': event['user'],
                'participant_id': event['participant_id'],
                'timestamp': event['timestamp'],
            })

    async def user_left(self, event):
        """Handle user left message"""
        await self.send_json({
            'type': 'user_left',
            'user_id': event['user_id'],
            'participant_id': event['participant_id'],
            'timestamp': event['timestamp'],
        })

    async def operation_applied(self, event):
        """Handle operation applied message"""
        await self.send_json({
            'type': 'operation_applied',
            'operation': event['operation'],
        })

    async def cursor_updated(self, event):
        """Handle cursor update message"""
        # Don't send cursor updates back to the user who sent them
        if event['participant_id'] != str(self.participant.id):
            await self.send_json({
                'type': 'cursor_updated',
                'participant_id': event['participant_id'],
                'cursor_position': event['cursor_position'],
                'selection_start': event['selection_start'],
                'selection_end': event['selection_end'],
                'user_id': event['user_id'],
            })

    async def session_locked(self, event):
        """Handle session locked message"""
        await self.send_json({
            'type': 'session_locked',
            'locked_by': event['locked_by'],
            'timestamp': event['timestamp'],
        })

    async def session_unlocked(self, event):
        """Handle session unlocked message"""
        await self.send_json({
            'type': 'session_unlocked',
            'unlocked_by': event['unlocked_by'],
            'timestamp': event['timestamp'],
        })

    async def session_ended(self, event):
        """Handle session ended message"""
        await self.send_json({
            'type': 'session_ended',
            'reason': event.get('reason', 'Session ended'),
            'timestamp': event['timestamp'],
        })

    async def group_add(self):
        """Add to collaborative editing group"""
        await self.channel_layer.group_add(
            f"collaborative_{self.article_id}",
            self.channel_name
        )

    async def group_discard(self):
        """Remove from collaborative editing group"""
        await self.channel_layer.group_discard(
            f"collaborative_{self.article_id}",
            self.channel_name
        )
