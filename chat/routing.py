from django.urls import re_path
from . import consumers
from .notification_consumer import NotificationConsumer
from .private_chat_consumer import PrivateChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/private-chat/(?P<friend_username>\w+)/$', PrivateChatConsumer.as_asgi()),
]