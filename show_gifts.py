import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import Gift

gifts = Gift.objects.all().order_by('id')
print(f"\n📋 Total Gifts: {gifts.count()}\n")
for gift in gifts:
    print(f"{gift.id}. {gift.emoji} {gift.name} ({gift.rarity})")
