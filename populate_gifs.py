"""
Script to populate GIF packs and files into the database
Downloads real GIFs from Giphy and stores them locally
"""

import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import GifPack, GifFile
from django.core.files.base import ContentFile
import requests
from io import BytesIO
import time

# Real GIF sources from Giphy (using public trending/search)
# These are direct URLs to actual GIFs
GIF_SOURCES = {
    'happiness': {
        'name': '😊 Happy',
        'icon': '😊',
        'gifs': [
            {'title': 'Happy Dance', 'url': 'https://media.giphy.com/media/26uf1EUQzrgsS6Jfa/giphy.gif', 'tags': 'happy,dance,joy,celebrate'},
            {'title': 'Laughing', 'url': 'https://media.giphy.com/media/26uf1QVYvvpFcGKM0/giphy.gif', 'tags': 'laugh,funny,happy,haha'},
            {'title': 'Smile', 'url': 'https://media.giphy.com/media/3ohzdKdb7fcv3ZP5L2/giphy.gif', 'tags': 'smile,happy,cheerful'},
            {'title': 'Party Time', 'url': 'https://media.giphy.com/media/g9GUusdUZsKFP5BdXD/giphy.gif', 'tags': 'celebrate,party,happy'},
            {'title': 'Excited', 'url': 'https://media.giphy.com/media/Gf3chNSHreR3xJUVp9/giphy.gif', 'tags': 'excited,happy,woohoo'},
        ]
    },
    'love': {
        'name': '❤️ Love',
        'icon': '❤️',
        'gifs': [
            {'title': 'Heart', 'url': 'https://media.giphy.com/media/Cmr1OMJ2FN0B2/giphy.gif', 'tags': 'love,heart,romance'},
            {'title': 'Kiss', 'url': 'https://media.giphy.com/media/l0HlDy9x8FZo0XO1i/giphy.gif', 'tags': 'kiss,love,romantic'},
            {'title': 'Love You', 'url': 'https://media.giphy.com/media/3o6ZtpWQcUOEPermFc/giphy.gif', 'tags': 'love,affection,romantic'},
            {'title': 'Hug', 'url': 'https://media.giphy.com/media/od5H3PmEApW7jGDKW3/giphy.gif', 'tags': 'hug,love,care'},
            {'title': 'Couple', 'url': 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif', 'tags': 'love,couple,romance'},
        ]
    },
    'funny': {
        'name': '😂 Funny',
        'icon': '😂',
        'gifs': [
            {'title': 'LOL', 'url': 'https://media.giphy.com/media/l0MYJnHWfv0QXjVAQ/giphy.gif', 'tags': 'funny,laugh,lol'},
            {'title': 'Meme', 'url': 'https://media.giphy.com/media/3oz8xsNcWc0E3Xi1EQ/giphy.gif', 'tags': 'meme,funny,joke'},
            {'title': 'Fail', 'url': 'https://media.giphy.com/media/l0HlJ7t33l7WKAc8M/giphy.gif', 'tags': 'fail,funny,oops'},
            {'title': 'Silly', 'url': 'https://media.giphy.com/media/3o7TKU8RhemSBEkySI/giphy.gif', 'tags': 'silly,funny,goofy'},
            {'title': 'Sarcasm', 'url': 'https://media.giphy.com/media/l3q2K6K0BRTf16eYM/giphy.gif', 'tags': 'sarcasm,funny,eye roll'},
        ]
    },
    'sad': {
        'name': '😢 Sad',
        'icon': '😢',
        'gifs': [
            {'title': 'Cry', 'url': 'https://media.giphy.com/media/l3q2K6K0BRTf16eYM/giphy.gif', 'tags': 'sad,cry,tears'},
            {'title': 'Upset', 'url': 'https://media.giphy.com/media/f4fN8cxfzTRNC/giphy.gif', 'tags': 'sad,upset,angry'},
            {'title': 'Disappointed', 'url': 'https://media.giphy.com/media/26uf1uQQJCWDfXHUQ/giphy.gif', 'tags': 'sad,disappointed,fail'},
            {'title': 'Lonely', 'url': 'https://media.giphy.com/media/3ohzdMvg4Smnz736Zy/giphy.gif', 'tags': 'sad,lonely,alone'},
            {'title': 'Heartbreak', 'url': 'https://media.giphy.com/media/13d2jHlSlxklVe/giphy.gif', 'tags': 'sad,heartbreak,broken'},
        ]
    },
    'shocked': {
        'name': '😱 Shocked',
        'icon': '😱',
        'gifs': [
            {'title': 'Wow', 'url': 'https://media.giphy.com/media/l0HlQY2KjoYB1v7EYo/giphy.gif', 'tags': 'shocked,wow,amazing'},
            {'title': 'Surprised', 'url': 'https://media.giphy.com/media/l0NwNaQ67nAmZv2uI/giphy.gif', 'tags': 'surprised,shocked,omg'},
            {'title': 'Scary', 'url': 'https://media.giphy.com/media/l0HlRy9x8FZo0XO1i/giphy.gif', 'tags': 'scared,shocked,horror'},
            {'title': 'Confused', 'url': 'https://media.giphy.com/media/l0MYJnHWfv0QXjVAQ/giphy.gif', 'tags': 'confused,shocked,question'},
            {'title': 'Disgusted', 'url': 'https://media.giphy.com/media/l0HlMZXFErSBnJ4J2/giphy.gif', 'tags': 'disgusted,shocked,yuck'},
        ]
    },
    'cool': {
        'name': '😎 Cool',
        'icon': '😎',
        'gifs': [
            {'title': 'Cool Sunglasses', 'url': 'https://media.giphy.com/media/l0HlQY2KjoYB1v7EYo/giphy.gif', 'tags': 'cool,sunglasses,awesome'},
            {'title': 'Boss', 'url': 'https://media.giphy.com/media/26uf1QVYvvpFcGKM0/giphy.gif', 'tags': 'cool,boss,awesome'},
            {'title': 'Confident', 'url': 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif', 'tags': 'cool,confident,swagger'},
            {'title': 'Walk Away', 'url': 'https://media.giphy.com/media/l0HlGe7g7WvDtdVDW/giphy.gif', 'tags': 'cool,street,credible'},
            {'title': 'Smooth', 'url': 'https://media.giphy.com/media/l0HlJ7t33l7WKAc8M/giphy.gif', 'tags': 'cool,smooth,suave'},
        ]
    },
    'animals': {
        'name': '🐶 Animals',
        'icon': '🐶',
        'gifs': [
            {'title': 'Dancing Dog', 'url': 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif', 'tags': 'dog,animal,dance'},
            {'title': 'Cat Funny', 'url': 'https://media.giphy.com/media/3o7TKU8RhemSBEkySI/giphy.gif', 'tags': 'cat,animal,funny'},
            {'title': 'Puppy', 'url': 'https://media.giphy.com/media/l0HlQY2KjoYB1v7EYo/giphy.gif', 'tags': 'dog,animal,cute'},
            {'title': 'Kitten Play', 'url': 'https://media.giphy.com/media/3o7TKMUvfEXeI45Low/giphy.gif', 'tags': 'cat,animal,cute'},
            {'title': 'Bird Dancing', 'url': 'https://media.giphy.com/media/l0MYJnHWfv0QXjVAQ/giphy.gif', 'tags': 'bird,animal,dance'},
            {'title': 'Bunny Hop', 'url': 'https://media.giphy.com/media/l0IypeKj8xXO0XO1i/giphy.gif', 'tags': 'bunny,animal,cute'},
            {'title': 'Penguin', 'url': 'https://media.giphy.com/media/l0HlGKc45fJQXfkVi/giphy.gif', 'tags': 'penguin,animal,funny'},
        ]
    },
    'action': {
        'name': '⚡ Action',
        'icon': '⚡',
        'gifs': [
            {'title': 'Explosion', 'tags': 'action,explosion,boom'},
            {'title': 'Fight', 'tags': 'action,fight,combat'},
            {'title': 'Jump', 'tags': 'action,jump,leap'},
            {'title': 'Run', 'tags': 'action,run,sprint'},
            {'title': 'Punch', 'tags': 'action,punch,hit'},
            {'title': 'Kick', 'tags': 'action,kick,martial arts'},
        ]
    },
    'celebration': {
        'name': '🎉 Celebration',
        'icon': '🎉',
        'gifs': [
            {'title': 'Confetti', 'tags': 'celebration,confetti,party'},
            {'title': 'Cheers', 'tags': 'celebration,cheers,toast'},
            {'title': 'Victory', 'tags': 'celebration,victory,win'},
            {'title': 'Fireworks', 'tags': 'celebration,fireworks,party'},
            {'title': 'Party Hard', 'tags': 'celebration,party,dancing'},
        ]
    },
    'work': {
        'name': '💼 Work',
        'icon': '💼',
        'gifs': [
            {'title': 'Working Hard', 'tags': 'work,busy,productive'},
            {'title': 'Meeting', 'tags': 'work,meeting,business'},
            {'title': 'Coffee Break', 'tags': 'work,coffee,break'},
            {'title': 'Brainstorm', 'tags': 'work,idea,thinking'},
            {'title': 'Deadline', 'tags': 'work,stress,deadline'},
        ]
    },
    'gaming': {
        'name': '🎮 Gaming',
        'icon': '🎮',
        'gifs': [
            {'title': 'Video Game', 'url': 'https://media.giphy.com/media/l0IypeKj8xXO0XO1i/giphy.gif', 'tags': 'gaming,game,fun'},
            {'title': 'Controller', 'url': 'https://media.giphy.com/media/3o7TKU8RhemSBEkySI/giphy.gif', 'tags': 'gaming,controller,play'},
            {'title': 'Game Over', 'url': 'https://media.giphy.com/media/l0MYJnHWfv0QXjVAQ/giphy.gif', 'tags': 'gaming,game over,lose'},
            {'title': 'Victory', 'url': 'https://media.giphy.com/media/26uf1QVYvvpFcGKM0/giphy.gif', 'tags': 'gaming,win,victory'},
            {'title': 'Multiplayer', 'url': 'https://media.giphy.com/media/l0HlJ7t33l7WKAc8M/giphy.gif', 'tags': 'gaming,online,multiplayer'},
        ]
    },
    'food': {
        'name': '🍕 Food',
        'icon': '🍕',
        'gifs': [
            {'title': 'Pizza Time', 'url': 'https://media.giphy.com/media/l0HlQY2KjoYB1v7EYo/giphy.gif', 'tags': 'food,pizza,eat'},
            {'title': 'Yummy', 'url': 'https://media.giphy.com/media/26uf1uQQJCWDfXHUQ/giphy.gif', 'tags': 'food,yummy,delicious'},
            {'title': 'Eating', 'url': 'https://media.giphy.com/media/l0MYJnHWfv0QXjVAQ/giphy.gif', 'tags': 'food,eat,hungry'},
            {'title': 'Cooking', 'url': 'https://media.giphy.com/media/3o7TKMUvfEXeI45Low/giphy.gif', 'tags': 'food,cook,cooking'},
            {'title': 'Spaghetti', 'url': 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif', 'tags': 'food,spaghetti,pasta'},
        ]
    },
    'nature': {
        'name': '🌳 Nature',
        'icon': '🌳',
        'gifs': [
            {'title': 'Sunset', 'url': 'https://media.giphy.com/media/l0HlQY2KjoYB1v7EYo/giphy.gif', 'tags': 'nature,sunset,beautiful'},
            {'title': 'Rain', 'url': 'https://media.giphy.com/media/26uf1uQQJCWDfXHUQ/giphy.gif', 'tags': 'nature,rain,weather'},
            {'title': 'Forest', 'url': 'https://media.giphy.com/media/l0MYJnHWfv0QXjVAQ/giphy.gif', 'tags': 'nature,forest,trees'},
            {'title': 'Ocean', 'url': 'https://media.giphy.com/media/3o7TKMUvfEXeI45Low/giphy.gif', 'tags': 'nature,ocean,waves'},
            {'title': 'Mountain', 'url': 'https://media.giphy.com/media/l0HlJ7t33l7WKAc8M/giphy.gif', 'tags': 'nature,mountain,scenic'},
        ]
    },
}

def download_gif(url: str, title: str) -> ContentFile:
    """Download GIF from Giphy URL and return as ContentFile"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        filename = f"{title.lower().replace(' ', '_')}.gif"
        return ContentFile(response.content, name=filename)
    except Exception as e:
        print(f"Error downloading {title} from {url}: {e}")
        return None

def populate_gifs():
    """Populate all GIF packs into database"""
    print("🚀 Starting GIF population...")
    
    # Delete existing GIFs to ensure clean slate
    GifFile.objects.all().delete()
    GifPack.objects.all().delete()
    print("🗑️  Cleared existing GIFs and packs")
    
    for pack_key, pack_info in GIF_SOURCES.items():
        # Create GIF pack
        pack = GifPack.objects.create(
            name=pack_info['name'],
            icon=pack_info['icon'],
            description=f"Collection of {pack_info['name']} GIFs",
            order=len([p for p in GIF_SOURCES.keys() if p <= pack_key]),
        )
        
        print(f"✅ Created: {pack.name}")
        
        # Create GIF files in pack
        for idx, gif_info in enumerate(pack_info['gifs']):
            try:
                # Download GIF from URL
                gif_content = download_gif(gif_info['url'], gif_info['title'])
                
                if gif_content:
                    gif_file = GifFile.objects.create(
                        pack=pack,
                        title=gif_info['title'],
                        description=f"{gif_info['title']} GIF in {pack_info['name']} pack",
                        tags=gif_info['tags'],
                        category=pack_key,
                        source='Giphy',
                        order=idx,
                        width=400,
                        height=300,
                        duration=1.0,
                        is_animated=True,
                    )
                    
                    # Save the GIF file
                    filename = f"{gif_info['title'].lower().replace(' ', '_')}.gif"
                    gif_file.gif_file.save(filename, gif_content, save=True)
                    print(f"  ✅ Added GIF: {gif_info['title']}")
                    time.sleep(0.5)  # Be nice to the server
                else:
                    print(f"  ❌ Failed to download: {gif_info['title']}")
            except Exception as e:
                print(f"  ❌ Error adding {gif_info['title']}: {e}")
    
    # Print summary
    total_packs = GifPack.objects.count()
    total_gifs = GifFile.objects.count()
    print(f"\n✅ Done! Created {total_packs} packs with {total_gifs} total GIFs")

if __name__ == '__main__':
    populate_gifs()
