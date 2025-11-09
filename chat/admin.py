from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import UserProfile, Room, Message, Gift, GiftTransaction

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'evercoin_display', 'profile_picture_preview', 'created_at', 'evercoin_actions']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'profile_picture_preview_large']
    ordering = ['-evercoin', '-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Currency', {
            'fields': ('evercoin',),
            'description': 'Virtual currency for sending gifts'
        }),
        ('Profile Customization', {
            'fields': ('profile_picture', 'profile_picture_preview_large', 'pixel_avatar', 'cover_image', 'cover_choice', 'bio'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def evercoin_display(self, obj):
        """Display evercoin with emoji"""
        formatted_amount = f"{obj.evercoin:,}"
        return format_html(
            '<span style="font-weight: bold; color: #f59e0b;">💰 {}</span>',
            formatted_amount
        )
    evercoin_display.short_description = "Evercoin Balance"
    
    def profile_picture_preview(self, obj):
        """Small preview of profile picture"""
        url = obj.get_profile_picture_url()
        return format_html(
            '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
            url
        )
    profile_picture_preview.short_description = "Avatar"
    
    def profile_picture_preview_large(self, obj):
        """Large preview of profile picture"""
        url = obj.get_profile_picture_url()
        return format_html(
            '<img src="{}" style="width: 150px; height: 150px; border-radius: 8px; object-fit: cover;" />',
            url
        )
    profile_picture_preview_large.short_description = "Profile Picture Preview"
    
    def evercoin_actions(self, obj):
        """Quick action buttons for evercoin management"""
        return format_html(
            '<a class="button" href="/admin/chat/userprofile/{}/add-evercoin/" '
            'style="background: #10b981; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin-right: 5px;">➕ Add</a>'
            '<a class="button" href="/admin/chat/userprofile/{}/deduct-evercoin/" '
            'style="background: #ef4444; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">➖ Deduct</a>',
            obj.pk, obj.pk
        )
    evercoin_actions.short_description = "Quick Actions"
    evercoin_actions.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:profile_id>/add-evercoin/', self.admin_site.admin_view(self.add_evercoin_view), name='add_evercoin'),
            path('<int:profile_id>/deduct-evercoin/', self.admin_site.admin_view(self.deduct_evercoin_view), name='deduct_evercoin'),
        ]
        return custom_urls + urls
    
    def add_evercoin_view(self, request, profile_id):
        """Custom view to add evercoin to a user"""
        if not request.user.is_superuser:
            messages.error(request, 'Only superusers can edit Evercoins.')
            return redirect('admin:chat_userprofile_changelist')
        
        profile = UserProfile.objects.get(pk=profile_id)
        
        if request.method == 'POST':
            try:
                amount = int(request.POST.get('amount', 0))
                reason = request.POST.get('reason', '').strip()
                
                if amount <= 0:
                    messages.error(request, 'Amount must be positive.')
                elif amount > 1000000:
                    messages.error(request, 'Amount too large. Maximum is 1,000,000.')
                else:
                    old_balance = profile.evercoin
                    profile.evercoin += amount
                    profile.save()
                    
                    messages.success(
                        request, 
                        f'Successfully added {amount:,} Evercoin to {profile.user.username}. '
                        f'Balance: {old_balance:,} → {profile.evercoin:,}. Reason: {reason or "N/A"}'
                    )
                    return redirect('admin:chat_userprofile_changelist')
            except ValueError:
                messages.error(request, 'Invalid amount.')
        
        context = {
            'profile': profile,
            'action_type': 'Add',
            'title': f'Add Evercoin to {profile.user.username}',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/chat/evercoin_form.html', context)
    
    def deduct_evercoin_view(self, request, profile_id):
        """Custom view to deduct evercoin from a user"""
        if not request.user.is_superuser:
            messages.error(request, 'Only superusers can edit Evercoins.')
            return redirect('admin:chat_userprofile_changelist')
        
        profile = UserProfile.objects.get(pk=profile_id)
        
        if request.method == 'POST':
            try:
                amount = int(request.POST.get('amount', 0))
                reason = request.POST.get('reason', '').strip()
                
                if amount <= 0:
                    messages.error(request, 'Amount must be positive.')
                elif amount > profile.evercoin:
                    messages.error(request, f'Cannot deduct {amount:,}. User only has {profile.evercoin:,} Evercoin.')
                else:
                    old_balance = profile.evercoin
                    profile.evercoin -= amount
                    profile.save()
                    
                    messages.success(
                        request, 
                        f'Successfully deducted {amount:,} Evercoin from {profile.user.username}. '
                        f'Balance: {old_balance:,} → {profile.evercoin:,}. Reason: {reason or "N/A"}'
                    )
                    return redirect('admin:chat_userprofile_changelist')
            except ValueError:
                messages.error(request, 'Invalid amount.')
        
        context = {
            'profile': profile,
            'action_type': 'Deduct',
            'title': f'Deduct Evercoin from {profile.user.username}',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/chat/evercoin_form.html', context)
    
    def get_readonly_fields(self, request, obj=None):
        """Make evercoin read-only for non-superusers"""
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly.append('evercoin')
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of user profiles"""
        return False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'visibility', 'creator', 'created_at', 'member_count']
    list_filter = ['visibility', 'created_at']
    search_fields = ['name', 'description', 'creator__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Members"


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'cost_display', 'rarity', 'animation']
    list_filter = ['rarity']
    search_fields = ['name', 'description']
    ordering = ['rarity', 'cost']
    
    fieldsets = (
        ('Gift Information', {
            'fields': ('name', 'emoji', 'description')
        }),
        ('Economics', {
            'fields': ('cost', 'rarity')
        }),
        ('Visual Effects', {
            'fields': ('animation',)
        }),
    )
    
    def cost_display(self, obj):
        formatted_cost = f"{obj.cost:,}"
        return format_html(
            '<span style="font-weight: bold; color: #f59e0b;">💰 {}</span>',
            formatted_cost
        )
    cost_display.short_description = "Cost"


@admin.register(GiftTransaction)
class GiftTransactionAdmin(admin.ModelAdmin):
    list_display = ['gift', 'sender', 'receiver', 'intimacy_display', 'room', 'sent_at']
    list_filter = ['sent_at', 'gift__rarity']
    search_fields = ['sender__username', 'receiver__username', 'gift__name', 'message']
    readonly_fields = ['sent_at']
    ordering = ['-sent_at']
    date_hierarchy = 'sent_at'
    
    def intimacy_display(self, obj):
        formatted_intimacy = f"{obj.intimacy_gained:,}"
        return format_html(
            '<span style="color: #ec4899;">💖 {}</span>',
            formatted_intimacy
        )
    intimacy_display.short_description = "Intimacy"
    
    def has_add_permission(self, request):
        return False  # Transactions should only be created through the app
    
    def has_change_permission(self, request, obj=None):
        return False  # Transactions should not be modified


# Admin action to grant evercoin to multiple users
@admin.action(description='Grant Evercoin to selected users')
def grant_evercoin_bulk(modeladmin, request, queryset):
    """Bulk action to grant evercoin to multiple users"""
    if not request.user.is_superuser:
        modeladmin.message_user(request, 'Only superusers can grant Evercoins.', level='error')
        return
    
    # This would typically open a form, but for simplicity we'll grant a fixed amount
    amount = 1000  # Default amount
    count = 0
    
    for profile in queryset:
        profile.evercoin += amount
        profile.save()
        count += 1
    
    modeladmin.message_user(
        request,
        f'Successfully granted {amount:,} Evercoin to {count} user(s).'
    )

UserProfileAdmin.actions = [grant_evercoin_bulk]


# Register MultiplayerGame2048 model
from .models import MultiplayerGame2048

@admin.register(MultiplayerGame2048)
class MultiplayerGame2048Admin(admin.ModelAdmin):
    list_display = ['game_id', 'player1', 'player2', 'status', 'player1_health', 'player2_health', 'winner', 'is_bot_game', 'created_at']
    list_filter = ['status', 'is_bot_game', 'created_at']
    search_fields = ['game_id', 'player1__username', 'player2__username']
    readonly_fields = ['game_id', 'created_at', 'started_at', 'finished_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Game Information', {
            'fields': ('game_id', 'status', 'is_bot_game')
        }),
        ('Players', {
            'fields': ('player1', 'player2', 'winner')
        }),
        ('Health & Score', {
            'fields': ('player1_health', 'player2_health', 'player1_score', 'player2_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'finished_at'),
            'classes': ('collapse',)
        }),
    )
