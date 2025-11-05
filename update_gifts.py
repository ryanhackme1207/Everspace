import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import Gift

# Gifts to keep (11 total) - good mix of rarities
GIFTS_TO_KEEP = [
    '🌹 Rose',      # common
    '❤️ Heart',     # common
    '⭐ Star',      # common
    '🎂 Cake',      # common
    '💎 Diamond',   # rare
    '👑 Crown',     # rare
    '🏆 Trophy',    # rare
    '🎆 Fireworks', # epic
    '🌈 Rainbow',   # epic
    '🦄 Unicorn',   # epic
    '🐉 Dragon',    # legendary
]

print("\n🔍 Finding gifts to delete...\n")

all_gifts = Gift.objects.all()
gifts_to_delete = []

for gift in all_gifts:
    gift_display = f"{gift.emoji} {gift.name}"
    if gift_display not in GIFTS_TO_KEEP:
        gifts_to_delete.append(gift)
        print(f"❌ Deleting: {gift_display}")

print(f"\n🗑️  Deleting {len(gifts_to_delete)} gifts...")
deleted_count, _ = Gift.objects.filter(id__in=[g.id for g in gifts_to_delete]).delete()

print(f"✅ Deleted {deleted_count} gifts")
print(f"📊 Remaining gifts: {Gift.objects.count()}\n")

# Show remaining gifts
remaining = Gift.objects.all().order_by('rarity', 'name')
for i, gift in enumerate(remaining, 1):
    print(f"{i}. {gift.emoji} {gift.name} ({gift.rarity})")

print("\n✨ Database updated successfully!")
