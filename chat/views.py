from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.decorators import otp_required
from django_otp import user_has_device
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Room, Message, RoomMember, RoomBan, Friendship, PrivateMessage, UserProfile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from functools import wraps
import os
import json

# Temporary diagnostic middleware (can be moved to separate file later)
class KickBanDiagnosticMiddleware:
    """Middleware to log details for kick/ban POST requests before redirect logic."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only inspect the problematic endpoints
        if request.path in ['/chat/kick-member/', '/chat/ban-member/'] and request.method == 'POST':
            print('[DIAG MIDDLEWARE] Path:', request.path)
            print('[DIAG MIDDLEWARE] User authenticated:', request.user.is_authenticated)
            print('[DIAG MIDDLEWARE] Session key:', request.session.session_key)
            print('[DIAG MIDDLEWARE] Headers X-Requested-With:', request.headers.get('X-Requested-With'))
            print('[DIAG MIDDLEWARE] Content-Type:', request.content_type)
        return self.get_response(request)

def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def ajax_login_required(view_func):
    """
    Decorator for AJAX views that require authentication.
    Returns JSON error instead of redirecting to login page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if is_ajax(request):
                return JsonResponse({
                    'success': False,
                    'message': 'Authentication required. Please log in.'
                }, status=401)
            return redirect('auth_login') # Or your login URL
        return view_func(request, *args, **kwargs)
    return wrapper

def landing_page(request):
    """Modern landing page with animations and introduction"""
    if request.user.is_authenticated:
        return redirect('chat_index')
    return render(request, 'chat/landing.html')

def test_endpoint(request):
    """Test endpoint to verify AJAX connectivity"""
    return JsonResponse({
        'success': True,
        'message': 'Test endpoint working',
        'method': request.method,
        'user_authenticated': request.user.is_authenticated,
        'user': str(request.user) if request.user.is_authenticated else 'Anonymous'
    })

@login_required
def index(request):
    # Check if user has MFA enabled (but don't show automatic message)
    user_has_mfa = user_has_device(request.user)
    
    rooms = Room.objects.all()
    
    # Get friends data if user is authenticated
    friends = []
    incoming_requests = []
    outgoing_requests = []
    
    if request.user.is_authenticated:
        # Get accepted friendships
        friends_relationships = Friendship.objects.filter(
            models.Q(sender=request.user) | models.Q(receiver=request.user),
            status='accepted'
        )
        
        friends = []
        for friendship in friends_relationships:
            friend = friendship.receiver if friendship.sender == request.user else friendship.sender
            friends.append(friend)
        
        # Get pending incoming requests
        incoming_requests = Friendship.objects.filter(
            receiver=request.user,
            status='pending'
        ).select_related('sender')
        
        # Get pending outgoing requests
        outgoing_requests = Friendship.objects.filter(
            sender=request.user,
            status='pending'
        ).select_related('receiver')
    
    return render(request, 'chat/index.html', {
        'rooms': rooms,
        'user_has_mfa': user_has_mfa,
        'friends': friends,
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
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
        messages.error(request, f'Room "{room_name}" does not exist or has been deleted.')
        return redirect('chat_index')
    
    # Check if user is banned from this room. Avoid spamming the same message across redirects.
    if room_obj.is_user_banned(request.user):
        ban_flag_key = f'banned_notice_shown_{room_name}'
        if not request.session.get(ban_flag_key):
            # Use extra_tags so templates can suppress room-ban messages outside chat contexts
            messages.error(request, f'You are banned from room "{room_name}". Contact the room host if you believe this is an error.', extra_tags='room-ban')
            request.session[ban_flag_key] = True
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
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
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
        
        # Notify all connected users before deleting the room
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_name}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'room_deleted',
                'message': f'Room "{room_name}" has been deleted by the creator.'
            }
        )
        
        # Clear active users from cache
        from django.core.cache import cache
        cache_key = f"active_users_{room_name}"
        cache.delete(cache_key)
        
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
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    room_obj = get_object_or_404(Room, name=room_name)
    
    if not room_obj.can_delete(request.user):
        messages.error(request, 'Only the room creator can delete this room.')
        return redirect('chat_room', room_name=room_name)
    
    if request.method == 'POST':
        # Notify all connected users before deleting the room
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_name}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'room_deleted',
                'message': f'Room "{room_name}" has been deleted by the creator.'
            }
        )
        
        # Clear active users from cache
        from django.core.cache import cache
        cache_key = f"active_users_{room_name}"
        cache.delete(cache_key)
        
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
    
    # Presence: derive online from cache active_users to avoid stale DB status
    from django.core.cache import cache
    cache_key = f"active_users_{room_name}"
    active_cache = cache.get(cache_key, {})  # dict of username -> {username, display_name}
    active_usernames = {data['username'] for data in active_cache.values() if 'username' in data}

    all_members = room_obj.get_all_members().select_related('user')
    online_members = [m for m in all_members if m.user.username in active_usernames]
    offline_members = [m for m in all_members if m.user.username not in active_usernames]
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
        'offline_members': offline_members,
        'all_members': all_members,
        'banned_users': banned_users,
        'total_members': all_members.count(),
        'online_count': len(online_members),
        'banned_count': banned_users.count(),
    })


