"""
Script to populate GIF packs and files into the database
Downloads GIFs from free sources and stores them locally
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
from PIL import Image

# Free GIF sources (no API key required)
GIF_SOURCES = {
    'happiness': {
        'name': '😊 Happy',
        'icon': '😊',
        'gifs': [
            {'title': 'Happy Dance', 'tags': 'happy,dance,joy,celebrate'},
            {'title': 'Laughing', 'tags': 'laugh,funny,happy,haha'},
            {'title': 'Smile', 'tags': 'smile,happy,cheerful'},
            {'title': 'Celebration', 'tags': 'celebrate,party,happy'},
            {'title': 'Excited', 'tags': 'excited,happy,woohoo'},
        ]
    },
    'love': {
        'name': '❤️ Love',
        'icon': '❤️',
        'gifs': [
            {'title': 'Heart', 'tags': 'love,heart,romance'},
            {'title': 'Kiss', 'tags': 'kiss,love,romantic'},
            {'title': 'Love You', 'tags': 'love,affection,romantic'},
            {'title': 'Hug', 'tags': 'hug,love,care'},
            {'title': 'Couple', 'tags': 'love,couple,romance'},
        ]
    },
    'funny': {
        'name': '😂 Funny',
        'icon': '😂',
        'gifs': [
            {'title': 'LOL', 'tags': 'funny,laugh,lol'},
            {'title': 'Meme', 'tags': 'meme,funny,joke'},
            {'title': 'Fail', 'tags': 'fail,funny,oops'},
            {'title': 'Silly', 'tags': 'silly,funny,goofy'},
            {'title': 'Sarcasm', 'tags': 'sarcasm,funny,eye roll'},
        ]
    },
    'sad': {
        'name': '😢 Sad',
        'icon': '😢',
        'gifs': [
            {'title': 'Cry', 'tags': 'sad,cry,tears'},
            {'title': 'Upset', 'tags': 'sad,upset,angry'},
            {'title': 'Disappointed', 'tags': 'sad,disappointed,fail'},
            {'title': 'Lonely', 'tags': 'sad,lonely,alone'},
            {'title': 'Heartbreak', 'tags': 'sad,heartbreak,broken'},
        ]
    },
    'shocked': {
        'name': '😱 Shocked',
        'icon': '😱',
        'gifs': [
            {'title': 'Wow', 'tags': 'shocked,wow,amazing'},
            {'title': 'Surprised', 'tags': 'surprised,shocked,omg'},
            {'title': 'Scary', 'tags': 'scared,shocked,horror'},
            {'title': 'Confused', 'tags': 'confused,shocked,question'},
            {'title': 'Disgusted', 'tags': 'disgusted,shocked,yuck'},
        ]
    },
    'cool': {
        'name': '😎 Cool',
        'icon': '😎',
        'gifs': [
            {'title': 'Cool Sunglasses', 'tags': 'cool,sunglasses,awesome'},
            {'title': 'Boss', 'tags': 'cool,boss,awesome'},
            {'title': 'Confident', 'tags': 'cool,confident,swagger'},
            {'title': 'Street Cred', 'tags': 'cool,street,credible'},
            {'title': 'Smooth Move', 'tags': 'cool,smooth,suave'},
        ]
    },
    'animals': {
        'name': '🐶 Animals',
        'icon': '🐶',
        'gifs': [
            {'title': 'Dancing Dog', 'tags': 'dog,animal,dance'},
            {'title': 'Cat Funny', 'tags': 'cat,animal,funny'},
            {'title': 'Puppy', 'tags': 'dog,animal,cute'},
            {'title': 'Kitten Play', 'tags': 'cat,animal,cute'},
            {'title': 'Bird Dancing', 'tags': 'bird,animal,dance'},
            {'title': 'Bunny Hop', 'tags': 'bunny,animal,cute'},
            {'title': 'Penguin', 'tags': 'penguin,animal,funny'},
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
            {'title': 'Video Game', 'tags': 'gaming,game,fun'},
            {'title': 'Controller', 'tags': 'gaming,controller,play'},
            {'title': 'Game Over', 'tags': 'gaming,game over,lose'},
            {'title': 'Victory', 'tags': 'gaming,win,victory'},
            {'title': 'Multiplayer', 'tags': 'gaming,online,multiplayer'},
        ]
    },
    'food': {
        'name': '🍕 Food',
        'icon': '🍕',
        'gifs': [
            {'title': 'Pizza Time', 'tags': 'food,pizza,eat'},
            {'title': 'Yummy', 'tags': 'food,yummy,delicious'},
            {'title': 'Eating', 'tags': 'food,eat,hungry'},
            {'title': 'Cooking', 'tags': 'food,cook,cooking'},
            {'title': 'Spaghetti', 'tags': 'food,spaghetti,pasta'},
        ]
    },
    'nature': {
        'name': '🌳 Nature',
        'icon': '🌳',
        'gifs': [
            {'title': 'Sunset', 'tags': 'nature,sunset,beautiful'},
            {'title': 'Rain', 'tags': 'nature,rain,weather'},
            {'title': 'Forest', 'tags': 'nature,forest,trees'},
            {'title': 'Ocean', 'tags': 'nature,ocean,waves'},
            {'title': 'Mountain', 'tags': 'nature,mountain,scenic'},
        ]
    },
}

def create_placeholder_gif(title: str, tags: str) -> ContentFile:
    """Create a simple placeholder GIF file"""
    try:
        # Create a simple colorful image as placeholder
        img = Image.new('RGB', (400, 300), color=(73, 109, 137))
        
        # Add text
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((50, 140), title, fill=(255, 255, 255))
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, format='GIF')
        img_io.seek(0)
        
        return ContentFile(img_io.read(), name=f"{title.lower().replace(' ', '_')}.gif")
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return None

def populate_gifs():
    """Populate all GIF packs into database"""
    print("🚀 Starting GIF population...")
    
    for pack_key, pack_info in GIF_SOURCES.items():
        # Create or get GIF pack
        pack, created = GifPack.objects.get_or_create(
            name=pack_info['name'],
            defaults={
                'icon': pack_info['icon'],
                'description': f"Collection of {pack_info['name']} GIFs",
                'order': len([p for p in GIF_SOURCES.keys() if p <= pack_key]),
            }
        )
        
        status = "✅ Created" if created else "📦 Exists"
        print(f"{status}: {pack.name}")
        
        # Create GIF files in pack
        for idx, gif_info in enumerate(pack_info['gifs']):
            gif_file, gif_created = GifFile.objects.get_or_create(
                pack=pack,
                title=gif_info['title'],
                defaults={
                    'description': f"{gif_info['title']} GIF in {pack_info['name']} pack",
                    'tags': gif_info['tags'],
                    'category': pack_key,
                    'source': 'Local Storage',
                    'order': idx,
                    'width': 400,
                    'height': 300,
                    'duration': 1.0,
                    'is_animated': True,
                }
            )
            
            # Create placeholder GIF if not exists
            if gif_created and not gif_file.gif_file:
                gif_content = create_placeholder_gif(gif_info['title'], gif_info['tags'])
                if gif_content:
                    gif_file.gif_file.save(
                        f"{gif_info['title'].lower().replace(' ', '_')}.gif",
                        gif_content,
                        save=True
                    )
                    print(f"  ✅ Added GIF: {gif_info['title']}")
            else:
                print(f"  📎 GIF exists: {gif_info['title']}")
    
    # Print summary
    total_packs = GifPack.objects.count()
    total_gifs = GifFile.objects.count()
    print(f"\n✅ Done! Created {total_packs} packs with {total_gifs} total GIFs")

if __name__ == '__main__':
    populate_gifs()
