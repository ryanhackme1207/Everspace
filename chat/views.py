from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.decorators import otp_required
from django_otp import user_has_device
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Room, Message, RoomMember, RoomBan

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
    
    # Check if user is banned from this room
    if room_obj.is_user_banned(request.user):
        messages.error(request, f'You are banned from room "{room_name}". Contact the room host if you believe this is an error.')
        return redirect('chat_index')
    
    # Handle private room password checking
    if room_obj.is_private():
        # Check if password is provided in POST request
        if request.method == 'POST':
            provided_password = request.POST.get('room_password', '')
            if room_obj.check_password(provided_password):
                # Store successful password verification in session
                request.session[f'room_access_{room_name}'] = True
            else:
                messages.error(request, 'Incorrect password for private room.')
                return render(request, 'chat/room_password.html', {
                    'room_obj': room_obj,
                    'room_name': room_name
                })
        else:
            # Check if user already provided correct password or is the creator
            if not request.session.get(f'room_access_{room_name}') and room_obj.creator != request.user:
                return render(request, 'chat/room_password.html', {
                    'room_obj': room_obj,
                    'room_name': room_name
                })
    
    # Add user as a member if not already added and create host if needed
    if room_obj.creator == request.user:
        # Ensure room creator is added as host member
        room_obj.add_member(request.user, role='host')
    else:
        # Add regular user as member
        room_obj.add_member(request.user, role='member')
    
    # Mark user as online in this room
    try:
        member = RoomMember.objects.get(room=room_obj, user=request.user)
        member.set_online()
    except RoomMember.DoesNotExist:
        pass
    
    messages_list = Message.objects.filter(room=room_obj).order_by('timestamp')[:50]  # Last 50 messages
    user_has_mfa = user_has_device(request.user)
    
    # Get online members for display
    online_members = room_obj.get_online_members()
    
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'room_obj': room_obj,
        'messages': messages_list,
        'user': request.user,
        'user_has_mfa': user_has_mfa,
        'is_room_creator': room_obj.can_delete(request.user),
        'is_room_host': room_obj.is_host(request.user),
        'online_members': online_members,
        'online_count': online_members.count(),
    })

@login_required
@require_POST
def create_room(request):
    """Create a new room with duplicate checking and 7-digit validation"""
    room_name = request.POST.get('room_name', '').strip()
    
    if not room_name:
        return JsonResponse({
            'success': False, 
            'message': 'Room number is required.'
        })
    
    # Validate 7-digit requirement
    if len(room_name) != 7 or not room_name.isdigit():
        return JsonResponse({
            'success': False, 
            'message': 'Room number must be exactly 7 digits (0-9 only).'
        })
    
    # Check if room already exists
    if Room.objects.filter(name=room_name).exists():
        return JsonResponse({
            'success': False, 
            'message': f'Room "{room_name}" already exists. Please choose a different number.'
        })
    
    # Create the room
    try:
        room = Room.objects.create(
            name=room_name,
            creator=request.user,
            description=''  # Initially empty, will be set via description modal
        )
        
        # Automatically add the creator as host member
        room.add_member(request.user, role='host')
        
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
@require_POST
def finalize_room(request):
    """Finalize room setup with description, visibility, and password"""
    room_name = request.POST.get('room_name', '').strip()
    description = request.POST.get('description', '').strip()
    visibility = request.POST.get('visibility', 'public').strip()
    password = request.POST.get('password', '').strip()
    
    if not room_name:
        return JsonResponse({
            'success': False, 
            'message': 'Room name is required.'
        })
    
    # Validate 7-digit requirement
    if len(room_name) != 7 or not room_name.isdigit():
        return JsonResponse({
            'success': False, 
            'message': 'Room number must be exactly 7 digits.'
        })
    
    # Validate visibility
    if visibility not in ['public', 'private']:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid visibility option.'
        })
    
    # Validate private room password
    if visibility == 'private':
        if not password:
            return JsonResponse({
                'success': False, 
                'message': 'Password is required for private rooms.'
            })
        if len(password) < 4:
            return JsonResponse({
                'success': False, 
                'message': 'Password must be at least 4 characters long.'
            })
    
    try:
        room = Room.objects.get(name=room_name)
        
        # Only creator can finalize room setup
        if room.creator != request.user:
            return JsonResponse({
                'success': False, 
                'message': 'Only the room creator can finalize the setup.'
            })
        
        # Update room settings
        room.description = description
        room.visibility = visibility
        room.password = password if visibility == 'private' else ''
        room.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Room {room_name} setup completed successfully!'
        })
        
    except Room.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Room not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred while finalizing the room setup.'
        })

