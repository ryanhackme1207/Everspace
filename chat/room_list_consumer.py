import json
from channels.generic.websocket import AsyncWebsocketConsumer


class RoomListConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live room list updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'room_list_updates'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print('[ROOM LIST] Client connected')
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('[ROOM LIST] Client disconnected')
    
    async def room_created(self, event):
        """Send room created event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'room_created',
            'room': event['room']
        }))
    
    async def room_deleted(self, event):
        """Send room deleted event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'room_deleted',
            'room_name': event['room_name']
        }))
    
    async def room_updated(self, event):
        """Send room updated event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'room_updated',
            'room': event['room']
        }))
