from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
import os


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='cover_images/', null=True, blank=True)
    # New: selectable cover choice (CSS/gradient or static predefined id). Takes precedence over uploaded cover.
    cover_choice = models.CharField(max_length=50, blank=True, default='')
    bio = models.TextField(max_length=500, blank=True, default='')
    pixel_avatar = models.CharField(max_length=50, blank=True, default='')
    username_changes_count = models.IntegerField(default=0)
    username_changes_year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def can_change_username(self):
        """Check if user can change username (max 3 times per year)"""
        current_year = timezone.now().year
        if self.username_changes_year != current_year:
            # Reset counter for new year
            self.username_changes_year = current_year
            self.username_changes_count = 0
            self.save()
        return self.username_changes_count < 3

    def record_username_change(self):
        """Record a username change"""
        current_year = timezone.now().year
        if self.username_changes_year != current_year:
            self.username_changes_year = current_year
            self.username_changes_count = 0
        self.username_changes_count += 1
        self.save()

    def get_profile_picture_url(self):
        """Get profile picture URL, fallback to pixel avatar or default"""
        if self.profile_picture:
            return self.profile_picture.url
        elif self.pixel_avatar:
            return f'/static/chat/images/pixel_avatars/{self.pixel_avatar}.png'
        else:
            return '/static/chat/images/default_avatar.png'

    def get_cover_image_url(self):
        """Resolve cover image: priority -> cover_choice preset -> uploaded cover -> default."""
        if self.cover_choice:
            # For gradient/CSS covers we return a sentinel path the template maps to a CSS class.
            # If cover_choice matches a file in static/chat/covers/<id>.jpg user can swap to actual images later.
            return f'/static/chat/covers/{self.cover_choice}.jpg'
        if self.cover_image:
            return self.cover_image.url
        return '/static/chat/images/default_cover.jpg'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile picture if it exists
        if self.profile_picture:
            self._resize_image(self.profile_picture.path, (300, 300))
        
        # Resize cover image if it exists
        if self.cover_image:
            self._resize_image(self.cover_image.path, (1200, 400))

    def _resize_image(self, image_path, size):
        """Resize image to specified size"""
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(image_path, optimize=True, quality=85)
        except Exception as e:
            print(f"Error resizing image: {e}")


class Room(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    name = models.CharField(max_length=7, unique=True)  # Exactly 7 digits
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    password = models.CharField(max_length=128, blank=True)  # For private rooms
    created_at = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def can_delete(self, user):
        """Check if user can delete this room (only creator can)"""
        return self.creator == user
    
    def is_private(self):
        """Check if room is private"""
        return self.visibility == 'private'
    
    def check_password(self, password):
        """Check if provided password matches room password"""
        return self.password == password if self.is_private() else True
    
    def is_host(self, user):
        """Check if user is the host of this room"""
        # Check if user has host role in the room members
        try:
            member = self.members.get(user=user, role='host')
            return True
        except RoomMember.DoesNotExist:
            # Fallback: check if user is the creator (for backwards compatibility)
            return self.creator == user
    
    def get_host_member(self):
        """Get the host member object"""
        try:
            return self.members.get(role='host')
        except:
            return None
    
    def get_online_members(self):
        """Get all currently online members"""
        return self.members.filter(status='online')
    
    def get_all_members(self):
        """Get all members (online and offline)"""
        return self.members.all()
    
    def is_user_banned(self, user):
        """Check if user is banned from this room"""
        return self.banned_users.filter(user=user, is_active=True).exists()
    
    def ban_user(self, user, banned_by, reason=""):
        """Ban a user from the room"""
        # Remove user from room members if they are in it
        self.members.filter(user=user).delete()
        
        # Create or update ban record
        ban, created = RoomBan.objects.get_or_create(
            room=self,
            user=user,
            defaults={
                'banned_by': banned_by,
                'reason': reason,
                'is_active': True
            }
        )
        if not created:
            ban.banned_by = banned_by
            ban.reason = reason
            ban.is_active = True
            ban.banned_at = timezone.now()
            ban.save()
        
        return ban
    
    def unban_user(self, user):
        """Unban a user from the room"""
        bans = self.banned_users.filter(user=user, is_active=True)
        for ban in bans:
            ban.unban()
    
    def kick_user(self, user):
        """Kick a user from the room (remove but don't ban)"""
        self.members.filter(user=user).delete()
    
    def add_member(self, user, role='member'):
        """Add a user as a member of the room"""
        # Check if user is banned
        if self.is_user_banned(user):
            return None
        
        member, created = RoomMember.objects.get_or_create(
            room=self,
            user=user,
            defaults={'role': role}
        )
        
        if created and role == 'host':
            # If this is a new host, make sure there's only one host
            self.members.filter(role='host').exclude(id=member.id).update(role='member')
        
        return member
    
    def update_description(self, new_description):
        """Update room description"""
        self.description = new_description
        self.save()
    
    def transfer_ownership(self, new_owner):
        """Transfer room ownership to another user"""
        # Remove host role from current owner
        if self.creator:
            old_host = self.members.filter(user=self.creator, role='host').first()
            if old_host:
                old_host.role = 'member'
                old_host.save()
        
        # Set new owner as creator
        self.creator = new_owner
        self.save()
        
        # Add new owner as host member
        self.add_member(new_owner, role='host')
        
        return True
    
    class Meta:
        ordering = ['name']

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'
    
    class Meta:
        ordering = ['timestamp']


class RoomMember(models.Model):
    """Track users who have joined a room and their status"""
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('member', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    joined_at = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['room', 'user']
        ordering = ['-last_seen']
    
    def __str__(self):
        return f'{self.user.username} in {self.room.name} ({self.role})'
    
    def is_host(self):
        """Check if user is the room host"""
        return self.role == 'host'
    
    def set_online(self):
        """Mark user as online in the room"""
        self.status = 'online'
        self.last_seen = timezone.now()
        self.save()
    
    def set_offline(self):
        """Mark user as offline in the room"""
        self.status = 'offline'
        self.last_seen = timezone.now()
        self.save()


class RoomBan(models.Model):
    """Track users banned from rooms"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='banned_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_bans')
    banned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_bans')
    reason = models.TextField(blank=True)
    banned_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['room', 'user']
        ordering = ['-banned_at']
    
    def __str__(self):
        return f'{self.user.username} banned from {self.room.name}'
    
    def unban(self):
        """Unban the user"""
        self.is_active = False
        self.save()


class Friendship(models.Model):
    """Track friendships between users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('blocked', 'Blocked'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['sender', 'receiver']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username} ({self.status})'
    
    def accept(self):
        """Accept the friend request"""
        self.status = 'accepted'
        self.save()
    
    def decline(self):
        """Decline the friend request"""
        self.status = 'declined'
        self.save()
    
    def block(self):
        """Block the user"""
        self.status = 'blocked'
        self.save()
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            models.Q(sender=user1, receiver=user2, status='accepted') |
            models.Q(sender=user2, receiver=user1, status='accepted')
        ).exists()
    
    @classmethod
    def get_friendship(cls, user1, user2):
        """Get friendship between two users"""
        try:
            return cls.objects.get(
                models.Q(sender=user1, receiver=user2) |
                models.Q(sender=user2, receiver=user1)
            )
        except cls.DoesNotExist:
            return None


class PrivateMessage(models.Model):
    """Private messages between friends"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_private_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_private_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}: {self.content[:50]}'
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save()
