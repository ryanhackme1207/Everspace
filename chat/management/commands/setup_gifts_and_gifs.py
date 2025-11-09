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
                self.stdout.write(f'  [+] Created: {gift_data["name"]} ({gift_data["cost"]} EC)')
            else:
                self.stdout.write(f'  [-] Already exists: {gift_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS(f'Gifts setup complete! Total: {Gift.objects.count()}'))

    def setup_gifs(self):
        self.stdout.write('Setting up GIF packs and files...')
        
        # Define packs with their sample GIFs
        packs_data = {
            'funny': {
                'name': 'Funny',
                'icon': '😂',
                'order': 1,
                'gifs': [
                    {'title': 'Laughing', 'url': 'https://media.giphy.com/media/3o7TKU9Z0i6VEKyOKI/giphy.gif'},
                    {'title': 'Funny Face', 'url': 'https://media.giphy.com/media/l0MYtWjuAb0bdW13W8/giphy.gif'},
                    {'title': 'LOL', 'url': 'https://media.giphy.com/media/g9GznKK0ZX9XC/giphy.gif'},
                ]
            },
            'happy': {
                'name': 'Happy',
                'icon': '😊',
                'order': 2,
                'gifs': [
                    {'title': 'Smile', 'url': 'https://media.giphy.com/media/xT9IgEx8SbQ1vhBbao/giphy.gif'},
                    {'title': 'Excited', 'url': 'https://media.giphy.com/media/b1o4elW5H87dO/giphy.gif'},
                    {'title': 'Happy Dance', 'url': 'https://media.giphy.com/media/l0HlO0Rr5K1p0sSJi/giphy.gif'},
                ]
            },
            'love': {
                'name': 'Love',
                'icon': '❤️',
                'order': 3,
                'gifs': [
                    {'title': 'Heart Eyes', 'url': 'https://media.giphy.com/media/B1p4UJRiKWXbq/giphy.gif'},
                    {'title': 'Love', 'url': 'https://media.giphy.com/media/4cuyucPeVWbNS/giphy.gif'},
                    {'title': 'Kiss', 'url': 'https://media.giphy.com/media/l0HlQY2KjoYB1v7EYo/giphy.gif'},
                ]
            },
            'work': {
                'name': 'Work',
                'icon': '💼',
                'order': 4,
                'gifs': [
                    {'title': 'Working Hard', 'url': 'https://media.giphy.com/media/13HgNZiMRLXjMI/giphy.gif'},
                    {'title': 'Busy', 'url': 'https://media.giphy.com/media/1qJ4InN2yvDbu/giphy.gif'},
                    {'title': 'Coffee Break', 'url': 'https://media.giphy.com/media/3o6Zt6KHxJTbXCnSvu/giphy.gif'},
                ]
            },
            'cool': {
                'name': 'Cool',
                'icon': '😎',
                'order': 5,
                'gifs': [
                    {'title': 'Cool Dude', 'url': 'https://media.giphy.com/media/l0HlGdZ6dmJBp8sZi/giphy.gif'},
                    {'title': 'Swagger', 'url': 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif'},
                    {'title': 'Sunglasses', 'url': 'https://media.giphy.com/media/lCYSEA3lepBxo/giphy.gif'},
                ]
            },
            'sad': {
                'name': 'Sad',
                'icon': '😢',
                'order': 6,
                'gifs': [
                    {'title': 'Crying', 'url': 'https://media.giphy.com/media/jUwpNzg9IcyrK/giphy.gif'},
                    {'title': 'Sad Face', 'url': 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif'},
                    {'title': 'Disappointed', 'url': 'https://media.giphy.com/media/GrUhLU9q3nyRG/giphy.gif'},
                ]
            },
            'shocked': {
                'name': 'Shocked',
                'icon': '😲',
                'order': 7,
                'gifs': [
                    {'title': 'Shocked Face', 'url': 'https://media.giphy.com/media/l0HlTy9x8FZo0XO1i/giphy.gif'},
                    {'title': 'Surprised', 'url': 'https://media.giphy.com/media/BfiYrCLpdv3kk/giphy.gif'},
                    {'title': 'Wow', 'url': 'https://media.giphy.com/media/xTiTnRS5NHH0OwvyeA/giphy.gif'},
                ]
            },
        }
        
        for pack_key, pack_data in packs_data.items():
            pack, created = GifPack.objects.get_or_create(
                name=pack_data['name'],
                defaults={
                    'icon': pack_data['icon'],
                    'order': pack_data['order'],
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(f'  [+] Created pack: {pack_data["name"]}')
            
            # Add sample GIF files
            for gif_data in pack_data['gifs']:
                gif_file, gif_created = GifFile.objects.get_or_create(
                    pack=pack,
                    title=gif_data['title'],
                    defaults={
                        'gif_file': gif_data['url'],  # Store URL directly
                        'is_active': True,
                        'category': pack_data['name'],
                        'source': 'Giphy',
                    }
                )
                if gif_created:
                    self.stdout.write(f'    [+] Added GIF: {gif_data["title"]} ({gif_data["url"]})')
        
        self.stdout.write(self.style.SUCCESS(f'GIF setup complete! Total packs: {GifPack.objects.count()}, Total GIFs: {GifFile.objects.count()}'))
