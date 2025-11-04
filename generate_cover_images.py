"""Generate beautiful gradient cover images locally using Pillow.
Run: python generate_cover_images.py

Creates 1200x400 JPG cover images with smooth gradients and optional overlays
for all cover_choice IDs: sunrise, aurora, cosmic, neon, circuit, starfield, 
horizon, ocean, midnight, crystal
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random

WIDTH = 1200
HEIGHT = 400

def interpolate_color(color1, color2, factor):
    """Interpolate between two RGB colors."""
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))

def create_gradient(width, height, color1, color2, direction='horizontal', steps=None):
    """Create a smooth gradient image."""
    if steps is None:
        steps = height if direction == 'vertical' else width
    
    base = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(base)
    
    for i in range(steps):
        factor = i / steps
        color = interpolate_color(color1, color2, factor)
        
        if direction == 'horizontal':
            x = int(width * factor)
            draw.rectangle([(x, 0), (x + width // steps + 1, height)], fill=color)
        else:
            y = int(height * factor)
            draw.rectangle([(0, y), (width, y + height // steps + 1)], fill=color)
    
    return base

def create_multi_gradient(width, height, colors, direction='diagonal'):
    """Create multi-color gradient."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    if direction == 'diagonal':
        for y in range(height):
            for x in range(width):
                # Calculate position factor (0 to 1) diagonally
                factor = (x / width + y / height) / 2
                # Determine which color pair to interpolate
                segment = min(int(factor * (len(colors) - 1)), len(colors) - 2)
                local_factor = (factor * (len(colors) - 1)) - segment
                color = interpolate_color(colors[segment], colors[segment + 1], local_factor)
                img.putpixel((x, y), color)
    elif direction == 'radial':
        cx, cy = width // 2, height // 2
        max_dist = ((width // 2) ** 2 + (height // 2) ** 2) ** 0.5
        for y in range(height):
            for x in range(width):
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                factor = min(dist / max_dist, 1.0)
                segment = min(int(factor * (len(colors) - 1)), len(colors) - 2)
                local_factor = (factor * (len(colors) - 1)) - segment
                color = interpolate_color(colors[segment], colors[segment + 1], local_factor)
                img.putpixel((x, y), color)
    
    return img

def add_noise_overlay(img, opacity=20):
    """Add subtle noise texture."""
    noise = Image.new('RGB', img.size)
    pixels = noise.load()
    for y in range(img.height):
        for x in range(img.width):
            val = random.randint(-opacity, opacity)
            pixels[x, y] = (val, val, val)
    
    return Image.blend(img, noise, 0.3)

def add_stars(img, count=100):
    """Add star effects to image."""
    draw = ImageDraw.Draw(img)
    for _ in range(count):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        size = random.randint(1, 3)
        brightness = random.randint(180, 255)
        color = (brightness, brightness, brightness)
        draw.ellipse([x, y, x + size, y + size], fill=color)
    return img

COVERS = {
    'sunrise': {
        'colors': [(255, 154, 158), (250, 208, 196), (255, 209, 102)],
        'direction': 'vertical',
        'effects': []
    },
    'aurora': {
        'colors': [(0, 198, 255), (0, 114, 255), (147, 51, 234)],
        'direction': 'diagonal',
        'effects': ['blur']
    },
    'cosmic': {
        'colors': [(102, 45, 140), (237, 30, 121), (255, 89, 94)],
        'direction': 'radial',
        'effects': ['stars']
    },
    'neon': {
        'colors': [(18, 194, 233), (196, 113, 237), (246, 79, 89)],
        'direction': 'diagonal',
        'effects': []
    },
    'circuit': {
        'colors': [(31, 28, 44), (146, 141, 171)],
        'direction': 'horizontal',
        'effects': ['noise']
    },
    'starfield': {
        'colors': [(15, 32, 39), (32, 58, 67), (44, 83, 100)],
        'direction': 'vertical',
        'effects': ['stars']
    },
    'horizon': {
        'colors': [(246, 211, 101), (253, 160, 133), (255, 107, 107)],
        'direction': 'vertical',
        'effects': []
    },
    'ocean': {
        'colors': [(33, 147, 176), (109, 213, 237)],
        'direction': 'vertical',
        'effects': []
    },
    'midnight': {
        'colors': [(20, 30, 48), (36, 59, 85)],
        'direction': 'vertical',
        'effects': ['stars']
    },
    'crystal': {
        'colors': [(137, 247, 254), (102, 166, 255)],
        'direction': 'diagonal',
        'effects': ['blur']
    },
}

def generate_cover(cover_id: str, spec: dict, outdir: Path):
    """Generate a single cover image."""
    outfile = outdir / f'{cover_id}.jpg'
    
    if outfile.exists():
        print(f'⏭️  Skipping {cover_id} (already exists)')
        return
    
    print(f'🎨 Generating {cover_id}...')
    
    # Create base gradient
    if spec['direction'] in ['diagonal', 'radial']:
        img = create_multi_gradient(WIDTH, HEIGHT, spec['colors'], spec['direction'])
    else:
        img = create_gradient(WIDTH, HEIGHT, spec['colors'][0], spec['colors'][-1], spec['direction'])
    
    # Apply effects
    for effect in spec.get('effects', []):
        if effect == 'noise':
            img = add_noise_overlay(img)
        elif effect == 'stars':
            img = add_stars(img, count=150)
        elif effect == 'blur':
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    # Save with high quality
    img.save(outfile, 'JPEG', quality=95, optimize=True)
    print(f'✅ Saved {outfile}')

def main():
    outdir = Path('chat/static/chat/covers')
    outdir.mkdir(parents=True, exist_ok=True)
    
    print(f'📂 Output directory: {outdir.absolute()}')
    print(f'🎨 Generating {len(COVERS)} cover images...\n')
    
    for cover_id, spec in COVERS.items():
        generate_cover(cover_id, spec, outdir)
    
    print('\n✨ Done! All cover images generated.')
    print(f'📁 Files saved to: {outdir.absolute()}')
    print('\n💡 Next steps:')
    print('   1. Review the generated images')
    print('   2. Run: python manage.py collectstatic --noinput (for production)')
    print('   3. Commit and push to deploy')

if __name__ == '__main__':
    main()
