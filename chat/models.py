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
    # Gift system
    evercoin = models.BigIntegerField(default=0, help_text='Virtual currency for gifts')
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
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'
    
    def can_be_deleted(self, user):
        """Check if message can be deleted by the user (within 2 minutes)"""
        if self.user != user or self.is_deleted:
            return False
        time_diff = timezone.now() - self.timestamp
        return time_diff.total_seconds() <= 120  # 2 minutes = 120 seconds
    
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


class Notification(models.Model):
    """Universal notification system for all events"""
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('friend_request', 'Friend Request'),
        ('friend_accepted', 'Friend Request Accepted'),
        ('kicked', 'Kicked from Room'),
        ('banned', 'Banned from Room'),
        ('room_deleted', 'Room Deleted'),
        ('transfer_ownership', 'Room Ownership Transferred'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)  # Link to relevant page
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Optional related objects
    room = models.ForeignKey('Room', on_delete=models.CASCADE, null=True, blank=True)
    private_message = models.ForeignKey(PrivateMessage, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.notification_type} for {self.recipient.username}: {self.title}'
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()
    
    @classmethod
    def create_message_notification(cls, sender, receiver, private_message):
        """Create notification for new private message"""
        return cls.objects.create(
            recipient=receiver,
            sender=sender,
            notification_type='message',
            title=f'New message from {sender.username}',
            message=private_message.content[:100],
            link=f'/friends/chat/{sender.username}/',
            private_message=private_message
        )
    
    @classmethod
    def create_friend_request_notification(cls, sender, receiver):
        """Create notification for friend request"""
        return cls.objects.create(
            recipient=receiver,
            sender=sender,
            notification_type='friend_request',
            title=f'{sender.username} sent you a friend request',
            message=f'{sender.username} wants to be your friend',
            link='/friends/'
        )
    
    @classmethod
    def create_friend_accepted_notification(cls, sender, receiver):
        """Create notification when friend request is accepted"""
        return cls.objects.create(
            recipient=sender,
            sender=receiver,
            notification_type='friend_accepted',
            title=f'{receiver.username} accepted your friend request',
            message=f'You and {receiver.username} are now friends!',
            link=f'/friends/chat/{receiver.username}/'
        )
    
    @classmethod
    def create_kick_notification(cls, kicked_user, room, kicked_by):
        """Create notification for being kicked from room"""
        return cls.objects.create(
            recipient=kicked_user,
            sender=kicked_by,
            notification_type='kicked',
            title=f'You were kicked from {room.name}',
            message=f'{kicked_by.username} removed you from room {room.name}',
            room=room,
            link='/chat/'
        )
    
    @classmethod
    def create_ban_notification(cls, banned_user, room, banned_by):
        """Create notification for being banned from room"""
        return cls.objects.create(
            recipient=banned_user,
            sender=banned_by,
            notification_type='banned',
            title=f'You were banned from {room.name}',
            message=f'{banned_by.username} banned you from room {room.name}',
            room=room,
            link='/chat/'
        )


