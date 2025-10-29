import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message
from django.core.cache import cache
import asyncio
import time

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heartbeat_task = None

    async def connect(self):
        # Check if user is authenticated
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Simple anti-spam approach using timestamps
        display_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        current_time = time.time()
        
        # Check when user was last seen in this room
        last_seen_key = f"last_seen_{self.room_name}_{self.user.username}"
        last_seen = cache.get(last_seen_key, 0)
        
        # Add user to active users list
        cache_key = f"active_users_{self.room_name}"
        active_users = cache.get(cache_key, {})
        was_already_active = self.user.username in active_users
        
        active_users[self.user.username] = {
            'username': self.user.username,
            'display_name': display_name
        }
        cache.set(cache_key, active_users, 3600)
        
        # Update user's last seen time
        cache.set(last_seen_key, current_time, 3600)
        
        # Send current active users list to the newly connected user
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': list(active_users.values())
        }))
        
        # Only send join notification if user wasn't recently active (more than 10 seconds ago)
        if not was_already_active or (current_time - last_seen) > 10:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'username': self.user.username,
                    'display_name': display_name,
                }
            )
            
        # Start heartbeat to keep user active
        self.heartbeat_task = asyncio.create_task(self._heartbeat())

    async def disconnect(self, close_code):
        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            
        # Leave room group first
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        # Schedule user removal check without blocking
        if hasattr(self, 'room_name') and hasattr(self, 'user'):
            # Create a background task to handle the delayed removal
            asyncio.create_task(self._handle_delayed_disconnect())

    async def _heartbeat(self):
        """Send periodic heartbeat to keep user active"""
        try:
            while True:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                # Update last seen time
                if hasattr(self, 'room_name') and hasattr(self, 'user'):
                    last_seen_key = f"last_seen_{self.room_name}_{self.user.username}"
                    cache.set(last_seen_key, time.time(), 3600)
                else:
                    break  # Exit if connection is gone
        except asyncio.CancelledError:
            pass  # Task was cancelled, which is normal during disconnect

    async def _handle_delayed_disconnect(self):
        """Handle user disconnection with delay to catch page refreshes"""
        # Wait to see if user reconnects (page refresh scenario)
        await asyncio.sleep(3)
        
        # Check if user has reconnected recently
        last_seen_key = f"last_seen_{self.room_name}_{self.user.username}"
        last_seen = cache.get(last_seen_key, 0)
        current_time = time.time()
        
        # If user hasn't been seen recently (no recent activity), remove them
        if (current_time - last_seen) >= 3:  # No activity for 3+ seconds
            cache_key = f"active_users_{self.room_name}"
            active_users = cache.get(cache_key, {})
            
            if self.user.username in active_users:
                del active_users[self.user.username]
                cache.set(cache_key, active_users, 3600)
                
                # Send leave notification
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_leave',
                        'username': self.user.username,
                        'display_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                    }
                )

    # Receive message from WebSocket
    async def receive(self, text_data):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
            
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message'].strip()
            
            # Basic message validation
            if not message or len(message) > 1000:
                return
            
            # Use authenticated user's username
            username = self.user.username
            display_name = f"{self.user.first_name} {self.user.last_name}".strip() or username

            # Save message to database
            await self.save_message(self.user, self.room_name, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'display_name': display_name,
                    'timestamp': self.get_timestamp()
                }
            )
        except json.JSONDecodeError:
            # Invalid JSON, ignore
            pass

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        display_name = event.get('display_name', username)
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'display_name': display_name,
            'timestamp': timestamp
        }))

    # Handle user join event
    async def user_join(self, event):
        username = event['username']
        display_name = event.get('display_name', username)

        # Send user join notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': username,
            'display_name': display_name,
        }))

    # Handle user leave event
    async def user_leave(self, event):
        username = event['username']
        display_name = event.get('display_name', username)

        # Send user leave notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': username,
            'display_name': display_name,
        }))



    # Handle active users list update
    async def active_users_update(self, event):
        users = event['users']
        
        # Send updated active users list to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': users,
        }))

    @database_sync_to_async
    def save_message(self, user, room_name, message):
        room, created = Room.objects.get_or_create(name=room_name)
        Message.objects.create(user=user, room=room, content=message)

    def get_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S')