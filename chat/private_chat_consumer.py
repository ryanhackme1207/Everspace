import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import PrivateMessage, Friendship
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime


class PrivateChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for private chat between friends"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        self.friend_username = self.scope['url_route']['kwargs']['friend_username']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Verify friendship
        are_friends = await self.check_friendship()
        if not are_friends:
            await self.close()
            return
        
        # Create unique room name for this private chat (sorted usernames for consistency)
        usernames = sorted([self.user.username, self.friend_username])
        self.room_group_name = f'private_chat_{usernames[0]}_{usernames[1]}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f'[PRIVATE CHAT] {self.user.username} connected to chat with {self.friend_username}')
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f'[PRIVATE CHAT] {self.user.username} disconnected from chat with {self.friend_username}')
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                message_content = data.get('message', '').strip()
                
                if not message_content:
                    return
                
                # Save message to database
                message = await self.save_message(message_content)
                
                if message:
                    # Send message to both users in the chat
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message_content,
                            'sender': self.user.username,
                            'timestamp': message['timestamp'],
                            'message_id': message['id']
                        }
                    )
                    
                    # Send notification to receiver
                    await self.send_notification_to_receiver(message)
            
            elif message_type == 'typing':
                is_typing = data.get('is_typing', False)
                
                # Broadcast typing status to other user
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'is_typing': is_typing,
                        'username': self.user.username
                    }
                )
        
        except Exception as e:
            print(f'[PRIVATE CHAT ERROR] {str(e)}')
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'message_id': event.get('message_id')
        }))
    
    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket"""
        # Only send to other user, not the one typing
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': event['is_typing']
            }))
    
    @database_sync_to_async
    def check_friendship(self):
        """Check if users are friends"""
        try:
            friend = User.objects.get(username=self.friend_username)
            return Friendship.are_friends(self.user, friend)
        except User.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database and create notification"""
        try:
            from .models import Notification
            
            friend = User.objects.get(username=self.friend_username)
            
            message = PrivateMessage.objects.create(
                sender=self.user,
                receiver=friend,
                content=content
            )
            
            # Create notification for the message
            Notification.create_message_notification(self.user, friend, message)
            
            return {
                'id': message.id,
                'timestamp': message.timestamp.isoformat(),
                'content': content
            }
        except Exception as e:
            print(f'[PRIVATE CHAT] Error saving message: {str(e)}')
            return None
    
    async def send_notification_to_receiver(self, message):
        """Send notification to receiver's notification channel"""
        try:
            receiver_notification_group = f'notifications_{self.friend_username}'
            
            await self.channel_layer.group_send(
                receiver_notification_group,
                {
                    'type': 'new_message_notification',
                    'sender': self.user.username,
                    'message': message.get('content', ''),
                    'timestamp': message['timestamp'],
                    'message_id': message['id']
                }
            )
        except Exception as e:
            print(f'[PRIVATE CHAT] Error sending notification: {str(e)}')