@ajax_login_required
@require_POST
def kick_member(request):
    """Kick a member from the room"""
    print("[KICK DEBUG] ====== KICK_MEMBER VIEW CALLED ======")
    print(f"[KICK DEBUG] Request method: {request.method}")
    print(f"[KICK DEBUG] User authenticated: {request.user.is_authenticated}")
    is_ajax_req = is_ajax(request)
    print(f"[KICK DEBUG] Is AJAX: {is_ajax_req}")
    print(f"[KICK DEBUG] Content-Type: {request.content_type}")

    room_name = ''
    username = ''
    raw_payload = None
    # Accept application/json plus possible charset suffix
    if request.content_type and request.content_type.startswith('application/json'):
        try:
            raw_payload = json.loads(request.body or b'{}')
            room_name = raw_payload.get('room_name', '').strip()
            username = raw_payload.get('username', '').strip()
        except json.JSONDecodeError:
            if is_ajax_req:
                return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    else:
        # Fallback for form-urlencoded or multipart
        room_name = request.POST.get('room_name', '').strip()
        username = request.POST.get('username', '').strip()
        raw_payload = request.POST.dict()

    print(f"[KICK DEBUG] Parsed room_name='{room_name}' username='{username}' payload={raw_payload}")
    
    if not room_name or not username:
        if is_ajax_req:
            return JsonResponse({'success': False,'message': 'Room name and username are required.'})
        messages.error(request, 'Room name and username are required.')
        return redirect('chat_index')
    
    try:
        room_obj = Room.objects.get(name=room_name)
        user_to_kick = User.objects.get(username=username)
        
        # Only room host can kick members
        is_host = room_obj.is_host(request.user)
        print(f"[KICK DEBUG] Is user host? {is_host}")
        if not is_host:
            if is_ajax_req:
                return JsonResponse({'success': False,'message': 'Only the room host can kick members.'})
            messages.error(request, 'Only the room host can kick members.')
            return redirect('chat_room', room_name=room_name)
        
        # Cannot kick the host
        if user_to_kick == request.user:
            if is_ajax_req:
                return JsonResponse({'success': False,'message': 'You cannot kick yourself.'})
            messages.error(request, 'You cannot kick yourself.')
            return redirect('chat_room', room_name=room_name)
        
        # Check if user is actually a member
        if not room_obj.members.filter(user=user_to_kick).exists():
            if is_ajax_req:
                return JsonResponse({'success': False,'message': f'{username} is not a member of this room.'})
            messages.error(request, f'{username} is not a member of this room.')
            return redirect('chat_room', room_name=room_name)
        
        # Kick the user
        room_obj.kick_user(user_to_kick)
        
        # Send WebSocket notification to kick user from the room
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_name}'
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'user_kicked',
                'username': username,
                'message': 'You have been kicked from this room.'
            }
        )
        
        if is_ajax_req:
            return JsonResponse({'success': True,'message': f'{username} has been kicked from the room.'})
        messages.success(request, f'{username} has been kicked from the room.')
        return redirect('chat_room', room_name=room_name)
        
    except Room.DoesNotExist:
        if is_ajax_req:
            return JsonResponse({'success': False,'message': 'Room not found.'})
        messages.error(request, 'Room not found.')
        return redirect('chat_index')
    except User.DoesNotExist:
        if is_ajax_req:
            return JsonResponse({'success': False,'message': 'User not found.'})
        messages.error(request, 'User not found.')
        return redirect('chat_room', room_name=room_name or 'chat_index')
    except Exception as e:
        if is_ajax_req:
            return JsonResponse({'success': False,'message': f'An error occurred while kicking the member: {str(e)}'})
        messages.error(request, 'An error occurred while kicking the member.')
        return redirect('chat_room', room_name=room_name or 'chat_index')


