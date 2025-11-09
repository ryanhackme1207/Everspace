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
            message_type = text_data_json.get('type', 'message')
            
            # Handle sound sharing
            if message_type == 'sound':
                username = self.user.username
                display_name = f"{self.user.first_name} {self.user.last_name}".strip() or username
                
                # Broadcast sound to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'sound_message',
                        'sound_name': text_data_json.get('sound_name', 'Sound'),
                        'sound_emoji': text_data_json.get('sound_emoji', '🔊'),
                        'sound_url': text_data_json.get('sound_url', ''),
                        'username': username,
                        'display_name': display_name,
                        'timestamp': self.get_timestamp(),
                    }
                )
                return
            
            # Handle regular chat messages
            message = text_data_json.get('message', '').strip()
            
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

    # Handle sound message event
    async def sound_message(self, event):
        username = event['username']
        display_name = event.get('display_name', username)
        sound_name = event.get('sound_name', 'Sound')
        sound_emoji = event.get('sound_emoji', '🔊')
        sound_url = event.get('sound_url', '')
        timestamp = event.get('timestamp', '')

        # Send sound to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'sound',
            'sound_name': sound_name,
            'sound_emoji': sound_emoji,
            'sound_url': sound_url,
            'username': username,
            'display_name': display_name,
            'timestamp': timestamp,
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


