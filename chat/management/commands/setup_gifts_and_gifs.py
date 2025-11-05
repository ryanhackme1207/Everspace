"""
Management command to setup gifts and GIFs for the first time or reset them.
Usage: python manage.py setup_gifts_and_gifs
"""
from django.core.management.base import BaseCommand
from chat.models import Gift, GifPack, GifFile
import os


class Command(BaseCommand):
    help = 'Setup gifts and GIFs in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-gifts',
            action='store_true',
            help='Skip gift setup'
        )
        parser.add_argument(
            '--skip-gifs',
            action='store_true',
            help='Skip GIF setup'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before setup'
        )

    def handle(self, *args, **options):
        skip_gifts = options['skip_gifts']
        skip_gifs = options['skip_gifs']
        reset = options['reset']

        if reset:
            self.stdout.write(self.style.WARNING('Resetting existing data...'))
            Gift.objects.all().delete()
            GifFile.objects.all().delete()
            GifPack.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data reset complete'))

        if not skip_gifts:
            self.setup_gifts()

        if not skip_gifs:
            self.setup_gifs()

        self.stdout.write(self.style.SUCCESS('Setup complete!'))

    def setup_gifts(self):
        self.stdout.write('Setting up gifts...')
        
        gifts_data = [
            # Common (50-150 EC)
            {'name': 'Rose', 'emoji': '🌹', 'rarity': 'common', 'description': 'A beautiful red rose', 'cost': 50, 'animation': 'hearts-rain'},
            {'name': 'Heart', 'emoji': '❤️', 'rarity': 'common', 'description': 'A red heart full of love', 'cost': 75, 'animation': 'hearts-rain'},
            {'name': 'Star', 'emoji': '⭐', 'rarity': 'common', 'description': 'A shining star', 'cost': 100, 'animation': 'sparkle-spin'},
            {'name': 'Cake', 'emoji': '🎂', 'rarity': 'common', 'description': 'A delicious birthday cake', 'cost': 150, 'animation': 'float'},
            
            # Rare (300-400 EC)
            {'name': 'Diamond', 'emoji': '💎', 'rarity': 'rare', 'description': 'A sparkling diamond', 'cost': 300, 'animation': 'crystal-drop'},
            {'name': 'Trophy', 'emoji': '🏆', 'rarity': 'rare', 'description': 'A golden trophy', 'cost': 350, 'animation': 'trophy-rise'},
            {'name': 'Crown', 'emoji': '👑', 'rarity': 'rare', 'description': 'A royal crown', 'cost': 400, 'animation': 'trophy-rise'},
            
            # Epic (500-700 EC)
            {'name': 'Fireworks', 'emoji': '🎆', 'rarity': 'epic', 'description': 'Spectacular fireworks display', 'cost': 500, 'animation': 'fireworks'},
            {'name': 'Rainbow', 'emoji': '🌈', 'rarity': 'epic', 'description': 'A magical rainbow', 'cost': 600, 'animation': 'rotate-rainbow'},
            {'name': 'Unicorn', 'emoji': '🦄', 'rarity': 'epic', 'description': 'A magical unicorn', 'cost': 700, 'animation': 'unicorn-gallop'},
            
            # Legendary (1000 EC)
            {'name': 'Dragon', 'emoji': '🐉', 'rarity': 'legendary', 'description': 'A majestic dragon', 'cost': 1000, 'animation': 'dragon-fly'},
        ]
        
        for gift_data in gifts_data:
            gift, created = Gift.objects.get_or_create(
                name=gift_data['name'],
                defaults={
                    'emoji': gift_data['emoji'],
                    'rarity': gift_data['rarity'],
                    'description': gift_data['description'],
                    'cost': gift_data['cost'],
                    'animation': gift_data['animation'],
                    'icon_url': f"/static/chat/gifts/{gift_data['name'].lower()}.png",
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created: {gift_data["name"]} ({gift_data["cost"]} EC)')
            else:
                self.stdout.write(f'  - Already exists: {gift_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS(f'Gifts setup complete! Total: {Gift.objects.count()}'))

    def setup_gifs(self):
        self.stdout.write('Setting up GIF packs...')
        
        packs_data = [
            {'name': 'Funny', 'icon': '😂', 'order': 1},
            {'name': 'Happy', 'icon': '😊', 'order': 2},
            {'name': 'Love', 'icon': '❤️', 'order': 3},
            {'name': 'Work', 'icon': '💼', 'order': 4},
            {'name': '😎 Cool', 'icon': '😎', 'order': 5},
            {'name': '😂 Funny', 'icon': '😂', 'order': 6},
            {'name': '😊 Happy', 'icon': '😊', 'order': 7},
            {'name': '❤️ Love', 'icon': '❤️', 'order': 8},
            {'name': '😢 Sad', 'icon': '😢', 'order': 9},
            {'name': '😱 Shocked', 'icon': '😱', 'order': 10},
        ]
        
        for pack_data in packs_data:
            pack, created = GifPack.objects.get_or_create(
                name=pack_data['name'],
                defaults={
                    'icon': pack_data['icon'],
                    'order': pack_data['order'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created pack: {pack_data["name"]}')
            else:
                self.stdout.write(f'  - Pack already exists: {pack_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS(f'GIF packs setup complete! Total: {GifPack.objects.count()}'))
        self.stdout.write(self.style.WARNING('Note: GIF files need to be populated separately using populate_gifs.py'))
