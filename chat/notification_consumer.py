import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


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
            'notification_type': 'message',
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'message_id': event.get('message_id')
        }))
    
    async def friend_request_notification(self, event):
        """Send friend request notification"""
        await self.send(text_data=json.dumps({
            'type': 'friend_request',
            'notification_type': 'friend_request',
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    async def friend_accepted_notification(self, event):
        """Send friend accepted notification"""
        await self.send(text_data=json.dumps({
            'type': 'friend_accepted',
            'notification_type': 'friend_accepted',
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    async def kick_notification(self, event):
        """Send kick notification"""
        await self.send(text_data=json.dumps({
            'type': 'kicked',
            'notification_type': 'kicked',
            'sender': event['sender'],
            'room': event['room'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    async def ban_notification(self, event):
        """Send ban notification"""
        await self.send(text_data=json.dumps({
            'type': 'banned',
            'notification_type': 'banned',
            'sender': event['sender'],
            'room': event['room'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    async def general_notification(self, event):
        """Send general notification"""
        await self.send(text_data=json.dumps({
            'type': event.get('notification_type', 'general'),
            'notification_type': event.get('notification_type', 'general'),
            'title': event.get('title', ''),
            'message': event['message'],
            'link': event.get('link', ''),
            'timestamp': event['timestamp']
        }))
