from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class SecureUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check for username strength
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        
        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            raise ValidationError("Username can only contain letters, numbers, underscores, dots, and hyphens.")
        
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user


class SecureAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })


class OTPVerificationForm(forms.Form):
    otp_token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        }),
        help_text="Enter the 6-digit code from your authenticator app"
    )

    def clean_otp_token(self):
        token = self.cleaned_data.get('otp_token')
        if not token.isdigit():
            raise ValidationError("OTP must contain only numbers.")
        return token


class RecoveryCodeForm(forms.Form):
    recovery_code = forms.CharField(
        max_length=10,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': 'abcd-1234',
            'autocomplete': 'off',
            'style': 'font-family: monospace; letter-spacing: 2px;'
        }),
        help_text="Enter one of your backup recovery codes"
    )

    def clean_recovery_code(self):
        code = self.cleaned_data.get('recovery_code')
        # Remove any spaces or dashes for consistency
        if code:
            code = code.replace('-', '').replace(' ', '').lower()
        return code


class MFARecoveryRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your account email'
        }),
        help_text="We'll send recovery instructions to your registered email"
    )
    
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Explain why you need MFA recovery (e.g., lost phone, new device, etc.)'
        }),
        help_text="Please provide details about your situation"
    )