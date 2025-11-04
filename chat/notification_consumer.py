import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import PrivateMessage


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Create a unique notification group for this user
        self.notification_group_name = f'notifications_{self.user.username}'
        
        # Join the notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f'[NOTIFICATION] User {self.user.username} connected to notifications')
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
            print(f'[NOTIFICATION] User {self.user.username} disconnected from notifications')
    
    async def receive(self, text_data):
        """Handle messages from WebSocket (not used for notifications, but required)"""
        pass
    
    async def new_message_notification(self, event):
        """Send new message notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'message_id': event.get('message_id')
        }))


@database_sync_to_async
def get_unread_message_count(user):
    """Get count of unread messages for a user"""
    return PrivateMessage.objects.filter(
        receiver=user,
        is_read=False
    ).count()
