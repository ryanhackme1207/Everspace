"""Generate missing pixel avatar images.
Run: python generate_missing_avatars.py
Creates 64x64 PNGs with simple pixel art placeholders for:
  cyber, lotus, mech, serpent, phoenix
If images already exist they won't be overwritten unless --overwrite passed.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import argparse

AVATARS = {
    'cyber': {
        'bg': (20, 20, 40),
        'fg': (0, 255, 200),
        'accent': (255, 0, 120),
    },
    'lotus': {
        'bg': (30, 10, 30),
        'fg': (255, 140, 200),
        'accent': (200, 255, 240),
    },
    'mech': {
        'bg': (25, 25, 25),
        'fg': (180, 180, 190),
        'accent': (255, 100, 0),
    },
    'serpent': {
        'bg': (10, 30, 15),
        'fg': (0, 200, 90),
        'accent': (255, 255, 120),
    },
    'phoenix': {
        'bg': (40, 15, 0),
        'fg': (255, 120, 0),
        'accent': (255, 200, 60),
    },
}

DEF_SIZE = 64

def draw_avatar(name: str, spec: dict, path: Path):
    img = Image.new('RGBA', (DEF_SIZE, DEF_SIZE), spec['bg'] + (255,))
    d = ImageDraw.Draw(img)
    # Border
    d.rectangle([(2,2),(DEF_SIZE-3, DEF_SIZE-3)], outline=spec['fg'])
    # Central shape (diamond)
    cx = cy = DEF_SIZE//2
    diamond = [(cx, cy-18),(cx+18, cy),(cx, cy+18),(cx-18, cy)]
    d.polygon(diamond, fill=spec['fg'])
    # Accent smaller diamond
    small = [(cx, cy-10),(cx+10, cy),(cx, cy+10),(cx-10, cy)]
    d.polygon(small, fill=spec['accent'])
    # Name initial stylized rectangle bottom
    initial = name[0].upper()
    # Simple pixel font by rectangles
    base_y = DEF_SIZE-18
    d.rectangle([(10, base_y),(DEF_SIZE-11, base_y+12)], fill=spec['bg'], outline=spec['fg'])
    # Put initial as a block pattern
    # We'll just draw a vertical bar + accent
    d.rectangle([(16, base_y+2),(20, base_y+10)], fill=spec['fg'])
    d.rectangle([(22, base_y+2),(24, base_y+10)], fill=spec['accent'])
    img.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files.')
    parser.add_argument('--outdir', default='chat/static/chat/images/pixel_avatars', help='Output directory.')
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []
    for name, spec in AVATARS.items():
        outfile = outdir / f'{name}.png'
        if outfile.exists() and not args.overwrite:
            skipped.append(str(outfile))
            continue
        draw_avatar(name, spec, outfile)
        created.append(str(outfile))

    print('Created:', created)
    print('Skipped (already existed):', skipped)
    print('Done.')

if __name__ == '__main__':
    main()
