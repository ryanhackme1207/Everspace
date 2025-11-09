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
                    {'title': 'Laughing', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXp5bzRrMW1jYjZndjhsNjhyMGIydGVmdWVvYWtzeWIzdWFkeDEyNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/142D1Q2ikiyLlu/giphy.gif'},
                    {'title': 'Funny Face', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGdhbzA3MHR1NWg1bDlubHlzaHRteWdudzY1dGdieW1tY3d0OTc2ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/NEvPzZ8bd1V4Y/giphy.gif'},
                    {'title': 'LOL', 'url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExenc1ZW9id2MxeDJ0dXBoeHgxZ2w3YmJhbG43dXBib2N4OWQwY3B0NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26tPo9rksWnfPo4HS/giphy.gif'},
                    {'title': 'Hilarious', 'url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExam5sMGp0YmpkdmlseGU0MzVjYWp5eTN0MTZld3A1eTQ2OHIzeXJzaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/7kn27lnYSAE9O/giphy.gif'},
                    {'title': 'Giggle', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2Uzd2N3OWhuc2JiNGtwbjNveXl2aDFweDczaG82ODkxNHJscHIybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT8qBvH1pAhtfSx52U/giphy.gif'},
                ]
            },
            'happy': {
                'name': 'Happy',
                'icon': '😊',
                'order': 2,
                'gifs': [
                    {'title': 'Smile', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWU3c3MzMnNzYW5qM2hvMzl0MzQzNThmY2p6d2swZzBtd2IzcHlydSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1BXa2alBjrCXC/giphy.gif'},
                    {'title': 'Excited', 'url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTZ4YzJ5MXVvamY0MjY4Zmo1N25qcDJvN2Ryc2RvbzFxM3ExdHJjMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/8Zaoyr0zW9NJLiF6Pv/giphy.gif'},
                    {'title': 'Happy Dance', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2g2cmlyeGxzbXY4bmdtNTNzZjU3cHppZHRmOGw0bjUwYmVnb29jbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/8QbwUh40Hl96yMgvOx/giphy.gif'},
                    {'title': 'Joy', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemJ3cmw1bmszeHZmanAya292dGFqNmtrNzYzaTcyb2UwZmwwYTJsOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/elPt1FL04JjHjrd2k0/giphy.gif'},
                    {'title': 'Celebrate', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmZseGYwbHNpdXhnMjVrNG80bHNwYTlybzZ2NGpsaTl2NHZwOHBybiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jto9Jx898ucZ7QDKLX/giphy.gif'},
                ]
            },
            'love': {
                'name': 'Love',
                'icon': '❤️',
                'order': 3,
                'gifs': [
                    {'title': 'Heart Eyes', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExanJjNDc2amMwNnp2OXhlYnpteW05NnN3MHY0ejBoZDZuMXl2ZWppdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/35DmVHlLURCWBxmK8j/giphy.gif'},
                    {'title': 'Love', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTU2eG5tdW5rMTA4Nm9ibHMxNDM3ZzhyM3M3bXFwcTkzYm9hdmxndiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/MDJ9IbxxvDUQM/giphy.gif'},
                    {'title': 'Kiss', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3N6aHhlN2VxN2NhcmwwaGpmNzlkYW1qazZhM2R1eWc2eHAyc2JsZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wBELrJgO6ZtII/giphy.gif'},
                    {'title': 'Romance', 'url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTZxdGVmazVpa2tjOXB3Y3RiaWFub24xbTBldHQ1bHp5aWhlcnRnZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/J6fjW4xvv2T2uPgk8M/giphy.gif'},
                    {'title': 'Hug', 'url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3I4NjN2cWZ4bm52NG5nMmduZjJoMXV0cGx4MTc1Znpyc3dvcnV4aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ASd0Ukj0y3qMM/giphy.gif'},
                ]
            },
            'work': {
                'name': 'Work',
                'icon': '💼',
                'order': 4,
                'gifs': [
                    {'title': 'Working Hard', 'url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcm80Y2ZtbW5remhjcW5jMXNwbjR3aTJpaWRzemF1cnFqNmRyd2ZxMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kj0mQIbv8gAEyaQ0Ac/giphy.gif'},
                    {'title': 'Busy', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmF2eXU4bmZmNzBtdHc4MGc5YnIzbjl4cmd3Y2t3a3doZG04eGh5MSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ef72To2kJgyAC1FdxK/giphy.gif'},
                    {'title': 'Coffee Break', 'url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDY5YWUwdGhucXpoZTJmeXBnb25jZWp0NjJwYmYxbWVleGE2aDJjciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mlvseq9yvZhba/giphy.gif'},
                    {'title': 'Typing', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExb2xwOHF2cHVhbWVmMGRrdnZlN3k0ejV4dG11d2Q5aDVkNjM2N3lwdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/13ZHjidRzoi7n2/giphy.gif'},
                    {'title': 'Deadline', 'url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbG5sdndmY2Zua284MnI3ajFwbWpyeXFlejBocWVlcml3Y3RkenJlMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ohhwxmNcPvwyRqYKI/giphy.gif'},
                ]
            },
            'cool': {
                'name': 'Cool',
                'icon': '😎',
                'order': 5,
                'gifs': [
                    {'title': 'Cool Dude', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXR3ZWdiNmVwZG16YWg2enhuMnNyMXN1YmRzd2N5eThlbjhkNGMyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lJNoBCvQYp7nq/giphy.gif'},
                    {'title': 'Swagger', 'url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXZ5eGgycnozdWg0b3Nvems0cG4zZTQzbHYzZzR2dGJ6enByMzJ4byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oGRFKJ8Ea3hKkLRyE/giphy.gif'},
                    {'title': 'Sunglasses', 'url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnN4Z2lsNWViZDNnMTNwNmV4c3h5bmd2MDM0ajJyejNqcjVqbmZiZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QkZsca78B7bNu/giphy.gif'},
                    {'title': 'Thumbs Up', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWFyenIydndmNzVpaXZkaTE1Mzh5MDIwYjl3NXEzMmR5ZWJzbjZjeSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3Ky1RlGqJN4xadIyRW/giphy.gif'},
                    {'title': 'Awesome', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExampzMnQ2dnIwNWxlc3pheTI5bTd2aHl1OTFwYXZzMzQwaGt0OTlwZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/I8nepxWwlEuqI/giphy.gif'},
                ]
            },
            'sad': {
                'name': 'Sad',
                'icon': '😢',
                'order': 6,
                'gifs': [
                    {'title': 'Crying', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTR5OGQybjk5ZnJ5YWI0Y2sxNTVmc2tkbGtkbHEzOGtpcGR6eTdnZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ROF8OQvDmxytW/giphy.gif'},
                    {'title': 'Sad Face', 'url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzhkMHhsZGY4OXlyeHY4ZmNwYnYzOWZrMWhwaXczdHRicWxhY2x5ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ISOckXUybVfQ4/giphy.gif'},
                    {'title': 'Disappointed', 'url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExamtpamhscnV6a2ZyZnNkamRncW9qbHdrd2tvdDZ0N2t2dmI0ZGg4MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7qDSOvfaCO9b3MlO/giphy.gif'},
                    {'title': 'Heartbroken', 'url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3R3dzdwMzI4czd6NTZya2VxOTltMnl3OXUzdTR5bzF1d2huYnkxdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jOpLbiGmHR9S0/giphy.gif'},
                    {'title': 'Sad Feels', 'url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXVsdzFjaGpmcXV1NDl6a2g0ZGUzcGNkYTg3azIxbGhic3R1anVydiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/L95W4wv8nnb9K/giphy.gif'},
                ]
            },
            'shocked': {
                'name': 'Shocked',
                'icon': '😲',
                'order': 7,
                'gifs': [
                    {'title': 'Shocked Face', 'url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3Y0cjZ6NjJza3h5dnBvOTU0cnE5bmVrbTR3ZDN5dTRrOWJ1MjFwZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o72EX5QZ9N9d51dqo/giphy.gif'},
                    {'title': 'Surprised', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXpxZDJ4ZnI2YTFudXF3czN2djBpNjNrdHZ1bGU1anE1cjRrNnN4MCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PQKlfexeEpnTq/giphy.gif'},
                    {'title': 'Wow', 'url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnhweTI4YzBodWRyZWpucG04anVhZmE1MGxjYXZ0d2hvajBxejF4bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5VKbvrjxpVJCM/giphy.gif'},
                    {'title': 'Mind Blown', 'url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWw3bzJraWwwYmk5c3VoNDQzd2tjOWhlbnRva2JmYWZuYjYwc3huayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26ufdipQqU2lhNA4g/giphy.gif'},
                    {'title': 'OMG', 'url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGFnanBwN2E4bTF3NGxybndrNTFsd2EwZmI1bTMzNWd2dHJ2aGFtdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5zvSMFG4QshVS/giphy.gif'},
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
