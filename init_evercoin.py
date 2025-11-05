import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from django.contrib.auth.models import User
from chat.models import UserProfile

# Give all users starting Evercoin
STARTING_EVERCOIN = 5000

print("\n💰 Distributing starting Evercoin...\n")

updated_count = 0
for user in User.objects.all():
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created or profile.evercoin == 0:
        profile.evercoin = STARTING_EVERCOIN
        profile.save()
        print(f"✅ {user.username}: +{STARTING_EVERCOIN} EC")
        updated_count += 1
    else:
        print(f"⏭️  {user.username}: Already has {profile.evercoin} EC")

print(f"\n✨ Updated {updated_count} users with starting Evercoin!")
