from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.decorators import otp_required
from django_otp import user_has_device
from .models import Room, Message

def landing_page(request):
    """Modern landing page with animations and introduction"""
    if request.user.is_authenticated:
        return redirect('chat_index')
    return render(request, 'chat/landing.html')

@login_required
def index(request):
    # Check if user has MFA enabled (but don't show automatic message)
    user_has_mfa = user_has_device(request.user)
    
    rooms = Room.objects.all()
    return render(request, 'chat/index.html', {
        'rooms': rooms,
        'user_has_mfa': user_has_mfa
    })

@login_required
def room(request, room_name):
    # Optional: Require MFA for accessing chat rooms (uncomment if desired)
    # if user_has_device(request.user) and not request.user.is_verified():
    #     messages.error(request, 'Please complete MFA verification to access chat rooms.')
    #     return redirect('auth_mfa_verify')
    
    room_obj, created = Room.objects.get_or_create(
        name=room_name,
        defaults={'creator': request.user}
    )
    messages_list = Message.objects.filter(room=room_obj).order_by('timestamp')[:50]  # Last 50 messages
    user_has_mfa = user_has_device(request.user)
    
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'room_obj': room_obj,
        'messages': messages_list,
        'user': request.user,
        'user_has_mfa': user_has_mfa,
        'is_room_creator': room_obj.can_delete(request.user)
    })

@login_required
def delete_room(request, room_name):
    """Delete a room - only the creator can delete it"""
    room_obj = get_object_or_404(Room, name=room_name)
    
    if not room_obj.can_delete(request.user):
        messages.error(request, 'Only the room creator can delete this room.')
        return redirect('chat_room', room_name=room_name)
    
    if request.method == 'POST':
        room_obj.delete()
        messages.success(request, f'Room "{room_name}" has been deleted successfully.')
        return redirect('chat_index')
    
    # If GET request, show confirmation page
    return render(request, 'chat/delete_room.html', {
        'room_obj': room_obj,
        'room_name': room_name
    })