class Game2048Consumer(AsyncWebsocketConsumer):
    """WebSocket consumer for multiplayer 2048 game"""
    
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
            
        self.user = self.scope["user"]
        self.game_id = self.scope['url_route']['kwargs'].get('game_id', None)
        
        if not self.game_id:
            await self.close()
            return
        
        self.game_group_name = f'game2048_{self.game_id}'
        
        # Join game group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Get game state and send to player
        game_state = await self.get_game_state()
        if game_state:
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'game': game_state
            }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'game_group_name'):
            await self.channel_layer.group_discard(
                self.game_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'find_match':
                await self.handle_find_match(data)
            elif message_type == 'move':
                await self.handle_move(data)
            elif message_type == 'game_over':
                await self.handle_game_over(data)
                
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_find_match(self, data):
        """Find an opponent or create bot game"""
        # Try to find waiting game
        game = await self.find_waiting_game()
        
        if game:
            # Join existing game
            await self.join_game(game['id'])
        else:
            # Check if user wants to wait or play with bot
            wait_for_player = data.get('wait_for_player', False)
            
            if wait_for_player:
                # Create new waiting game
                game = await self.create_game(is_bot=False)
                await self.send(text_data=json.dumps({
                    'type': 'waiting',
                    'game_id': game['id'],
                    'message': 'Waiting for opponent...'
                }))
            else:
                # Create bot game
                game = await self.create_game(is_bot=True)
                await self.start_game(game['id'])
    
    async def handle_move(self, data):
        """Handle player move and calculate attacks/heals"""
        merged_tiles = data.get('merged_tiles', [])
        score = data.get('score', 0)
        board = data.get('board', [])
        
        # Update game state
        await self.update_player_state(score, board)
        
        # Calculate damage and healing
        total_damage = 0
        total_heal = 0
        
        for tile_value in merged_tiles:
            damage = await self.calculate_damage(tile_value)
            heal = await self.calculate_heal(tile_value)
            total_damage += damage
            total_heal += heal
        
        # Apply damage to opponent and heal to self
        health_updates = await self.apply_health_changes(total_damage, total_heal)
        
        # Broadcast move to opponent
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_move',
                'player': self.user.username,
                'score': score,
                'board': board,
                'damage': total_damage,
                'heal': total_heal,
                'health_updates': health_updates,
                'merged_tiles': merged_tiles
            }
        )
        
        # Check win condition
        if health_updates['opponent_health'] <= 0:
            await self.handle_victory()
    
    async def handle_game_over(self, data):
        """Handle game over (someone reached 2048 or health depleted)"""
        winner = data.get('winner')
        reason = data.get('reason', 'health')  # 'health' or '2048'
        
        await self.finish_game(winner, reason)
    
    async def handle_victory(self):
        """Handle victory and calculate rewards"""
        game_state = await self.get_game_state()
        
        if not game_state or game_state['status'] != 'active':
            return
        
        # Finish game
        await self.finish_game(self.user.username, 'health')
        
        # Calculate rewards
        rewards = await self.calculate_rewards(game_state)
        
        # Broadcast victory
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_victory',
                'winner': self.user.username,
                'reason': 'health',
                'rewards': rewards
            }
        )
    
    # WebSocket message handlers
    async def game_move(self, event):
        """Send move update to client"""
        await self.send(text_data=json.dumps(event))
    
    async def game_start(self, event):
        """Send game start notification"""
        await self.send(text_data=json.dumps(event))
    
    async def game_victory(self, event):
        """Send victory notification"""
        await self.send(text_data=json.dumps(event))
    
    # Database operations
    @database_sync_to_async
    def get_game_state(self):
        """Get current game state"""
        from .models import MultiplayerGame2048
        try:
            game = MultiplayerGame2048.objects.get(game_id=self.game_id)
            return {
                'id': game.game_id,
                'status': game.status,
                'player1': game.player1.username,
                'player2': game.player2.username if game.player2 else 'BOT',
                'is_bot': game.is_bot_game,
                'player1_health': game.player1_health,
                'player2_health': game.player2_health,
                'player1_score': game.player1_score,
                'player2_score': game.player2_score,
            }
        except MultiplayerGame2048.DoesNotExist:
            return None
    
    @database_sync_to_async
    def find_waiting_game(self):
        """Find a waiting game to join"""
        from .models import MultiplayerGame2048
        game = MultiplayerGame2048.objects.filter(
            status='waiting',
            is_bot_game=False
        ).exclude(player1=self.user).first()
        
        if game:
            return {'id': game.game_id}
        return None
    
    @database_sync_to_async
    def create_game(self, is_bot=False):
        """Create a new game"""
        from .models import MultiplayerGame2048
        import uuid
        
        game_id = f"game_{uuid.uuid4().hex[:12]}"
        game = MultiplayerGame2048.objects.create(
            game_id=game_id,
            player1=self.user,
            is_bot_game=is_bot,
            status='waiting' if not is_bot else 'active'
        )
        
        if is_bot:
            # Create a bot user if not exists
            bot_user, _ = User.objects.get_or_create(
                username='2048_BOT',
                defaults={'first_name': 'Bot', 'last_name': 'AI'}
            )
            game.player2 = bot_user
            game.started_at = timezone.now()
            game.save()
        
        return {'id': game.game_id}
    
    @database_sync_to_async
    def join_game(self, game_id):
        """Join an existing game"""
        from .models import MultiplayerGame2048
        try:
            game = MultiplayerGame2048.objects.get(game_id=game_id)
            if not game.player2:
                game.player2 = self.user
                game.status = 'active'
                game.started_at = timezone.now()
                game.save()
                return True
        except MultiplayerGame2048.DoesNotExist:
            pass
        return False
    
    @database_sync_to_async
    def start_game(self, game_id):
        """Start the game"""
        from .models import MultiplayerGame2048
        try:
            game = MultiplayerGame2048.objects.get(game_id=game_id)
            game.start_game()
            
            # Notify both players
            asyncio.create_task(
                self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'game_start',
                        'game_id': game_id,
                        'player1': game.player1.username,
                        'player2': game.player2.username if game.player2 else 'BOT',
                        'is_bot': game.is_bot_game
                    }
                )
            )
        except MultiplayerGame2048.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_player_state(self, score, board):
        """Update player's score and board"""
        from .models import MultiplayerGame2048
        import json as json_lib
        
        try:
            game = MultiplayerGame2048.objects.get(game_id=self.game_id)
            if game.player1 == self.user:
                game.player1_score = score
                game.player1_board = json_lib.dumps(board)
            elif game.player2 == self.user:
                game.player2_score = score
                game.player2_board = json_lib.dumps(board)
            game.save()
        except MultiplayerGame2048.DoesNotExist:
            pass
    
    @database_sync_to_async
    def calculate_damage(self, tile_value):
        """Calculate damage from tile merge"""
        from .models import MultiplayerGame2048
        game = MultiplayerGame2048.objects.filter(game_id=self.game_id).first()
        if game:
            return game.calculate_damage(tile_value)
        return 0
    
    @database_sync_to_async
    def calculate_heal(self, tile_value):
        """Calculate heal from tile merge"""
        from .models import MultiplayerGame2048
        game = MultiplayerGame2048.objects.filter(game_id=self.game_id).first()
        if game:
            return game.calculate_heal(tile_value)
        return 0
    
    @database_sync_to_async
    def apply_health_changes(self, damage, heal):
        """Apply damage to opponent and heal to self"""
        from .models import MultiplayerGame2048
        
        try:
            game = MultiplayerGame2048.objects.get(game_id=self.game_id)
            
            # Determine player positions
            is_player1 = game.player1 == self.user
            
            if is_player1:
                # Player 1 attacks player 2 and heals self
                game.player2_health = max(0, game.player2_health - damage)
                game.player1_health = min(100, game.player1_health + heal)
                
                result = {
                    'your_health': game.player1_health,
                    'opponent_health': game.player2_health
                }
            else:
                # Player 2 attacks player 1 and heals self
                game.player1_health = max(0, game.player1_health - damage)
                game.player2_health = min(100, game.player2_health + heal)
                
                result = {
                    'your_health': game.player2_health,
                    'opponent_health': game.player1_health
                }
            
            game.save()
            return result
            
        except MultiplayerGame2048.DoesNotExist:
            return {'your_health': 100, 'opponent_health': 100}
    
    @database_sync_to_async
    def finish_game(self, winner_username, reason):
        """Finish the game"""
        from .models import MultiplayerGame2048
        
        try:
            game = MultiplayerGame2048.objects.get(game_id=self.game_id)
            winner = User.objects.get(username=winner_username)
            game.finish_game(winner)
        except (MultiplayerGame2048.DoesNotExist, User.DoesNotExist):
            pass
    
    @database_sync_to_async
    def calculate_rewards(self, game_state):
        """Calculate Evercoin rewards for winner"""
        from .models import UserProfile
        
        # Base reward from score
        winner_score = game_state['player1_score'] if game_state['player1'] == self.user.username else game_state['player2_score']
        base_reward = min(200, max(50, winner_score // 50))
        
        # Bonus for winning
        win_bonus = 100
        
        # Health bonus (remaining health)
        winner_health = game_state['player1_health'] if game_state['player1'] == self.user.username else game_state['player2_health']
        health_bonus = winner_health // 2  # 0-50 bonus
        
        total_reward = base_reward + win_bonus + health_bonus
        
        # Credit to winner
        try:
            profile, _ = UserProfile.objects.get_or_create(user=self.user)
            profile.evercoin += total_reward
            profile.save()
        except:
            pass
        
        return {
            'base': base_reward,
            'win_bonus': win_bonus,
            'health_bonus': health_bonus,
            'total': total_reward
        }