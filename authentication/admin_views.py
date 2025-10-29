from django.contrib import admin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import MFARecoveryRequest, BackupCode

@staff_member_required
def approve_recovery_request(request, request_id):
    """Approve an MFA recovery request and reset user's MFA"""
    recovery_request = get_object_or_404(MFARecoveryRequest, id=request_id)
    
    if recovery_request.resolved:
        messages.warning(request, "This request has already been resolved.")
        return redirect('admin:authentication_mfarecoveryrequest_changelist')
    
    if request.method == 'POST':
        user = recovery_request.user
        
        # Disable all TOTP devices for the user
        totp_devices = TOTPDevice.objects.filter(user=user)
        totp_count = totp_devices.count()
        totp_devices.delete()
        
        # Disable all unused backup codes
        backup_codes = BackupCode.objects.filter(user=user, used=False)
        backup_count = backup_codes.count()
        backup_codes.update(used=True, used_at=timezone.now())
        
        # Mark request as resolved
        recovery_request.resolved = True
        recovery_request.resolved_by = request.user
        recovery_request.resolved_at = timezone.now()
        recovery_request.save()
        
        # Send email notification to user
        try:
            send_mail(
                subject='MFA Recovery Request Approved - EverSpace Chat',
                message=f'''
Dear {user.get_full_name() or user.username},

Your MFA recovery request has been approved by our security team.

Your multi-factor authentication has been reset. You can now:
1. Log in with just your username and password
2. Set up new MFA when you access your account

Security Details:
- {totp_count} TOTP device(s) removed
- {backup_count} backup code(s) disabled
- Request processed by: {request.user.get_full_name() or request.user.username}
- Processed at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

If you did not request this recovery, please contact our support team immediately.

Best regards,
EverSpace Chat Security Team
                '''.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f"MFA reset successful, but email notification failed: {e}")
        
        messages.success(
            request, 
            f"Successfully approved MFA recovery for {user.username}. "
            f"Removed {totp_count} TOTP device(s) and disabled {backup_count} backup code(s). "
            f"User has been notified via email."
        )
        
        return redirect('admin:authentication_mfarecoveryrequest_changelist')
    
    context = {
        'recovery_request': recovery_request,
        'user': recovery_request.user,
        'totp_devices_count': TOTPDevice.objects.filter(user=recovery_request.user).count(),
        'backup_codes_count': BackupCode.objects.filter(user=recovery_request.user, used=False).count(),
        'title': f'Approve MFA Recovery for {recovery_request.user.username}',
    }
    
    return render(request, 'admin/authentication/approve_recovery.html', context)

@staff_member_required
def deny_recovery_request(request, request_id):
    """Deny an MFA recovery request"""
    recovery_request = get_object_or_404(MFARecoveryRequest, id=request_id)
    
    if recovery_request.resolved:
        messages.warning(request, "This request has already been resolved.")
        return redirect('admin:authentication_mfarecoveryrequest_changelist')
    
    if request.method == 'POST':
        denial_reason = request.POST.get('denial_reason', 'No reason provided')
        
        # Mark request as resolved (denied)
        recovery_request.resolved = True
        recovery_request.resolved_by = request.user
        recovery_request.resolved_at = timezone.now()
        recovery_request.save()
        
        # Send email notification to user
        try:
            send_mail(
                subject='MFA Recovery Request Denied - EverSpace Chat',
                message=f'''
Dear {recovery_request.user.get_full_name() or recovery_request.user.username},

Your MFA recovery request has been reviewed and unfortunately cannot be approved at this time.

Reason: {denial_reason}

What you can do:
1. If you still have access to your authenticator app, use your backup codes
2. Contact our support team if you believe this decision was made in error
3. Provide additional verification information if requested

Your account security remains intact with MFA still active.

If you have questions about this decision, please contact our support team.

Best regards,
EverSpace Chat Security Team
                '''.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recovery_request.user.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f"Request denied, but email notification failed: {e}")
        
        messages.success(
            request, 
            f"Denied MFA recovery request for {recovery_request.user.username}. User has been notified."
        )
        
        return redirect('admin:authentication_mfarecoveryrequest_changelist')
    
    context = {
        'recovery_request': recovery_request,
        'user': recovery_request.user,
        'title': f'Deny MFA Recovery for {recovery_request.user.username}',
    }
    
    return render(request, 'admin/authentication/deny_recovery.html', context)

@method_decorator(staff_member_required, name='dispatch')
class MFADashboardView(View):
    """Admin dashboard for MFA management"""
    
    def get(self, request):
        # Statistics
        total_users = MFARecoveryRequest.objects.values('user').distinct().count()
        pending_requests = MFARecoveryRequest.objects.filter(resolved=False).count()
        resolved_requests = MFARecoveryRequest.objects.filter(resolved=True).count()
        
        # Recent activity
        recent_requests = MFARecoveryRequest.objects.order_by('-created_at')[:10]
        recent_approvals = MFARecoveryRequest.objects.filter(
            resolved=True, 
            resolved_by__isnull=False
        ).order_by('-resolved_at')[:5]
        
        # Users with MFA enabled
        users_with_mfa = TOTPDevice.objects.filter(confirmed=True).count()
        
        context = {
            'title': 'MFA Management Dashboard',
            'total_users': total_users,
            'pending_requests': pending_requests,
            'resolved_requests': resolved_requests,
            'recent_requests': recent_requests,
            'recent_approvals': recent_approvals,
            'users_with_mfa': users_with_mfa,
        }
        
        return render(request, 'admin/authentication/mfa_dashboard.html', context)