from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.decorators import otp_required
from django_otp import user_has_device
from django.http import JsonResponse
from django.views.decorators.http import require_POST
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
    
    # Check if room exists, redirect to index if not
    try:
        room_obj = Room.objects.get(name=room_name)
    except Room.DoesNotExist:
        messages.error(request, f'Room "{room_name}" does not exist. Please create it first or join an existing room.')
        return redirect('chat_index')
    
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
@require_POST
def create_room(request):
    """Create a new room with duplicate checking"""
    room_name = request.POST.get('room_name', '').strip()
    
    if not room_name:
        return JsonResponse({
            'success': False, 
            'message': 'Room name is required.'
        })
    
    # Check if room already exists
    if Room.objects.filter(name=room_name).exists():
        return JsonResponse({
            'success': False, 
            'message': f'Room "{room_name}" already exists. Please choose a different name.'
        })
    
    # Create the room
    try:
        room = Room.objects.create(
            name=room_name,
            creator=request.user
        )
        return JsonResponse({
            'success': True, 
            'message': f'Room "{room_name}" created successfully!',
            'redirect_url': f'/chat/{room_name}/'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred while creating the room. Please try again.'
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
