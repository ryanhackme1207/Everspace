import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message, RoomMember
from django.core.cache import cache
import asyncio
from django.utils import timezone
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

        # Check if room still exists
        room_exists = await self.check_room_exists()
        if not room_exists:
            await self.close()
            return

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
            'display_name': display_name,
        }
        # Mark user online in DB RoomMember (sync presence)
        await self._mark_online()
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
        """Send periodic heartbeat to keep user active and sync user lists"""
        try:
            while True:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                # Update last seen time
                if hasattr(self, 'room_name') and hasattr(self, 'user'):
                    last_seen_key = f"last_seen_{self.room_name}_{self.user.username}"
                    cache.set(last_seen_key, time.time(), 3600)
                    
                    # Send updated active users list to keep everyone in sync
                    cache_key = f"active_users_{self.room_name}"
                    active_users = cache.get(cache_key, {})
                    
                    # Clean up users who haven't been seen recently (more than 2 minutes)
                    current_time = time.time()
                    users_to_remove = []
                    
                    for username in active_users.keys():
                        user_last_seen_key = f"last_seen_{self.room_name}_{username}"
                        user_last_seen = cache.get(user_last_seen_key, 0)
                        if (current_time - user_last_seen) > 120:  # 2 minutes
                            users_to_remove.append(username)
                    
                    # Remove inactive users
                    for username in users_to_remove:
                        user_data = active_users.get(username, {})
                        del active_users[username]
                        
                        # Send leave notification
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'user_leave',
                                'username': username,
                                'display_name': user_data.get('display_name', username),
                            }
                        )
                        # Mark user offline in DB
                        await self._mark_offline_username(username)
                    
                    # Update cache if users were removed
                    if users_to_remove:
                        cache.set(cache_key, active_users, 3600)
                        
                        # Send updated active users list
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'active_users_update',
                                'users': list(active_users.values())
                            }
                        )
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
                # Mark user offline in DB
                await self._mark_offline_username(self.user.username)

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

            # Save message to database - check if room still exists
            message_id = await self.save_message(self.user, self.room_name, message)
            
            if not message_id:
                # Room no longer exists or user is banned - disconnect user
                await self.send(text_data=json.dumps({
                    'type': 'room_deleted',
                    'message': 'This room has been deleted or you have been banned.'
                }))
                await self.close()
                return

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'display_name': display_name,
                    'timestamp': self.get_timestamp(),
                    'message_id': message_id
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
        message_id = event.get('message_id')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'display_name': display_name,
            'timestamp': timestamp,
            'message_id': message_id
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

    # Handle room deletion event
    async def room_deleted(self, event):
        message = event.get('message', 'This room has been deleted.')
        
        # Send room deletion notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'room_deleted',
            'message': message
        }))
        
        # Close the connection
        await self.close()

    # Handle message deletion event
    async def delete_message(self, event):
        message_id = event['message_id']
        username = event['username']
        
        # Send message deletion notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'delete_message',
            'message_id': message_id,
            'username': username
        }))

    # Handle gift animation event
    async def gift_animation(self, event):
        # Send gift animation to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'gift_animation',
            'sender_username': event['sender_username'],
            'sender_display': event['sender_display'],
            'recipient_username': event['recipient_username'],
            'recipient_display': event['recipient_display'],
            'gift_name': event['gift_name'],
            'gift_emoji': event['gift_emoji'],
            'animation': event['animation'],
            'intimacy_gained': event['intimacy_gained'],
            'intimacy_total': event['intimacy_total']
        }))

    # Handle user kicked event
    async def user_kicked(self, event):
        username = event['username']
        message = event['message']
        
        # Check if this is the kicked user
        if self.user.username == username:
            # Send kick notification and disconnect
            await self.send(text_data=json.dumps({
                'type': 'user_kicked',
                'message': message
            }))
            await self.close()
        else:
            # Notify other users about the kick
            await self.send(text_data=json.dumps({
                'type': 'user_leave',
                'username': username,
                'display_name': username,
            }))

    # Handle user banned event  
    async def user_banned(self, event):
        username = event['username']
        message = event['message']
        
        # Check if this is the banned user
        if self.user.username == username:
            # Send ban notification and disconnect
            await self.send(text_data=json.dumps({
                'type': 'user_banned',
                'message': message
            }))
            await self.close()
        else:
            # Notify other users about the ban
            await self.send(text_data=json.dumps({
                'type': 'user_leave',
                'username': username,
                'display_name': username,
            }))

    async def ownership_transferred(self, event):
        """Handle room ownership transfer notification"""
        await self.send(text_data=json.dumps({
            'type': 'ownership_transferred',
            'old_owner': event['old_owner'],
            'new_owner': event['new_owner'],
            'message': event['message']
        }))

    @database_sync_to_async
    def check_room_exists(self):
        try:
            Room.objects.get(name=self.room_name)
            return True
        except Room.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, room_name, message):
        try:
            room = Room.objects.get(name=room_name)
            # Check if user is banned from this room
            if room.is_user_banned(user):
                return None
            # Check if user is still a member of the room (not kicked)
            if not room.members.filter(user=user).exists():
                return None
            msg = Message.objects.create(user=user, room=room, content=message)
            return msg.id
        except Room.DoesNotExist:
            # Room no longer exists
            return None

    def get_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    # ==== Presence helper methods (DB sync) ====
    @database_sync_to_async
    def _set_member_status(self, username: str, status: str):
        """Low-level helper to set a RoomMember.status if membership exists."""
        try:
            room = Room.objects.get(name=self.room_name)
            room_member = room.members.select_related('user').get(user__username=username)
            if room_member.status != status:
                room_member.status = status
                room_member.save(update_fields=["status"])
        except (Room.DoesNotExist, RoomMember.DoesNotExist):
            # Room deleted or user not a member anymore (kicked/banned) - ignore
            pass

    async def _mark_online(self):
        """Mark the current websocket user online in the RoomMember table."""
        if hasattr(self, 'user') and hasattr(self, 'room_name'):
            await self._set_member_status(self.user.username, 'online')

    async def _mark_offline_username(self, username: str):
        """Mark an arbitrary username offline (used by idle pruning / disconnect)."""
        if hasattr(self, 'room_name'):
            await self._set_member_status(username, 'offline')