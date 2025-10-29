from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('chat/', views.index, name='chat_index'),
    path('chat/<str:room_name>/', views.room, name='chat_room'),
    path('chat/<str:room_name>/delete/', views.delete_room, name='delete_room'),
]