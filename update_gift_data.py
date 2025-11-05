import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import Gift

# Gift data with costs and animations (names WITHOUT emoji prefix)
GIFT_DATA = {
    'Rose': {'cost': 50, 'animation': 'hearts-rain'},
    'Heart': {'cost': 75, 'animation': 'hearts-rain'},
    'Star': {'cost': 100, 'animation': 'sparkle-spin'},
    'Cake': {'cost': 150, 'animation': 'float'},
    'Diamond': {'cost': 300, 'animation': 'crystal-drop'},
    'Crown': {'cost': 400, 'animation': 'trophy-rise'},
    'Trophy': {'cost': 350, 'animation': 'trophy-rise'},
    'Fireworks': {'cost': 500, 'animation': 'fireworks'},
    'Rainbow': {'cost': 600, 'animation': 'rotate-rainbow'},
    'Unicorn': {'cost': 700, 'animation': 'unicorn-gallop'},
    'Dragon': {'cost': 1000, 'animation': 'dragon-fly'},
}

print("\n🎁 Updating gift costs and animations...\n")

for gift_name, data in GIFT_DATA.items():
    try:
        gift = Gift.objects.get(name=gift_name)
        gift.cost = data['cost']
        gift.animation = data['animation']
        gift.save()
        print(f"✅ {gift_name}: {data['cost']} EC, {data['animation']}")
    except Gift.DoesNotExist:
        print(f"⚠️  Gift not found: {gift_name}")

print("\n✨ Gift system updated successfully!")

# Show all gifts
print("\n📋 All gifts:\n")
for gift in Gift.objects.all().order_by('rarity', 'cost'):
    print(f"{gift.emoji} {gift.name:20} | {gift.cost:4} EC | {gift.rarity:10} | {gift.animation}")
