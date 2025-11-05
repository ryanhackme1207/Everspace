import os
import django
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import GifPack, GifFile

# Define which files go into which category
GIF_CATEGORIZATION = {
    'Love': [
        'Happy Love You GIF by LINE FRIENDS.gif',
        'I Love You Hug GIF.gif',
        'In Love Hearts GIF by SpongeBob SquarePants.gif',
        'Love Me GIF.gif',
    ],
    'Funny': [
        'Funny Thank You GIF by MOODMAN.gif',
        'The Big Lebowski Thank You GIF.gif',
    ],
    'Happy': [
        'Happy Thank U GIF by Shark Week.gif',
        'Dog Thank You GIF by MOODMAN.gif',
    ],
    'Work': [
        'Seth Meyers Thank You GIF by Late Night with Seth Meyers.gif',
        'Thank U GIF by Best Friends Animal Society.gif',
        'Thank U Reaction GIF by Amanda.gif',
    ],
}

def organize_gifs():
    """Organize user's GIFs into appropriate packs"""
    gifs_dir = Path('media/gifs')
    
    print("🚀 Starting GIF organization...\n")
    
    for pack_name, gif_files in GIF_CATEGORIZATION.items():
        # Get or create the pack
        pack, created = GifPack.objects.get_or_create(
            name=pack_name,
            defaults={'is_active': True}
        )
        
        if created:
            print(f"📦 Created pack: {pack_name}")
        else:
            print(f"📦 Using existing pack: {pack_name}")
        
        for gif_filename in gif_files:
            gif_path = gifs_dir / gif_filename
            
            if not gif_path.exists():
                print(f"  ⚠️  File not found: {gif_filename}")
                continue
            
            # Extract title from filename (remove .gif and format nicely)
            title = gif_filename.replace('.gif', '').strip()
            
            # Check if GIF already exists
            if GifFile.objects.filter(title=title, pack=pack).exists():
                print(f"  ✓ Already exists: {title}")
                continue
            
            # Create GIF entry
            gif = GifFile.objects.create(
                pack=pack,
                title=title,
                gif_file=f'gifs/{gif_filename}',
                tags=pack_name.lower() + ', thank you, reaction',
                is_active=True
            )
            
            print(f"  ✅ Added: {title}")
    
    print("\n✨ GIF organization complete!")
    
    # Show summary
    print("\n📊 Summary:")
    for pack in GifPack.objects.all():
        count = GifFile.objects.filter(pack=pack).count()
        print(f"  {pack.name}: {count} GIFs")

if __name__ == '__main__':
    organize_gifs()
