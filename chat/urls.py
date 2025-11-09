from django.urls import path
from . import views

app_name = 'chat'

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
    # Message Management URLs
    path('chat/message/unsend/', views.unsend_message, name='unsend_message'),
    # Profile URLs
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('profile/', views.view_profile, name='my_profile'),
    # Notification URLs
    path('chat/notifications/count/', views.notification_count, name='notification_count'),
    path('chat/notifications/list/', views.notification_list, name='notification_list'),
    path('chat/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('chat/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    # Gift System URLs
    path('chat/gifts/send/', views.send_gift, name='send_gift'),
    path('chat/gifts/send-new/<str:room_name>/', views.send_gift_new, name='send_gift_new'),
    path('chat/gifts/list/', views.get_gifts, name='get_gifts'),
    path('chat/gifts/search/', views.search_gifts, name='search_gifts'),
    path('chat/gifts/users/<str:room_name>/', views.get_room_users, name='get_room_users'),
    path('chat/gifts/intimacy/', views.get_user_intimacy, name='get_user_intimacy'),
    path('chat/gifts/leaderboard/', views.get_leaderboard, name='get_leaderboard'),
    # GIF System URLs
    path('chat/gifs/packs/', views.get_gif_packs, name='get_gif_packs'),
    path('chat/gifs/pack/<int:pack_id>/', views.get_gifs_by_pack, name='get_gifs_by_pack'),
    path('chat/gifs/search/', views.search_gifs, name='search_gifs'),
    path('chat/gifs/send/', views.send_gif, name='send_gif'),
    path('chat/gifs/trending/', views.get_trending_gifs, name='get_trending_gifs'),
    path('chat/gifs/stats/', views.get_gif_stats, name='get_gif_stats'),
    # Mini Games URLs
    path('games/2048/', views.game_2048, name='game_2048'),
    path('games/submit-score/', views.submit_game_score, name='submit_game_score'),
    path('games/stats/', views.get_game_stats, name='get_game_stats'),
    # Debug endpoints
    path('debug/gifts-status/', views.debug_gifts_status, name='debug_gifts_status'),
]