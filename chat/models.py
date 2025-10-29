from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def can_delete(self, user):
        """Check if user can delete this room (only creator can)"""
        return self.creator == user
    
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
