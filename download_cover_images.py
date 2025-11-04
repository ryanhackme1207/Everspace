"""Download cover images from Unsplash (free stock photos).
Run: python download_cover_images.py

Downloads themed cover images for the cover_choice IDs defined in views.py:
  sunrise, aurora, cosmic, neon, circuit, starfield, horizon, ocean, midnight, crystal

Uses Unsplash Source API (no auth required for basic usage).
Images are saved to chat/static/chat/covers/ as <id>.jpg
"""
import urllib.request
import urllib.error
from pathlib import Path
import time

# Map cover IDs to search queries/themes for Unsplash
COVER_THEMES = {
    'sunrise': 'sunset,sky,gradient',
    'aurora': 'aurora,northern-lights,space',
    'cosmic': 'galaxy,nebula,stars',
    'neon': 'neon,cyberpunk,grid',
    'circuit': 'technology,circuit,dark',
    'starfield': 'stars,night-sky,space',
    'horizon': 'horizon,sunset,landscape',
    'ocean': 'ocean,wave,blue',
    'midnight': 'night,dark,city',
    'crystal': 'crystal,ice,abstract',
}

# Image dimensions for cover photos (1200x400 recommended)
WIDTH = 1200
HEIGHT = 400

def download_image(cover_id: str, query: str, outdir: Path, use_random=True):
    """Download an image from Unsplash Source API."""
    outfile = outdir / f'{cover_id}.jpg'
    
    if outfile.exists():
        print(f'⏭️  Skipping {cover_id} (already exists)')
        return
    
    # Unsplash Source API (public, no auth required)
    # Format: https://source.unsplash.com/{WIDTH}x{HEIGHT}/?{query}
    # Or featured: https://source.unsplash.com/featured/{WIDTH}x{HEIGHT}/?{query}
    url = f'https://source.unsplash.com/featured/{WIDTH}x{HEIGHT}/?{query}'
    
    try:
        print(f'⬇️  Downloading {cover_id} from Unsplash ({query})...')
        headers = {'User-Agent': 'Mozilla/5.0 (Everspace Cover Downloader)'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            
        with open(outfile, 'wb') as f:
            f.write(data)
            
        print(f'✅ Saved {outfile} ({len(data) // 1024} KB)')
        
    except urllib.error.URLError as e:
        print(f'❌ Failed to download {cover_id}: {e}')
    except Exception as e:
        print(f'❌ Error saving {cover_id}: {e}')


def main():
    outdir = Path('chat/static/chat/covers')
    outdir.mkdir(parents=True, exist_ok=True)
    
    print(f'📂 Output directory: {outdir.absolute()}')
    print(f'📥 Downloading {len(COVER_THEMES)} cover images from Unsplash...\n')
    
    for i, (cover_id, query) in enumerate(COVER_THEMES.items(), 1):
        download_image(cover_id, query, outdir)
        
        # Rate limiting: small delay between requests
        if i < len(COVER_THEMES):
            time.sleep(1.5)
    
    print('\n✨ Done! All cover images downloaded.')
    print(f'📁 Files saved to: {outdir.absolute()}')
    print('\n💡 Next steps:')
    print('   1. Review the downloaded images')
    print('   2. Run: python manage.py collectstatic --noinput')
    print('   3. Commit and push to deploy')


if __name__ == '__main__':
    main()