class Gift(models.Model):
    """Predefined gifts that users can send"""
    ANIMATION_CHOICES = [
        ('dragon-fly', 'Dragon Flying'),
        ('hearts-rain', 'Hearts Rain'),
        ('fireworks', 'Fireworks Burst'),
        ('sparkle-spin', 'Sparkle Spin'),
        ('bounce', 'Bounce'),
        ('float', 'Float Up'),
        ('rotate-rainbow', 'Rainbow Rotate'),
        ('crystal-drop', 'Crystal Drop'),
        ('trophy-rise', 'Trophy Rise'),
        ('crown-fall', 'Crown Falling'),
        ('unicorn-gallop', 'Unicorn Gallop'),
        ('phoenix-burn', 'Phoenix Burn'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon_url = models.CharField(max_length=200)
    emoji = models.CharField(max_length=10, blank=True)
    rarity = models.CharField(
        max_length=20,
        choices=[
            ('common', 'Common'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
        ],
        default='common'
    )
    cost = models.IntegerField(default=100, help_text='Cost in Evercoin')
    animation = models.CharField(
        max_length=50,
        choices=ANIMATION_CHOICES,
        default='sparkle-spin'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rarity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.rarity}) - {self.cost} EC"


class GiftTransaction(models.Model):
    """Track gifts sent between users in rooms"""
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='transactions')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_gifts')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_gifts')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='gift_transactions')
    quantity = models.IntegerField(default=1)
    message = models.TextField(blank=True, max_length=200)
    sent_at = models.DateTimeField(default=timezone.now)
    intimacy_gained = models.IntegerField(default=0, help_text='Intimacy points gained from this gift')
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['receiver', '-sent_at']),
            models.Index(fields=['sender', '-sent_at']),
            models.Index(fields=['room', '-sent_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username} sent {self.quantity}x {self.gift.name} to {self.receiver.username}"


class Intimacy(models.Model):
    """Track intimacy points between two users (亲密度)"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intimacy_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intimacy_as_user2')
    points = models.IntegerField(default=0, help_text='Intimacy points (亲密度)')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user1', 'user2']]
        indexes = [
            models.Index(fields=['user1', '-points']),
            models.Index(fields=['user2', '-points']),
        ]
    
    def __str__(self):
        return f"亲密度 {self.user1.username} <-> {self.user2.username}: {self.points}"
    
    @staticmethod
    def get_intimacy(user_a, user_b):
        """Get intimacy points between two users"""
        if user_a.id > user_b.id:
            user_a, user_b = user_b, user_a
        
        intimacy, _ = Intimacy.objects.get_or_create(user1=user_a, user2=user_b)
        return intimacy.points
    
    @staticmethod
    def add_intimacy(user_a, user_b, points):
        """Add intimacy points between two users"""
        if user_a.id > user_b.id:
            user_a, user_b = user_b, user_a
        
        intimacy, _ = Intimacy.objects.get_or_create(user1=user_a, user2=user_b)
        intimacy.points += points
        intimacy.save()
        return intimacy


class GifPack(models.Model):
    """Collection/Category of GIFs"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=10, default='📦')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_gif_count(self):
        return self.gifs.filter(is_active=True).count()


class GifFile(models.Model):
    """Individual GIF file"""
    pack = models.ForeignKey(GifPack, on_delete=models.CASCADE, related_name='gifs')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    gif_file = models.FileField(upload_to='gifs/')
    thumbnail = models.ImageField(upload_to='gifs/thumbnails/', null=True, blank=True)
    tags = models.TextField(default='', help_text='Comma-separated tags')
    category = models.CharField(max_length=50, blank=True, default='')
    source = models.CharField(max_length=200, blank=True, default='')
    file_size = models.BigIntegerField(default=0)  # in bytes
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    duration = models.FloatField(default=0)  # in seconds
    is_animated = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['pack', 'order', 'title']
        indexes = [
            models.Index(fields=['pack', '-created_at']),
            models.Index(fields=['tags']),
        ]
    
    def __str__(self):
        return f"{self.pack.name} - {self.title}"
    
    def get_url(self):
        """Get GIF URL - handles both FileField objects and direct URLs"""
        if self.gif_file:
            gif_str = str(self.gif_file)
            # Check if it's a full URL (starts with http:// or https://)
            if gif_str.startswith(('http://', 'https://')):
                return gif_str
            # If it's a FileField object with a URL method, use it
            if hasattr(self.gif_file, 'url'):
                return self.gif_file.url
            # Otherwise, it's a local file path
            return f'/media/{gif_str}'
        return ''
    
    def increment_views(self):
        """Increment view counter"""
        self.views += 1
        self.save(update_fields=['views'])


class GifUsageLog(models.Model):
    """Track GIF usage in rooms"""
    gif = models.ForeignKey(GifFile, on_delete=models.CASCADE, related_name='usage_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gif_usages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='gif_usages')
    message_text = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['gif', '-sent_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} sent {self.gif.title} in {self.room.name}"


