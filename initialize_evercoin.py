#!/usr/bin/env python
"""
Initialize Evercoin balance for all users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from django.contrib.auth.models import User
from chat.models import UserProfile

# Starting balance
STARTING_EVERCOIN = 10000

# Get or create profile for all users
updated_count = 0
for user in User.objects.all():
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Only set if not already set
    if profile.evercoin == 0:
        profile.evercoin = STARTING_EVERCOIN
        profile.save()
        updated_count += 1
        print(f"✅ {user.username}: +{STARTING_EVERCOIN} EC (total: {profile.evercoin})")
    else:
        print(f"⚠️  {user.username}: Already has {profile.evercoin} EC (skipped)")

print(f"\n✅ Updated {updated_count} users with {STARTING_EVERCOIN} EC starting balance")
