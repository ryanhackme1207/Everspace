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
                    {'title': 'Laughing', 'url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjFhbDlzeXJ3anl2cmZnbTdxZGttOXY2cnZrYjU2b3puanVoMHI5cSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cYZkY9HeKgofpQnOUl/giphy.gif'},
                    {'title': 'Funny Face', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemFqNDMyY2lkY2pqNDd3dDhobXk2dHN4eGU3ZzVqdTl0cHRqbXVkbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/pWO49XP9L7TxbgQVib/giphy.gif'},
                    {'title': 'LOL', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNm5yZWc5bGp0Z3I2cGU0bTdncTBkM3pzOTQ1czU3YTI2dmp3enh2biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZfK4cXKJTTay1Ava29/giphy.gif'},
                    {'title': 'Hilarious', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZm1xbGlnZ2RicG5xN2YxN25mcjJ3YzN4cXFraHZmdmV6eG1xa2VpYSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/JIX9t2j0ZTN9S/giphy.gif'},
                    {'title': 'Giggle', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2Y2anJxYnVia2R0dTRqbGl5NHZnYWlqM3VnOHJ6NWJqYXB2OWVjdCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3oEjI6SIIHBdRxXI40/giphy.gif'},
                ]
            },
            'happy': {
                'name': 'Happy',
                'icon': '😊',
                'order': 2,
                'gifs': [
                    {'title': 'Smile', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2s5dXdiZ3MxNm9xeWZ0amMxM2xxbTBmbjk3YWxmaTl6NzM5bzBsdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/pyHTKJ4G9WGQKd12cl/giphy.gif'},
                    {'title': 'Excited', 'url': 'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bTZ4dms4eXI4MzRreWgyYzQxbWpveTJ3ZmZvNGI1ZzhjY25vbW5mZCZlcD12MV9naWZzX3JlbGF0ZWQmY3Q9Zw/IN2JswkB122n6/giphy.gif'},
                    {'title': 'Happy Dance', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2d6d3FxeXBjcnJydGU1cWhnZzd4NGttdGlrd3cwNnRvdWxmeWcxYSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/H7wajFPnZGdRWaQeu0/giphy.gif'},
                    {'title': 'Joy', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWJkOWc0YmRmaHVlaHh2OGwzeTB1dHNuN3czZ2Vwbm9qaDN5YWsxYSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/XR9Dp54ZC4dji/giphy.gif'},
                    {'title': 'Celebrate', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXFubHM4bjBmY3Z3ejJ1d3piZ24zY2p5M3hkaHozNXB6anR4aG0yYSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/artj92V8o75VPL7AeQ/giphy.gif'},
                ]
            },
            'love': {
                'name': 'Love',
                'icon': '❤️',
                'order': 3,
                'gifs': [
                    {'title': 'Heart Eyes', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGo3cDhxZ3p0NXUzNXlzbnR2dzk4emx1aGltbWRnanZvMGl6aWk1MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/G5X63GrrLjjVK/giphy.gif'},
                    {'title': 'Love', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTF6ZTlyYmVvdWtzOTB0dG50ZnNhOGEyNGk4eDRzOTBvbHp4eTlhcCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/MDJ9IbxxvDUQM/giphy.gif'},
                    {'title': 'Kiss', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmp3aGZvdXBtZTh6MWprZXRlNW00ZnNicWtxNnVrMGo3ZmdqYzI0bSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/bGm9FuBCGg4SY/giphy.gif'},
                ]
            },
            'work': {
                'name': 'Work',
                'icon': '💼',
                'order': 4,
                'gifs': [
                    {'title': 'Working Hard', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHBpOHdxY3Z0d2VvMmxjenJudWozanFvZmRidHdqb3l0bWN0Y2RydSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xTiN0DvoDyWQey2B8I/giphy.gif'},
                    {'title': 'Busy', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWN6OWxkZ2J1b2Zlemx0cGx0bWszMXlnM2U0ZmpqZnZsMjR6cDkyZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3o7btNhMBytxAM6YBa/giphy.gif'},
                    {'title': 'Coffee Break', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnpvaHN6bWdvZ29hOXA0dWRrYnFnY3dvYnp4ZGJqemF3bjJnaGhybSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3o6fJ1OqbJFjnLgfuM/giphy.gif'},
                ]
            },
            'cool': {
                'name': 'Cool',
                'icon': '😎',
                'order': 5,
                'gifs': [
                    {'title': 'Cool Dude', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcXkxdWxhdnVuMW5ibHdiaWlkbnBrZmg1NHk5cTBxc251cmJ3cGRsZiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l0IydMNwRPUo0yvHG/giphy.gif'},
                    {'title': 'Swagger', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbHhvdnh6YTNuNGVvY3Z0M3dmemF0OGNiYjB6MGFudGJwYzRobDdzdCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/YoV992AlZr7W8/giphy.gif'},
                    {'title': 'Sunglasses', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXh1bDB5OTVydzltdDB1OTV3dms0N3FyMWFrZHV0c2k1YW1zb2Z1aSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/YRuFixSNWFVcXaxpmX/giphy.gif'},
                ]
            },
            'sad': {
                'name': 'Sad',
                'icon': '😢',
                'order': 6,
                'gifs': [
                    {'title': 'Crying', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHU3Y3lic2s5OWVpZGVqdGM4bnN2MnY2eXBuZGRvdnd4cTFiZGJ4NiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ROF8OQvDmxytW/giphy.gif'},
                    {'title': 'Sad Face', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbjY2bTFqcGswY2p2cDNidGhlZXBqZGxqcGk4NHpoMDlld2d1ZTk4cCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ISOckXUybVfQ4/giphy.gif'},
                    {'title': 'Disappointed', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmdvNnNqb3dnYjN0YWV0c2F4OTB1cXFnZ2lzZWhuaDJyZWMwN3NvcCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/d2lcHJTG5Tscg/giphy.gif'},
                ]
            },
            'shocked': {
                'name': 'Shocked',
                'icon': '😲',
                'order': 7,
                'gifs': [
                    {'title': 'Shocked Face', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjZpNmF4ZDk1ODRtbGJ0YzQ5YWx1cHE3MTg4bWV0M2ZpMXYyY3oxdyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3o72F8t9TDi2xVnxOE/giphy.gif'},
                    {'title': 'Surprised', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjh4NW5wZmJkMGVtN2U5dWxhczBubHY0NmphbzBqajRpZ2Rnb3IxayZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PUBxelwT57jsQ/giphy.gif'},
                    {'title': 'Wow', 'url': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExajRvdGQ0bnBvY3Z6ajN1ZWwxNGxpaGxtNm1zODBxYmo3MDJvMzI0NyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/26ufdipQqU2lhNA4g/giphy.gif'},
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
