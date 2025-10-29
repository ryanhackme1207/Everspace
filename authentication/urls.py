from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='auth_register'),
    path('login/', views.SecureLoginView.as_view(), name='auth_login'),
    path('logout/', views.SecureLogoutView.as_view(), name='auth_logout'),
    path('mfa/setup/', views.mfa_setup_view, name='auth_mfa_setup'),
    path('mfa/verify/', views.mfa_verify_view, name='auth_mfa_verify'),
    path('mfa/disable/', views.mfa_disable_view, name='auth_mfa_disable'),
    path('mfa/backup-codes/', views.backup_codes_view, name='auth_backup_codes'),
    path('mfa/regenerate-codes/', views.regenerate_backup_codes_view, name='auth_regenerate_codes'),
    path('mfa/view-codes/', views.view_backup_codes_view, name='auth_view_codes'),
    path('mfa/recovery/', views.mfa_recovery_request_view, name='auth_mfa_recovery'),
]