@login_required
@require_POST
def delete_room_ajax(request):
    """Delete a room via AJAX (for cancellation)"""
    room_name = request.POST.get('room_name', '').strip()
    
    if not room_name:
        return JsonResponse({
            'success': False, 
            'message': 'Room name is required.'
        })
    
    try:
        room = Room.objects.get(name=room_name)
        
        # Only creator can delete
        if room.creator != request.user:
            return JsonResponse({
                'success': False, 
                'message': 'Only the room creator can delete this room.'
            })
        
        room.delete()
        return JsonResponse({
            'success': True, 
            'message': f'Room {room_name} deleted successfully.'
        })
        
    except Room.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Room not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred while deleting the room.'
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


@login_required  
def room_settings(request, room_name):
    """Room settings page for hosts to manage room, members, and settings"""
    room_obj = get_object_or_404(Room, name=room_name)
    
    # Only room host can access settings
    if not room_obj.is_host(request.user):
        messages.error(request, 'Only the room host can access room settings.')
        return redirect('chat_room', room_name=room_name)
    
    # Get room statistics
    online_members = room_obj.get_online_members()
    all_members = room_obj.get_all_members()
    banned_users = room_obj.banned_users.filter(is_active=True)
    
    # Handle description update
    if request.method == 'POST' and 'update_description' in request.POST:
        new_description = request.POST.get('description', '').strip()
        room_obj.update_description(new_description)
        messages.success(request, 'Room description updated successfully!')
        return redirect('room_settings', room_name=room_name)
    
    return render(request, 'chat/room_settings.html', {
        'room_obj': room_obj,
        'room_name': room_name,
        'online_members': online_members,
        'all_members': all_members,
        'banned_users': banned_users,
        'total_members': all_members.count(),
        'online_count': online_members.count(),
        'banned_count': banned_users.count(),
    })


@login_required
@require_POST
def kick_member(request):
    """Kick a member from the room"""
    room_name = request.POST.get('room_name', '').strip()
    username = request.POST.get('username', '').strip()
    
    if not room_name or not username:
        return JsonResponse({
            'success': False,
            'message': 'Room name and username are required.'
        })
    
    try:
        room_obj = get_object_or_404(Room, name=room_name)
        user_to_kick = get_object_or_404(User, username=username)
        
        # Only room host can kick members
        if not room_obj.is_host(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Only the room host can kick members.'
            })
        
        # Cannot kick the host
        if user_to_kick == request.user:
            return JsonResponse({
                'success': False,
                'message': 'You cannot kick yourself.'
            })
        
        # Kick the user
        room_obj.kick_user(user_to_kick)
        
        return JsonResponse({
            'success': True,
            'message': f'{username} has been kicked from the room.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while kicking the member.'
        })


@login_required
@require_POST
def ban_member(request):
    """Ban a member from the room"""
    room_name = request.POST.get('room_name', '').strip()
    username = request.POST.get('username', '').strip()
    reason = request.POST.get('reason', '').strip()
    
    if not room_name or not username:
        return JsonResponse({
            'success': False,
            'message': 'Room name and username are required.'
        })
    
    try:
        room_obj = get_object_or_404(Room, name=room_name)
        user_to_ban = get_object_or_404(User, username=username)
        
        # Only room host can ban members
        if not room_obj.is_host(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Only the room host can ban members.'
            })
        
        # Cannot ban the host
        if user_to_ban == request.user:
            return JsonResponse({
                'success': False,
                'message': 'You cannot ban yourself.'
            })
        
        # Check if user is already banned
        if room_obj.is_user_banned(user_to_ban):
            return JsonResponse({
                'success': False,
                'message': f'{username} is already banned from this room.'
            })
        
        # Ban the user
        room_obj.ban_user(user_to_ban, request.user, reason)
        
        return JsonResponse({
            'success': True,
            'message': f'{username} has been banned from the room.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while banning the member.'
        })


@login_required
@require_POST
def unban_member(request):
    """Unban a member from the room"""
    room_name = request.POST.get('room_name', '').strip()
    username = request.POST.get('username', '').strip()
    
    if not room_name or not username:
        return JsonResponse({
            'success': False,
            'message': 'Room name and username are required.'
        })
    
    try:
        room_obj = get_object_or_404(Room, name=room_name)
        user_to_unban = get_object_or_404(User, username=username)
        
        # Only room host can unban members
        if not room_obj.is_host(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Only the room host can unban members.'
            })
        
        # Check if user is actually banned
        if not room_obj.is_user_banned(user_to_unban):
            return JsonResponse({
                'success': False,
                'message': f'{username} is not banned from this room.'
            })
        
        # Unban the user
        room_obj.unban_user(user_to_unban)
        
        return JsonResponse({
            'success': True,
            'message': f'{username} has been unbanned from the room.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while unbanning the member.'
        })
