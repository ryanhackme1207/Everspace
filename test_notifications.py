import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from django.contrib.auth.models import User
from chat.models import Notification, PrivateMessage, Friendship

print("=" * 60)
print("NOTIFICATION LINK TEST")
print("=" * 60)

# Get or create test users
try:
    user1 = User.objects.get(username='ryanadmin')
    print(f"✓ Found user: {user1.username}")
except User.DoesNotExist:
    print("✗ User 'ryanadmin' not found")
    user1 = None

try:
    user2 = User.objects.get(username='ryanhackme123')
    print(f"✓ Found user: {user2.username}")
except User.DoesNotExist:
    print("✗ User 'ryanhackme123' not found")
    user2 = None

if user1 and user2:
    print("\n" + "=" * 60)
    print("TESTING NOTIFICATION CREATION")
    print("=" * 60)
    
    # Test 1: Create a message notification
    print("\n1. Testing message notification...")
    try:
        # Create a private message
        msg = PrivateMessage.objects.create(
            sender=user1,
            receiver=user2,
            content="Test message for notification"
        )
        
        # Create notification
        notif = Notification.create_message_notification(user1, user2, msg)
        print(f"   ✓ Created notification: {notif.title}")
        print(f"   ✓ Link: {notif.link}")
        print(f"   ✓ Type: {notif.notification_type}")
        
        # Verify link format
        if notif.link.startswith('/friends/chat/'):
            print(f"   ✓ Link format is CORRECT")
        else:
            print(f"   ✗ Link format is WRONG: {notif.link}")
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 2: Friend request notification
    print("\n2. Testing friend request notification...")
    try:
        notif = Notification.create_friend_request_notification(user1, user2)
        print(f"   ✓ Created notification: {notif.title}")
        print(f"   ✓ Link: {notif.link}")
        print(f"   ✓ Type: {notif.notification_type}")
        
        if notif.link == '/friends/':
            print(f"   ✓ Link format is CORRECT")
        else:
            print(f"   ✗ Link format is WRONG: {notif.link}")
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 3: Friend accepted notification
    print("\n3. Testing friend accepted notification...")
    try:
        notif = Notification.create_friend_accepted_notification(user1, user2)
        print(f"   ✓ Created notification: {notif.title}")
        print(f"   ✓ Link: {notif.link}")
        print(f"   ✓ Type: {notif.notification_type}")
        
        if notif.link.startswith('/friends/chat/'):
            print(f"   ✓ Link format is CORRECT")
        else:
            print(f"   ✗ Link format is WRONG: {notif.link}")
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Show all notifications for user2
    print("\n" + "=" * 60)
    print(f"ALL NOTIFICATIONS FOR {user2.username}")
    print("=" * 60)
    
    notifications = Notification.objects.filter(recipient=user2).order_by('-created_at')[:10]
    
    if notifications:
        for i, notif in enumerate(notifications, 1):
            print(f"\n{i}. {notif.title}")
            print(f"   Type: {notif.notification_type}")
            print(f"   Link: {notif.link}")
            print(f"   Sender: {notif.sender.username if notif.sender else 'System'}")
            print(f"   Read: {'Yes' if notif.is_read else 'No'}")
            print(f"   Created: {notif.created_at}")
    else:
        print("No notifications found")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

else:
    print("\n✗ Cannot run tests without both test users")
