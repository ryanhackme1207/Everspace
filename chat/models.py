from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
