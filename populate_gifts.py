#!/usr/bin/env python
"""
Script to populate default gifts in the EverSpace chat application.
Run with: python populate_gifts.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import Gift

# Default gifts data
DEFAULT_GIFTS = [
    # Common gifts
    {
        'name': 'Rose',
        'description': 'A beautiful red rose',
        'emoji': '🌹',
        'icon_url': '/static/chat/gifts/rose.png',
        'rarity': 'common',
    },
    {
        'name': 'Heart',
        'description': 'A red heart full of love',
        'emoji': '❤️',
        'icon_url': '/static/chat/gifts/heart.png',
        'rarity': 'common',
    },
    {
        'name': 'Star',
        'description': 'A shining star',
        'emoji': '⭐',
        'icon_url': '/static/chat/gifts/star.png',
        'rarity': 'common',
    },
    {
        'name': 'Flower',
        'description': 'A colorful flower',
        'emoji': '🌸',
        'icon_url': '/static/chat/gifts/flower.png',
        'rarity': 'common',
    },
    {
        'name': 'Cake',
        'description': 'A delicious birthday cake',
        'emoji': '🎂',
        'icon_url': '/static/chat/gifts/cake.png',
        'rarity': 'common',
    },
    # Rare gifts
    {
        'name': 'Diamond',
        'description': 'A sparkling diamond',
        'emoji': '💎',
        'icon_url': '/static/chat/gifts/diamond.png',
        'rarity': 'rare',
    },
    {
        'name': 'Crown',
        'description': 'A royal crown',
        'emoji': '👑',
        'icon_url': '/static/chat/gifts/crown.png',
        'rarity': 'rare',
    },
    {
        'name': 'Trophy',
        'description': 'A golden trophy',
        'emoji': '🏆',
        'icon_url': '/static/chat/gifts/trophy.png',
        'rarity': 'rare',
    },
    {
        'name': 'Gift Box',
        'description': 'A mysterious gift box',
        'emoji': '🎁',
        'icon_url': '/static/chat/gifts/gift_box.png',
        'rarity': 'rare',
    },
    # Epic gifts
    {
        'name': 'Fireworks',
        'description': 'Spectacular fireworks display',
        'emoji': '🎆',
        'icon_url': '/static/chat/gifts/fireworks.png',
        'rarity': 'epic',
    },
    {
        'name': 'Rainbow',
        'description': 'A magical rainbow',
        'emoji': '🌈',
        'icon_url': '/static/chat/gifts/rainbow.png',
        'rarity': 'epic',
    },
    {
        'name': 'Unicorn',
        'description': 'A magical unicorn',
        'emoji': '🦄',
        'icon_url': '/static/chat/gifts/unicorn.png',
        'rarity': 'epic',
    },
    # Legendary gifts
    {
        'name': 'Dragon',
        'description': 'A majestic dragon',
        'emoji': '🐉',
        'icon_url': '/static/chat/gifts/dragon.png',
        'rarity': 'legendary',
    },
    {
        'name': 'Phoenix',
        'description': 'A mythical phoenix rising from flames',
        'emoji': '🔥',
        'icon_url': '/static/chat/gifts/phoenix.png',
        'rarity': 'legendary',
    },
    {
        'name': 'Meteor',
        'description': 'A blazing meteor from space',
        'emoji': '☄️',
        'icon_url': '/static/chat/gifts/meteor.png',
        'rarity': 'legendary',
    },
]

def populate_gifts():
    """Populate default gifts in database"""
    created_count = 0
    skipped_count = 0
    
    for gift_data in DEFAULT_GIFTS:
        gift, created = Gift.objects.get_or_create(
            name=gift_data['name'],
            defaults={
                'description': gift_data['description'],
                'emoji': gift_data['emoji'],
                'icon_url': gift_data['icon_url'],
                'rarity': gift_data['rarity'],
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {gift.name} ({gift.rarity})")
        else:
            skipped_count += 1
            print(f"- Skipped: {gift.name} (already exists)")
    
    print(f"\n========================================")
    print(f"Total created: {created_count}")
    print(f"Total skipped: {skipped_count}")
    print(f"Total gifts: {Gift.objects.count()}")
    print(f"========================================")

if __name__ == '__main__':
    populate_gifts()