@ajax_login_required
@require_POST
def ban_member(request):
    """Ban a member from the room"""
    print("[BAN DEBUG] ====== BAN_MEMBER VIEW CALLED ======")
    print(f"[BAN DEBUG] Request method: {request.method}")
    print(f"[BAN DEBUG] User authenticated: {request.user.is_authenticated}")
    is_ajax_req = is_ajax(request)
    print(f"[BAN DEBUG] Is AJAX: {is_ajax_req}")
    print(f"[BAN DEBUG] Content-Type: {request.content_type}")

    room_name = ''
    username = ''
    reason = ''
    raw_payload = None
    # Accept application/json plus possible charset suffix
    if request.content_type and request.content_type.startswith('application/json'):
        try:
            raw_payload = json.loads(request.body or b'{}')
            room_name = raw_payload.get('room_name', '').strip()
            username = raw_payload.get('username', '').strip()
            reason = raw_payload.get('reason', '').strip()
        except json.JSONDecodeError:
            if is_ajax_req:
                return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    else:
        room_name = request.POST.get('room_name', '').strip()
        username = request.POST.get('username', '').strip()
        reason = request.POST.get('reason', '').strip()
        raw_payload = request.POST.dict()

    print(f"[BAN DEBUG] Parsed room_name='{room_name}' username='{username}' reason='{reason}' payload={raw_payload}")
    
    if not room_name or not username:
        return JsonResponse({
            'success': False,
            'message': 'Room name and username are required.'
        })
    
    try:
        room_obj = Room.objects.get(name=room_name)
        user_to_ban = User.objects.get(username=username)
        
        # Only room host can ban members
        if not room_obj.is_host(request.user):
            if is_ajax_req:
                return JsonResponse({'success': False,'message': 'Only the room host can ban members.'})
            messages.error(request, 'Only the room host can ban members.')
            return redirect('chat_room', room_name=room_name)
        
        # Cannot ban the host
        if user_to_ban == request.user:
            if is_ajax_req:
                return JsonResponse({'success': False,'message': 'You cannot ban yourself.'})
            messages.error(request, 'You cannot ban yourself.')
            return redirect('chat_room', room_name=room_name)
        
        # Check if user is already banned
        if room_obj.is_user_banned(user_to_ban):
            if is_ajax_req:
                return JsonResponse({'success': False,'message': f'{username} is already banned from this room.'})
            messages.error(request, f'{username} is already banned from this room.')
            return redirect('chat_room', room_name=room_name)
        
        # Ban the user
        room_obj.ban_user(user_to_ban, request.user, reason)
        
        # Send WebSocket notification to ban user from the room
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_name}'
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'user_banned',
                'username': username,
                'message': f'You have been banned from this room. Reason: {reason}' if reason else 'You have been banned from this room.'
            }
        )
        
        if is_ajax_req:
            return JsonResponse({'success': True,'message': f'{username} has been banned from the room.'})
        messages.success(request, f'{username} has been banned from the room.')
        return redirect('chat_room', room_name=room_name)
        
    except Room.DoesNotExist:
        if is_ajax_req:
            return JsonResponse({'success': False,'message': 'Room not found.'})
        messages.error(request, 'Room not found.')
        return redirect('chat_index')
    except User.DoesNotExist:
        if is_ajax_req:
            return JsonResponse({'success': False,'message': 'User not found.'})
        messages.error(request, 'User not found.')
        return redirect('chat_room', room_name=room_name or 'chat_index')
    except Exception as e:
        if is_ajax_req:
            return JsonResponse({'success': False,'message': f'An error occurred while banning the member: {str(e)}'})
        messages.error(request, 'An error occurred while banning the member.')
        return redirect('chat_room', room_name=room_name or 'chat_index')


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


