#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import MFARecoveryRequest, BackupCode
from django_otp.plugins.otp_totp.models import TOTPDevice

def create_test_data():
    """Create test data for MFA recovery system"""
    
    print("Creating test data for MFA recovery system...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='demouser',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        user.set_password('demo123456')
        user.save()
        print(f"✅ Created user: {user.username}")
    else:
        print(f"ℹ️  User already exists: {user.username}")
    
    # Create TOTP device (simulating MFA setup)
    totp_device, created = TOTPDevice.objects.get_or_create(
        user=user,
        name='Demo Phone App',
        defaults={
            'confirmed': True,
            'key': 'JBSWY3DPEHPK3PXP'  # Sample key
        }
    )
    
    if created:
        print(f"✅ Created TOTP device: {totp_device.name}")
    else:
        print(f"ℹ️  TOTP device already exists: {totp_device.name}")
    
    # Create backup codes if they don't exist
    existing_codes = BackupCode.objects.filter(user=user, used=False).count()
    if existing_codes == 0:
        codes = BackupCode.generate_codes_for_user(user)
        print(f"✅ Generated {len(codes)} backup codes")
    else:
        print(f"ℹ️  User already has {existing_codes} unused backup codes")
    
    # Create recovery request if it doesn't exist
    recovery_request, created = MFARecoveryRequest.objects.get_or_create(
        user=user,
        resolved=False,
        defaults={
            'email': 'demo.recovery@gmail.com',
            'reason': '''I lost my phone during travel and no longer have access to my authenticator app. 
            
I need to recover my EverSpace account as I use it for work communications. 

I can provide:
- Alternative email verification
- Photo ID if needed
- Answer security questions

Please help me regain access to my account. Thank you!'''
        }
    )
    
    if created:
        print(f"✅ Created recovery request (ID: {recovery_request.id})")
    else:
        print(f"ℹ️  Recovery request already exists (ID: {recovery_request.id})")
    
    # Summary
    total_users = User.objects.count()
    total_requests = MFARecoveryRequest.objects.count()
    pending_requests = MFARecoveryRequest.objects.filter(resolved=False).count()
    total_totp = TOTPDevice.objects.filter(confirmed=True).count()
    total_backup_codes = BackupCode.objects.filter(used=False).count()
    
    print("\n" + "="*50)
    print("📊 SYSTEM SUMMARY:")
    print(f"👥 Total Users: {total_users}")
    print(f"🔐 Users with MFA: {total_totp}")
    print(f"🎫 Unused Backup Codes: {total_backup_codes}")
    print(f"📋 Total Recovery Requests: {total_requests}")
    print(f"⏳ Pending Requests: {pending_requests}")
    print("="*50)
    
    if pending_requests > 0:
        print("\n🎯 You can now test the admin interface!")
        print("1. Go to: http://127.0.0.1:8000/admin/")
        print("2. Login with: ryan / ryan123456")
        print("3. Click 'Mfa recovery requests' under Authentication")
        print("4. You'll see pending requests with Approve/Deny buttons")
        print("5. Click 'Approve & Reset MFA' to test the approval workflow")
    
    return True

if __name__ == '__main__':
    create_test_data()