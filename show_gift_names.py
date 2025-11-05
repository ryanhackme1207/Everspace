import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import Gift

print("\n📋 Current gift names:\n")
for gift in Gift.objects.all():
    print(f'Name: "{gift.name}", Emoji: "{gift.emoji}", Rarity: {gift.rarity}')
