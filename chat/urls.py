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
]