@login_required
@require_POST
def send_friend_request(request):
    """Send a friend request to another user or remove a friend"""
    username = request.POST.get('username', '').strip()
    action = request.POST.get('action', 'add')  # 'add' or 'remove'
    
    if not username:
        return JsonResponse({
            'success': False,
            'message': 'Username is required.'
        })
    
    try:
        target_user = get_object_or_404(User, username=username)
        
        # Cannot perform action on yourself
        if target_user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'You cannot perform this action on yourself.'
            })
        
        if action == 'remove':
            # Remove friendship
            existing_friendship = Friendship.get_friendship(request.user, target_user)
            if existing_friendship and existing_friendship.status == 'accepted':
                existing_friendship.delete()
                return JsonResponse({
                    'success': True,
                    'message': f'{username} has been removed from your friends.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'You are not friends with this user.'
                })
        
        else:  # action == 'add'
            # Check if friendship already exists
            existing_friendship = Friendship.get_friendship(request.user, target_user)
            if existing_friendship:
                if existing_friendship.status == 'accepted':
                    return JsonResponse({
                        'success': False,
                        'message': f'You are already friends with {username}.'
                    })
                elif existing_friendship.status == 'pending':
                    return JsonResponse({
                        'success': False,
                        'message': f'Friend request to {username} is already pending.'
                    })
                elif existing_friendship.status == 'blocked':
                    return JsonResponse({
                        'success': False,
                        'message': f'You cannot send a friend request to {username}.'
                    })
            
            # Create friend request
            friendship = Friendship.objects.create(
                sender=request.user,
                receiver=target_user,
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Friend request sent to {username}!'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while processing your request.'
        })


@login_required
@require_POST
def respond_friend_request(request):
    """Accept or decline a friend request"""
    request_id = request.POST.get('request_id')
    status = request.POST.get('status')  # 'accepted', 'declined', or 'cancelled'
    
    if not request_id or not status:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request parameters.'
        })
    
    try:
        if status == 'cancelled':
            # User is cancelling their own outgoing request
            friendship = get_object_or_404(Friendship, id=request_id, sender=request.user, status='pending')
            friendship.delete()
            return JsonResponse({
                'success': True,
                'message': 'Friend request cancelled.'
            })
        else:
            # User is responding to an incoming request
            friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user, status='pending')
        
        if status == 'accepted':
            friendship.accept()
            message = f'You are now friends with {friendship.sender.username}!'
        elif status == 'declined':
            friendship.decline()
            message = f'Friend request from {friendship.sender.username} declined.'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status.'
            })
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while processing the friend request.'
        })


