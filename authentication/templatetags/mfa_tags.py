from django import template
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice

register = template.Library()

@register.filter
def has_mfa_enabled(user):
    """Check if user has MFA enabled"""
    return user_has_device(user)

@register.filter  
def mfa_devices_count(user):
    """Get count of confirmed TOTP devices for user"""
    return TOTPDevice.objects.filter(user=user, confirmed=True).count()

@register.simple_tag
def mfa_status(user):
    """Get comprehensive MFA status for user"""
    if not user.is_authenticated:
        return {
            'enabled': False,
            'devices_count': 0,
            'has_backup_codes': False
        }
    
    from authentication.models import BackupCode
    
    enabled = user_has_device(user)
    devices_count = TOTPDevice.objects.filter(user=user, confirmed=True).count()
    unused_backup_codes = BackupCode.objects.filter(user=user, used=False).count()
    
    return {
        'enabled': enabled,
        'devices_count': devices_count,
        'has_backup_codes': unused_backup_codes > 0,
        'backup_codes_count': unused_backup_codes
    }