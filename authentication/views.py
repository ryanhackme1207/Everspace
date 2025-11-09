from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import user_has_device
import qrcode
import io
import base64

from .forms import SecureUserCreationForm, SecureAuthenticationForm, OTPVerificationForm, RecoveryCodeForm, MFARecoveryRequestForm
from .models import BackupCode, MFARecoveryRequest


@ratelimit(key='ip', rate='5/m', method='POST')
def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat:chat_index')
    
    if request.method == 'POST':
        form = SecureUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in to start chatting.')
            return redirect('auth_login')
    else:
        form = SecureUserCreationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


@method_decorator([never_cache, csrf_protect, ratelimit(key='ip', rate='10/m', method='POST')], name='dispatch')
class SecureLoginView(LoginView):
    form_class = SecureAuthenticationForm
    template_name = 'authentication/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        
        # Check if user has MFA enabled
        if user_has_device(user):
            # Store user in session for MFA verification
            self.request.session['pre_2fa_user_pk'] = user.pk
            return redirect('auth_mfa_verify')
        else:
            # Login directly if no MFA
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {user.first_name}!')
            
            # Just redirect to chat (let user choose when to set up MFA)
            return redirect('chat:chat_index')

    def get_success_url(self):
        return reverse_lazy('chat:chat_index')


@ratelimit(key='ip', rate='10/m', method='POST')
def mfa_verify_view(request):
    if 'pre_2fa_user_pk' not in request.session:
        return redirect('auth_login')
    
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=request.session['pre_2fa_user_pk'])
    except User.DoesNotExist:
        return redirect('auth_login')
    
    # Check which form was submitted
    use_recovery = request.GET.get('recovery') == 'true' or request.POST.get('use_recovery')
    
    if request.method == 'POST':
        if use_recovery:
            form = RecoveryCodeForm(request.POST)
            if form.is_valid():
                recovery_code = form.cleaned_data['recovery_code']
                
                # Verify backup code
                if BackupCode.verify_code(user, recovery_code):
                    login(request, user)
                    del request.session['pre_2fa_user_pk']
                    messages.success(request, f'Welcome back, {user.first_name}! Recovery code used successfully.')
                    
                    # Check remaining backup codes
                    remaining_codes = BackupCode.objects.filter(user=user, used=False).count()
                    if remaining_codes <= 2:
                        messages.warning(request, f'You only have {remaining_codes} backup codes remaining. Consider generating new ones.')
                    
                    return redirect('chat:chat_index')
                else:
                    messages.error(request, 'Invalid or already used recovery code.')
        else:
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                token = form.cleaned_data['otp_token']
                
                # Verify the OTP token
                for device in user.totpdevice_set.all():
                    if device.verify_token(token):
                        # Token is valid, complete login
                        login(request, user)
                        del request.session['pre_2fa_user_pk']
                        messages.success(request, f'Welcome back, {user.first_name}!')
                        return redirect('chat:chat_index')
                
                # Token is invalid
                messages.error(request, 'Invalid authentication code. Please try again.')
    else:
        if use_recovery:
            form = RecoveryCodeForm()
        else:
            form = OTPVerificationForm()
    
    return render(request, 'authentication/mfa_verify.html', {
        'form': form,
        'user': user,
        'use_recovery': use_recovery,
        'has_backup_codes': BackupCode.objects.filter(user=user, used=False).exists()
    })


