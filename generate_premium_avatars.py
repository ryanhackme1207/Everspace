"""Generate premium animated pixel avatars with modern designs.
Run: python generate_premium_avatars.py
Creates enhanced 128x128 PNG avatars with better pixel art and effects.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math

SIZE = 128
PIXEL_SCALE = 4  # Pixel size for retro effect

# Premium avatar designs with enhanced color palettes
PREMIUM_AVATARS = {
    'cyber': {
        'base': (15, 15, 25),
        'primary': (0, 255, 200),
        'secondary': (255, 0, 180),
        'accent': (80, 200, 255),
        'design': 'tech_helmet'
    },
    'lotus': {
        'base': (25, 15, 30),
        'primary': (255, 140, 200),
        'secondary': (200, 100, 255),
        'accent': (255, 220, 240),
        'design': 'flower'
    },
    'mech': {
        'base': (20, 20, 20),
        'primary': (180, 180, 190),
        'secondary': (255, 100, 0),
        'accent': (100, 200, 255),
        'design': 'robot_head'
    },
    'serpent': {
        'base': (10, 20, 15),
        'primary': (0, 255, 120),
        'secondary': (255, 230, 0),
        'accent': (0, 180, 90),
        'design': 'snake'
    },
    'phoenix': {
        'base': (40, 10, 0),
        'primary': (255, 140, 0),
        'secondary': (255, 220, 60),
        'accent': (255, 80, 80),
        'design': 'bird'
    },
    'dragon': {
        'base': (20, 0, 30),
        'primary': (200, 50, 255),
        'secondary': (100, 200, 255),
        'accent': (255, 150, 50),
        'design': 'dragon_head'
    },
    'knight': {
        'base': (30, 30, 40),
        'primary': (180, 180, 200),
        'secondary': (200, 150, 80),
        'accent': (255, 200, 100),
        'design': 'helmet'
    },
    'wizard': {
        'base': (15, 10, 40),
        'primary': (100, 80, 255),
        'secondary': (200, 150, 255),
        'accent': (255, 200, 100),
        'design': 'wizard_hat'
    },
    'ninja': {
        'base': (5, 5, 15),
        'primary': (40, 40, 60),
        'secondary': (255, 50, 50),
        'accent': (200, 200, 220),
        'design': 'ninja_mask'
    },
    'astronaut': {
        'base': (0, 10, 30),
        'primary': (200, 200, 220),
        'secondary': (100, 150, 255),
        'accent': (255, 200, 80),
        'design': 'space_helmet'
    },
}

def draw_pixel(draw, x, y, color, scale=PIXEL_SCALE):
    """Draw a scaled pixel."""
    draw.rectangle(
        [x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1],
        fill=color
    )

def draw_tech_helmet(img, colors):
    """Cyber/tech helmet design."""
    draw = ImageDraw.Draw(img)
    s = SIZE // PIXEL_SCALE
    
    # Visor glow
    for y in range(12, 18):
        for x in range(8, 24):
            if 10 <= y <= 15:
                draw_pixel(draw, x, y, colors['primary'])
    
    # Helmet outline
    for x in range(6, 26):
        draw_pixel(draw, x, 8, colors['secondary'])
        draw_pixel(draw, x, 22, colors['secondary'])
    for y in range(8, 23):
        draw_pixel(draw, 6, y, colors['secondary'])
        draw_pixel(draw, 25, y, colors['secondary'])
    
    # Accent lines
    for x in range(10, 22):
        draw_pixel(draw, x, 18, colors['accent'])

def draw_flower(img, colors):
    """Lotus flower design."""
    draw = ImageDraw.Draw(img)
    s = SIZE // PIXEL_SCALE
    cx, cy = s // 2, s // 2
    
    # Petals
    petals = [(cx-4, cy-6), (cx+4, cy-6), (cx-6, cy), (cx+6, cy), (cx-4, cy+6), (cx+4, cy+6)]
    for px, py in petals:
        for dx in range(-2, 3):
            for dy in range(-3, 4):
                if dx*dx + dy*dy <= 6:
                    draw_pixel(draw, px+dx, py+dy, colors['primary'])
    
    # Center
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx*dx + dy*dy <= 8:
                draw_pixel(draw, cx+dx, cy+dy, colors['accent'])

def draw_robot_head(img, colors):
    """Mechanical robot head."""
    draw = ImageDraw.Draw(img)
    s = SIZE // PIXEL_SCALE
    
    # Head rectangle
    for x in range(8, 24):
        for y in range(6, 24):
            draw_pixel(draw, x, y, colors['base'])
    
    # Eyes
    for x in range(11, 14):
        for y in range(12, 16):
            draw_pixel(draw, x, y, colors['secondary'])
    for x in range(18, 21):
        for y in range(12, 16):
            draw_pixel(draw, x, y, colors['secondary'])
    
    # Mouth grille
    for x in range(12, 20):
        for y in [18, 20]:
            draw_pixel(draw, x, y, colors['accent'])

def draw_snake(img, colors):
    """Serpent design."""
    draw = ImageDraw.Draw(img)
    s = SIZE // PIXEL_SCALE
    
    # Snake body spiral
    cx, cy = s // 2, s // 2
    for angle in range(0, 720, 15):
        rad = angle / 180 * math.pi
        r = angle / 100
        x = int(cx + r * math.cos(rad))
        y = int(cy + r * math.sin(rad))
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                draw_pixel(draw, x+dx, y+dy, colors['primary'])
    
    # Head
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            draw_pixel(draw, cx-8+dx, cy-8+dy, colors['secondary'])

def draw_bird(img, colors):
    """Phoenix bird design."""
    draw = ImageDraw.Draw(img)
    s = SIZE // PIXEL_SCALE
    cx, cy = s // 2, s // 2 - 2
    
    # Wings
    for x in range(cx-10, cx-3):
        for y in range(cy-2, cy+4):
            if abs(y-cy) < 4:
                draw_pixel(draw, x, y, colors['primary'])
    for x in range(cx+3, cx+10):
        for y in range(cy-2, cy+4):
            if abs(y-cy) < 4:
                draw_pixel(draw, x, y, colors['primary'])
    
    # Body
    for x in range(cx-3, cx+3):
        for y in range(cy, cy+6):
            draw_pixel(draw, x, y, colors['secondary'])
    
    # Head
    for dx in range(-2, 3):
        for dy in range(-3, 0):
            draw_pixel(draw, cx+dx, cy+dy, colors['accent'])

def draw_generic_avatar(img, colors, design):
    """Generic fallback design."""
    draw = ImageDraw.Draw(img)
    s = SIZE // PIXEL_SCALE
    cx, cy = s // 2, s // 2
    
    # Circular design
    for x in range(s):
        for y in range(s):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if dist < 10:
                if dist < 6:
                    draw_pixel(draw, x, y, colors['primary'])
                elif dist < 9:
                    draw_pixel(draw, x, y, colors['secondary'])
                else:
                    draw_pixel(draw, x, y, colors['accent'])

DESIGN_FUNCTIONS = {
    'tech_helmet': draw_tech_helmet,
    'flower': draw_flower,
    'robot_head': draw_robot_head,
    'snake': draw_snake,
    'bird': draw_bird,
    'dragon_head': draw_generic_avatar,
    'helmet': draw_generic_avatar,
    'wizard_hat': draw_generic_avatar,
    'ninja_mask': draw_generic_avatar,
    'space_helmet': draw_generic_avatar,
}

def generate_avatar(name, spec, outfile):
    """Generate a single premium avatar."""
    img = Image.new('RGBA', (SIZE, SIZE), spec['base'] + (255,))
    
    design_func = DESIGN_FUNCTIONS.get(spec['design'], draw_generic_avatar)
    if spec['design'] in ['dragon_head', 'helmet', 'wizard_hat', 'ninja_mask', 'space_helmet']:
        design_func(img, spec, spec['design'])
    else:
        design_func(img, spec)
    
    # Add glow effect (outer border)
    draw = ImageDraw.Draw(img)
    for i in range(3):
        alpha = 255 - (i * 80)
        glow_color = tuple(list(spec['primary'][:3]) + [alpha])
        draw.rectangle([i, i, SIZE-1-i, SIZE-1-i], outline=glow_color, width=1)
    
    img.save(outfile, 'PNG')

def main():
    # Delete old avatars first
    avatar_dir = Path('chat/static/chat/images/pixel_avatars')
    print(f'🗑️  Removing old avatars from {avatar_dir}...')
    for old_file in avatar_dir.glob('*.png'):
        old_file.unlink()
        print(f'   Deleted: {old_file.name}')
    
    print(f'\n🎨 Generating {len(PREMIUM_AVATARS)} premium animated avatars...\n')
    
    created = []
    for name, spec in PREMIUM_AVATARS.items():
        outfile = avatar_dir / f'{name}.png'
        print(f'✨ Creating premium {name} avatar...')
        generate_avatar(name, spec, outfile)
        created.append(str(outfile))
    
    print(f'\n✅ Done! Created {len(created)} premium avatars.')
    print(f'📁 Location: {avatar_dir.absolute()}')

if __name__ == '__main__':
    main()
