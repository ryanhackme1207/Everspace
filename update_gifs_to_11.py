import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()

from chat.models import GifFile

# Your 11 GIFs to keep
YOUR_GIFS = [
    'Funny Thank You GIF by MOODMAN',
    'The Big Lebowski Thank You GIF',
    'Dog Thank You GIF by MOODMAN',
    'Happy Thank U GIF by Shark Week',
    'Happy Love You GIF by LINE FRIENDS',
    'I Love You Hug GIF',
    'In Love Hearts GIF by SpongeBob SquarePants',
    'Love Me GIF',
    'Seth Meyers Thank You GIF by Late Night with Seth Meyers',
    'Thank U GIF by Best Friends Animal Society',
    'Thank U Reaction GIF by Amanda',
]

print("\n🔍 Removing extra GIFs...\n")

all_gifs = GifFile.objects.all()
gifs_to_delete = []

for gif in all_gifs:
    if gif.title not in YOUR_GIFS:
        gifs_to_delete.append(gif)
        print(f"❌ Deleting: {gif.title}")

print(f"\n🗑️  Deleting {len(gifs_to_delete)} GIFs...")
deleted_count, _ = GifFile.objects.filter(id__in=[g.id for g in gifs_to_delete]).delete()

print(f"✅ Deleted {deleted_count} GIFs")
print(f"📊 Remaining GIFs: {GifFile.objects.count()}\n")

# Show remaining GIFs
remaining = GifFile.objects.all().order_by('title')
for i, gif in enumerate(remaining, 1):
    print(f"{i}. {gif.title} ({gif.pack.name})")

print("\n✨ GIF database updated successfully!")
