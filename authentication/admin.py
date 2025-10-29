from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import BackupCode, MFARecoveryRequest

@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code_preview', 'used', 'created_at', 'used_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['code', 'created_at', 'used_at']
    ordering = ['-created_at']
    
    def code_preview(self, obj):
        return f"{obj.code[:2]}**-**{obj.code[-2:]}"
    code_preview.short_description = "Code Preview"
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing

@admin.register(MFARecoveryRequest)
class MFARecoveryRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'status_badge', 'created_at', 'resolved_by', 'action_buttons']
    list_filter = ['resolved', 'created_at']
    search_fields = ['user__username', 'user__email', 'email', 'reason']
    readonly_fields = ['created_at', 'resolved_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'email', 'reason', 'created_at')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_at', 'resolved_by'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.resolved:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Resolved</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
            )
    status_badge.short_description = "Status"
    
    def action_buttons(self, obj):
        if not obj.resolved:
            return format_html(
                '<a class="button" href="/admin/authentication/mfarecoveryrequest/{}/approve/" '
                'style="background: green; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin-right: 5px;">Approve & Reset MFA</a>'
                '<a class="button" href="/admin/authentication/mfarecoveryrequest/{}/deny/" '
                'style="background: red; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">Deny Request</a>',
                obj.pk, obj.pk
            )
        return format_html('<span style="color: gray;">No actions needed</span>')
    action_buttons.short_description = "Actions"
    action_buttons.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        from . import admin_views
        
        custom_urls = [
            path('<int:request_id>/approve/', admin_views.approve_recovery_request, name='approve_recovery'),
            path('<int:request_id>/deny/', admin_views.deny_recovery_request, name='deny_recovery'),
        ]
        return custom_urls + urls
    
    def save_model(self, request, obj, form, change):
        if change and obj.resolved and not obj.resolved_by:
            obj.resolved_by = request.user
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)

# Custom admin actions
def approve_mfa_recovery(modeladmin, request, queryset):
    """Approve MFA recovery requests and reset user MFA"""
    approved_count = 0
    for recovery_request in queryset.filter(resolved=False):
        user = recovery_request.user
        
        # Disable all TOTP devices for the user
        TOTPDevice.objects.filter(user=user).delete()
        
        # Disable all backup codes
        BackupCode.objects.filter(user=user, used=False).update(used=True, used_at=timezone.now())
        
        # Mark request as resolved
        recovery_request.resolved = True
        recovery_request.resolved_by = request.user
        recovery_request.resolved_at = timezone.now()
        recovery_request.save()
        
        approved_count += 1
        
        # TODO: Send email notification to user
    
    modeladmin.message_user(
        request, 
        f"Successfully approved {approved_count} MFA recovery request(s). Users' MFA has been reset."
    )

approve_mfa_recovery.short_description = "Approve selected recovery requests and reset MFA"

def deny_mfa_recovery(modeladmin, request, queryset):
    """Deny MFA recovery requests"""
    denied_count = 0
    for recovery_request in queryset.filter(resolved=False):
        recovery_request.resolved = True
        recovery_request.resolved_by = request.user
        recovery_request.resolved_at = timezone.now()
        recovery_request.save()
        denied_count += 1
        
        # TODO: Send email notification to user about denial
    
    modeladmin.message_user(
        request, 
        f"Denied {denied_count} MFA recovery request(s)."
    )

deny_mfa_recovery.short_description = "Deny selected recovery requests"

# Add actions to the admin
MFARecoveryRequestAdmin.actions = [approve_mfa_recovery, deny_mfa_recovery]
