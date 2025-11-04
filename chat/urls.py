from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('chat/', views.index, name='chat_index'),
    path('chat/create/', views.create_room, name='create_room'),
    path('chat/finalize-room/', views.finalize_room, name='finalize_room'),
    path('chat/delete-room/', views.delete_room_ajax, name='delete_room_ajax'),
    # Specific chat action endpoints should precede dynamic room route to avoid shadow matching
    path('chat/kick-member/', views.kick_member, name='kick_member'),
    path('chat/ban-member/', views.ban_member, name='ban_member'),
    path('chat/unban-member/', views.unban_member, name='unban_member'),
    path('test-ajax/', views.test_endpoint, name='test_endpoint'),
    path('chat/transfer-ownership/', views.transfer_ownership, name='transfer_ownership'),
    # Dynamic room routes (placed after specific endpoints)
    path('chat/<str:room_name>/', views.room, name='chat_room'),
    path('chat/<str:room_name>/delete/', views.delete_room, name='delete_room'),
    path('chat/<str:room_name>/settings/', views.room_settings, name='room_settings'),
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/send-request/', views.send_friend_request, name='send_friend_request'),
    path('friends/respond-request/', views.respond_friend_request, name='respond_friend_request'),
    path('friends/chat/<str:username>/', views.private_chat, name='private_chat'),
    path('friends/send-message/', views.send_private_message, name='send_private_message'),
    # Profile URLs
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('profile/', views.view_profile, name='my_profile'),
    # GIF search proxy
    path('gif/search/', views.gif_search, name='gif_search'),
    # Notification URLs
    path('chat/notifications/count/', views.notification_count, name='notification_count'),
    path('chat/notifications/list/', views.notification_list, name='notification_list'),
    path('chat/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('chat/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]