@ajax_login_required
@require_POST
def transfer_ownership(request):
    """Transfer room ownership to another user"""
    
    print("[TRANSFER DEBUG] ====== TRANSFER_OWNERSHIP VIEW CALLED ======")
    print(f"[TRANSFER DEBUG] Request method: {request.method}")
    print(f"[TRANSFER DEBUG] User authenticated: {request.user.is_authenticated}")
    
    try:
        data = json.loads(request.body)
        room_name = data.get('room_name', '').strip()
        username = data.get('username', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    
    print(f"[TRANSFER DEBUG] Room name: '{room_name}'")
    print(f"[TRANSFER DEBUG] Username: '{username}'")
    
    if not room_name or not username:
        return JsonResponse({
            'success': False,
            'message': 'Room name and username are required.'
        })
    
    try:
        room_obj = Room.objects.get(name=room_name)
        new_owner = User.objects.get(username=username)
        
        # Only current host can transfer ownership
        if not room_obj.is_host(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Only the room host can transfer ownership.'
            })
        
        # Cannot transfer to yourself
        if new_owner == request.user:
            return JsonResponse({
                'success': False,
                'message': 'You are already the owner.'
            })
        
        # Check if new owner is a member of the room
        if not room_obj.members.filter(user=new_owner).exists():
            return JsonResponse({
                'success': False,
                'message': f'{username} must be a member of the room to receive ownership.'
            })
        
        # Transfer ownership
        room_obj.transfer_ownership(new_owner)
        
        # Send WebSocket notification
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_name}'
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'ownership_transferred',
                'old_owner': request.user.username,
                'new_owner': username,
                'message': f'Room ownership has been transferred to {username}'
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Ownership transferred to {username} successfully.'
        })
        
    except Room.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Room not found.'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found.'
        })
    except Exception as e:
        print(f"[TRANSFER DEBUG] Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'An error occurred while transferring ownership: {str(e)}'
        })


@login_required
def friends_list(request):
    """Display user's friends list"""
    # Get accepted friendships
    friends = []
    friendships = Friendship.objects.filter(
        models.Q(sender=request.user, status='accepted') |
        models.Q(receiver=request.user, status='accepted')
    )
    
    for friendship in friendships:
        friend = friendship.receiver if friendship.sender == request.user else friendship.sender
        friends.append({
            'user': friend,
            'is_online': False,  # TODO: Implement online status tracking
            'unread_count': PrivateMessage.objects.filter(
                sender=friend, receiver=request.user, is_read=False
            ).count()
        })
    
    # Get pending friend requests
    pending_requests = Friendship.objects.filter(
        receiver=request.user, status='pending'
    )
    
    return render(request, 'chat/friends.html', {
        'friends': friends,
        'pending_requests': pending_requests,
    })


@login_required
def private_chat(request, username):
    """Private chat with a friend"""
    friend = get_object_or_404(User, username=username)
    
    # Check if users are friends
    if not Friendship.are_friends(request.user, friend):
        messages.error(request, f'You are not friends with {username}.')
        return redirect('friends_list')
    
    # Get conversation messages
    messages_list = PrivateMessage.objects.filter(
        models.Q(sender=request.user, receiver=friend) |
        models.Q(sender=friend, receiver=request.user)
    ).order_by('timestamp')[:50]
    
    # Mark messages from friend as read
    PrivateMessage.objects.filter(
        sender=friend, receiver=request.user, is_read=False
    ).update(is_read=True)
    
    return render(request, 'chat/private_chat.html', {
        'friend': friend,
        'messages': messages_list,
    })


@login_required
@require_POST
def send_private_message(request):
    """Send a private message to a friend"""
    username = request.POST.get('username', '').strip()
    content = request.POST.get('content', '').strip()
    
    if not username or not content:
        return JsonResponse({
            'success': False,
            'message': 'Username and message content are required.'
        })
    
    try:
        receiver = get_object_or_404(User, username=username)
        
        # Check if users are friends
        if not Friendship.are_friends(request.user, receiver):
            return JsonResponse({
                'success': False,
                'message': 'You can only send messages to friends.'
            })
        
        # Create private message
        message = PrivateMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully!',
            'message_data': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'sender': message.sender.username
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while sending the message.'
        })


