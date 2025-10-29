from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string

class BackupCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backup_codes')
    code = models.CharField(max_length=10, unique=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'code']
        
    def __str__(self):
        return f"{self.user.username} - {self.code} ({'Used' if self.used else 'Available'})"
    
    @classmethod
    def generate_codes_for_user(cls, user, count=10):
        """Generate backup codes for a user"""
        # Delete existing unused codes
        cls.objects.filter(user=user, used=False).delete()
        
        codes = []
        for _ in range(count):
            # Generate a random 8-character code (4 letters + 4 numbers)
            letters = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(4))
            numbers = ''.join(secrets.choice(string.digits) for _ in range(4))
            code = letters + numbers
            
            # Ensure uniqueness
            while cls.objects.filter(code=code).exists():
                letters = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(4))
                numbers = ''.join(secrets.choice(string.digits) for _ in range(4))
                code = letters + numbers
            
            backup_code = cls.objects.create(user=user, code=code)
            codes.append(code)
        
        return codes
    
    @classmethod
    def verify_code(cls, user, code):
        """Verify and mark a backup code as used"""
        try:
            backup_code = cls.objects.get(
                user=user, 
                code=code.lower().replace('-', '').replace(' ', ''), 
                used=False
            )
            backup_code.used = True
            backup_code.used_at = timezone.now()
            backup_code.save()
            return True
        except cls.DoesNotExist:
            return False


class MFARecoveryRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_mfa_requests'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"MFA Recovery Request - {self.user.username} ({self.created_at.strftime('%Y-%m-%d')})"
