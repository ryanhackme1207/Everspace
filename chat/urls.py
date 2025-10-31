from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('chat/', views.index, name='chat_index'),
    path('chat/create/', views.create_room, name='create_room'),
    path('chat/finalize-room/', views.finalize_room, name='finalize_room'),
    path('chat/delete-room/', views.delete_room_ajax, name='delete_room_ajax'),
    path('chat/<str:room_name>/', views.room, name='chat_room'),
    path('chat/<str:room_name>/delete/', views.delete_room, name='delete_room'),
    path('chat/<str:room_name>/settings/', views.room_settings, name='room_settings'),
    path('chat/kick-member/', views.kick_member, name='kick_member'),
    path('chat/ban-member/', views.ban_member, name='ban_member'),
    path('chat/unban-member/', views.unban_member, name='unban_member'),
    path('test-ajax/', views.test_endpoint, name='test_endpoint'),
    path('chat/transfer-ownership/', views.transfer_ownership, name='transfer_ownership'),
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/send-request/', views.send_friend_request, name='send_friend_request'),
    path('friends/respond-request/', views.respond_friend_request, name='respond_friend_request'),
    path('friends/chat/<str:username>/', views.private_chat, name='private_chat'),
    path('friends/send-message/', views.send_private_message, name='send_private_message'),
    # Profile URLs
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('profile/upload-cover/', views.upload_cover_image, name='upload_cover_image'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('profile/', views.view_profile, name='my_profile'),
]