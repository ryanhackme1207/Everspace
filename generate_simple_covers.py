"""Generate cover images without external dependencies.
Uses only Python standard library to create gradient JPEGs.
Run: python generate_simple_covers.py
"""
from pathlib import Path
import struct
import math

WIDTH = 1200
HEIGHT = 400

def interpolate(c1, c2, t):
    """Linear interpolation between two RGB tuples."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def create_ppm_gradient(colors, width, height, direction='vertical'):
    """Create PPM (portable pixmap) gradient - universal format."""
    pixels = []
    
    for y in range(height):
        row = []
        for x in range(width):
            if direction == 'vertical':
                t = y / height
            elif direction == 'horizontal':
                t = x / width
            else:  # diagonal
                t = (x / width + y / height) / 2
            
            # Multi-color gradient
            segment_count = len(colors) - 1
            segment = min(int(t * segment_count), segment_count - 1)
            local_t = (t * segment_count) - segment
            
            color = interpolate(colors[segment], colors[segment + 1], local_t)
            row.append(color)
        pixels.append(row)
    
    return pixels

def save_ppm(filename, pixels):
    """Save as PPM format (can be converted to JPG later)."""
    height = len(pixels)
    width = len(pixels[0])
    
    with open(filename, 'w') as f:
        f.write('P3\n')
        f.write(f'{width} {height}\n')
        f.write('255\n')
        for row in pixels:
            for r, g, b in row:
                f.write(f'{r} {g} {b} ')
            f.write('\n')

# Cover definitions matching views.py
COVERS = {
    'sunrise': {
        'colors': [(255, 154, 158), (250, 208, 196), (255, 209, 102)],
        'direction': 'vertical'
    },
    'aurora': {
        'colors': [(0, 198, 255), (0, 114, 255), (147, 51, 234)],
        'direction': 'diagonal'
    },
    'cosmic': {
        'colors': [(102, 45, 140), (237, 30, 121), (255, 89, 94)],
        'direction': 'diagonal'
    },
    'neon': {
        'colors': [(18, 194, 233), (196, 113, 237), (246, 79, 89)],
        'direction': 'diagonal'
    },
    'circuit': {
        'colors': [(31, 28, 44), (146, 141, 171)],
        'direction': 'horizontal'
    },
    'starfield': {
        'colors': [(15, 32, 39), (32, 58, 67), (44, 83, 100)],
        'direction': 'vertical'
    },
    'horizon': {
        'colors': [(246, 211, 101), (253, 160, 133), (255, 107, 107)],
        'direction': 'vertical'
    },
    'ocean': {
        'colors': [(33, 147, 176), (109, 213, 237)],
        'direction': 'vertical'
    },
    'midnight': {
        'colors': [(20, 30, 48), (36, 59, 85)],
        'direction': 'vertical'
    },
    'crystal': {
        'colors': [(137, 247, 254), (102, 166, 255)],
        'direction': 'diagonal'
    },
}

def main():
    outdir = Path('chat/static/chat/covers')
    outdir.mkdir(parents=True, exist_ok=True)
    
    print(f'📂 Output directory: {outdir.absolute()}')
    print(f'🎨 Generating {len(COVERS)} cover images (PPM format)...\n')
    print('⚠️  Note: PPM files are large. You may want to convert to JPG manually.')
    print('   Convert using ImageMagick: mogrify -format jpg -quality 90 *.ppm\n')
    
    for cover_id, spec in COVERS.items():
        outfile = outdir / f'{cover_id}.ppm'
        
        if outfile.exists():
            print(f'⏭️  Skipping {cover_id} (already exists)')
            continue
        
        print(f'🎨 Generating {cover_id}...')
        pixels = create_ppm_gradient(
            spec['colors'],
            WIDTH,
            HEIGHT,
            spec['direction']
        )
        save_ppm(outfile, pixels)
        print(f'✅ Saved {outfile}')
    
    print('\n✨ Done!')
    print('\n💡 Next steps:')
    print('   1. Install Pillow: python -m pip install pillow')
    print('   2. Run conversion script (see below)')
    print('   3. Commit JPG files and push\n')
    
    # Create conversion script
    convert_script = outdir.parent.parent.parent / 'convert_ppm_to_jpg.py'
    with open(convert_script, 'w') as f:
        f.write('''"""Convert PPM files to JPG using Pillow."""
from pathlib import Path
from PIL import Image

ppm_dir = Path('chat/static/chat/covers')
for ppm_file in ppm_dir.glob('*.ppm'):
    jpg_file = ppm_file.with_suffix('.jpg')
    print(f'Converting {ppm_file.name} -> {jpg_file.name}')
    img = Image.open(ppm_file)
    img.save(jpg_file, 'JPEG', quality=90, optimize=True)
    ppm_file.unlink()  # Delete PPM after conversion
print('Done!')
''')
    
    print(f'📝 Created conversion script: {convert_script}')
    print('   Run: python convert_ppm_to_jpg.py')

if __name__ == '__main__':
    main()
