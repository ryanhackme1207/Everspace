"""Test script to verify friendship and messaging system.
Run: python test_friendship.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from django.contrib.auth.models import User
from chat.models import Friendship, PrivateMessage

def test_friendship():
    print("\n=== Testing Friendship System ===\n")
    
    # Get all users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    for user in users:
        print(f"  - {user.username}")
    
    # Get all friendships
    friendships = Friendship.objects.all()
    print(f"\nTotal friendships: {friendships.count()}")
    for friendship in friendships:
        print(f"  - {friendship.sender.username} -> {friendship.receiver.username} ({friendship.status})")
    
    # Check accepted friendships
    accepted = Friendship.objects.filter(status='accepted')
    print(f"\nAccepted friendships: {accepted.count()}")
    for friendship in accepted:
        user1 = friendship.sender
        user2 = friendship.receiver
        are_friends = Friendship.are_friends(user1, user2)
        print(f"  - {user1.username} & {user2.username}: are_friends={are_friends}")
    
    # Check pending friendships
    pending = Friendship.objects.filter(status='pending')
    print(f"\nPending friendships: {pending.count()}")
    for friendship in pending:
        print(f"  - {friendship.sender.username} -> {friendship.receiver.username}")
    
    # Check private messages
    messages = PrivateMessage.objects.all().order_by('-timestamp')[:10]
    print(f"\nRecent private messages: {messages.count()}")
    for msg in messages:
        print(f"  - {msg.sender.username} -> {msg.receiver.username}: {msg.content[:50]}...")
    
    print("\n=== Test Complete ===\n")

if __name__ == '__main__':
    test_friendship()
