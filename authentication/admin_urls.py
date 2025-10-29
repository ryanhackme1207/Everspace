from django.urls import path
from . import admin_views

urlpatterns = [
    path('admin/authentication/mfarecoveryrequest/<int:request_id>/approve/', 
         admin_views.approve_recovery_request, 
         name='admin_approve_recovery'),
    path('admin/authentication/mfarecoveryrequest/<int:request_id>/deny/', 
         admin_views.deny_recovery_request, 
         name='admin_deny_recovery'),
    path('admin/authentication/mfa-dashboard/', 
         admin_views.MFADashboardView.as_view(), 
         name='admin_mfa_dashboard'),
]