# Profile Management Views
@login_required
def edit_profile(request):
    """Display and handle profile editing"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Define available pixel avatars
    pixel_avatars = [
        'robot', 'alien', 'knight', 'wizard', 'ninja', 'pirate', 'cat', 'dog',
        'dragon', 'unicorn', 'ghost', 'monster', 'astronaut', 'viking', 'samurai', 'mage'
    ]
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_basic_info':
            # Update basic info (username, first name, last name)
            new_username = request.POST.get('username', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            
            # Validate username change
            if new_username != request.user.username:
                if not profile.can_change_username():
                    messages.error(request, 'You have reached the maximum number of username changes for this year (3).')
                    return redirect('edit_profile')
                
                # Check if username is available
                if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                    messages.error(request, 'Username is already taken.')
                    return redirect('edit_profile')
                
                # Validate username format
                if len(new_username) < 3 or len(new_username) > 30:
                    messages.error(request, 'Username must be between 3 and 30 characters.')
                    return redirect('edit_profile')
                
                if not new_username.replace('_', '').replace('-', '').isalnum():
                    messages.error(request, 'Username can only contain letters, numbers, underscores, and hyphens.')
                    return redirect('edit_profile')
                
                # Update username and record change
                request.user.username = new_username
                profile.record_username_change()
            
            # Update names
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            
            messages.success(request, 'Basic information updated successfully!')
            
        elif action == 'update_bio':
            # Update bio
            bio = request.POST.get('bio', '').strip()
            if len(bio) > 500:
                messages.error(request, 'Bio cannot exceed 500 characters.')
            else:
                profile.bio = bio
                profile.save()
                messages.success(request, 'Bio updated successfully!')
                
        elif action == 'set_pixel_avatar':
            # Set pixel avatar
            pixel_avatar = request.POST.get('pixel_avatar')
            if pixel_avatar in pixel_avatars:
                profile.pixel_avatar = pixel_avatar
                # Clear uploaded profile picture when setting pixel avatar
                if profile.profile_picture:
                    profile.profile_picture.delete()
                    profile.profile_picture = None
                profile.save()
                messages.success(request, 'Pixel avatar updated successfully!')
            else:
                messages.error(request, 'Invalid pixel avatar selection.')
        
        return redirect('edit_profile')
    
    context = {
        'profile': profile,
        'pixel_avatars': pixel_avatars,
        'remaining_username_changes': 3 - profile.username_changes_count if profile.can_change_username() else 0,
        'can_change_username': profile.can_change_username(),
    }
    
    return render(request, 'chat/edit_profile.html', context)


@login_required
@require_POST
def upload_profile_picture(request):
    """Handle profile picture upload"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if 'profile_picture' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No file uploaded.'})
    
    file = request.FILES['profile_picture']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return JsonResponse({'success': False, 'message': 'Only JPEG, PNG, GIF, and WebP images are allowed.'})
    
    # Validate file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        return JsonResponse({'success': False, 'message': 'File size cannot exceed 5MB.'})
    
    try:
        # Delete old profile picture if exists
        if profile.profile_picture:
            profile.profile_picture.delete()
        
        # Clear pixel avatar when uploading custom picture
        profile.pixel_avatar = ''
        profile.profile_picture = file
        profile.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Profile picture updated successfully!',
            'image_url': profile.get_profile_picture_url()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred while uploading the image.'})


@login_required
@require_POST
def upload_cover_image(request):
    """Handle cover image upload"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if 'cover_image' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No file uploaded.'})
    
    file = request.FILES['cover_image']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return JsonResponse({'success': False, 'message': 'Only JPEG, PNG, GIF, and WebP images are allowed.'})
    
    # Validate file size (max 10MB)
    if file.size > 10 * 1024 * 1024:
        return JsonResponse({'success': False, 'message': 'File size cannot exceed 10MB.'})
    
    try:
        # Delete old cover image if exists
        if profile.cover_image:
            profile.cover_image.delete()
        
        profile.cover_image = file
        profile.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Cover image updated successfully!',
            'image_url': profile.get_cover_image_url()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred while uploading the image.'})


@login_required
def view_profile(request, username=None):
    """View a user's profile"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': user == request.user,
    }
    
    return render(request, 'chat/view_profile.html', context)