@login_required
def mfa_setup_view(request):
    user = request.user
    
    # Check if user already has MFA enabled
    if user_has_device(user):
        messages.info(request, 'Multi-Factor Authentication is already enabled.')
        return redirect('chat:chat_index')
    
    # Show helpful message when user manually chooses to set up MFA
    if request.method == 'GET':
        messages.info(request, 'Setting up MFA will add an extra layer of security to your EverSpace account.')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['otp_token']
            device_name = request.session.get('device_name', 'default')
            
            # Get the device from session
            device = TOTPDevice(user=user, name=device_name)
            device.key = request.session.get('device_key')
            
            if device.verify_token(token):
                device.confirmed = True
                device.save()
                del request.session['device_key']
                del request.session['device_name']
                
                # Generate backup codes
                backup_codes = BackupCode.generate_codes_for_user(user)
                request.session['new_backup_codes'] = backup_codes
                
                messages.success(request, 'Multi-Factor Authentication has been successfully enabled!')
                return redirect('auth_backup_codes')
            else:
                messages.error(request, 'Invalid code. Please try again.')
    else:
        form = OTPVerificationForm()
        
        # Create a new TOTP device
        device = TOTPDevice(user=user, name='default')
        device.save()
        
        # Store device info in session
        request.session['device_key'] = device.key
        request.session['device_name'] = device.name
    
    # Generate QR code
    device_key = request.session.get('device_key')
    if device_key:
        device = TOTPDevice(user=user, name='default')
        device.key = device_key
        
        # Generate QR code
        qr_code_url = device.config_url
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_code_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    else:
        qr_code_data = None
    
    return render(request, 'authentication/mfa_setup.html', {
        'form': form,
        'qr_code_data': qr_code_data,
        'manual_key': device_key
    })


@login_required
def mfa_disable_view(request):
    if request.method == 'POST':
        # Delete all TOTP devices for the user
        request.user.totpdevice_set.all().delete()
        messages.success(request, 'Multi-Factor Authentication has been disabled.')
        return redirect('chat:chat_index')
    
    return render(request, 'authentication/mfa_disable.html')


@login_required
def backup_codes_view(request):
    """Show backup codes after MFA setup or regeneration"""
    backup_codes = request.session.get('new_backup_codes', [])
    
    if not backup_codes:
        # Regenerate if needed
        if user_has_device(request.user):
            backup_codes = BackupCode.generate_codes_for_user(request.user)
            request.session['new_backup_codes'] = backup_codes
        else:
            messages.error(request, 'Please set up MFA first.')
            return redirect('auth_mfa_setup')
    
    if request.method == 'POST':
        # User confirmed they saved the codes
        if 'new_backup_codes' in request.session:
            del request.session['new_backup_codes']
        messages.success(request, 'Backup codes saved! You can now use them if you lose your device.')
        return redirect('chat:chat_index')
    
    return render(request, 'authentication/backup_codes.html', {
        'backup_codes': backup_codes
    })


@login_required
def regenerate_backup_codes_view(request):
    """Regenerate backup codes"""
    if not user_has_device(request.user):
        messages.error(request, 'Please set up MFA first.')
        return redirect('auth_mfa_setup')
    
    if request.method == 'POST':
        backup_codes = BackupCode.generate_codes_for_user(request.user)
        request.session['new_backup_codes'] = backup_codes
        messages.success(request, 'New backup codes generated! Please save them securely.')
        return redirect('auth_backup_codes')
    
    return render(request, 'authentication/regenerate_backup_codes.html')


def mfa_recovery_request_view(request):
    """Request MFA recovery help"""
    if request.method == 'POST':
        form = MFARecoveryRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            reason = form.cleaned_data['reason']
            
            # Find user by email
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(email=email)
                MFARecoveryRequest.objects.create(
                    user=user,
                    email=email,
                    reason=reason
                )
                messages.success(request, 'Recovery request submitted. An administrator will review your request.')
                return redirect('auth_login')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = MFARecoveryRequestForm()
    
    return render(request, 'authentication/mfa_recovery_request.html', {
        'form': form
    })


@login_required
def view_backup_codes_view(request):
    """View existing backup codes status"""
    backup_codes = BackupCode.objects.filter(user=request.user).order_by('created_at')
    unused_count = backup_codes.filter(used=False).count()
    
    return render(request, 'authentication/view_backup_codes.html', {
        'backup_codes': backup_codes,
        'unused_count': unused_count
    })


class SecureLogoutView(LogoutView):
    next_page = '/'  # Redirect to landing page after logout
    http_method_names = ['get', 'post']  # Allow both GET and POST requests
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully. Welcome back to EverSpace!')
        return super().dispatch(request, *args, **kwargs)
