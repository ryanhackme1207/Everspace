"""Generate special cover images for profile cover choices.
Creates JPG files in chat/static/chat/covers/ matching IDs in cover_choices.
Each image is 1600x500 with gradient base + simple overlay pattern.
Run: python generate_special_covers.py
Optional flags:
  --overwrite : regenerate even if file exists
"""
from pathlib import Path
from PIL import Image, ImageDraw
import argparse, math, random

COVERS = {
    'galaxy': {
        'size': (1600, 500),
        'colors': [(30,60,120), (20,30,60), (10,10,25)],
        'stars': 450,
        'effect': 'swirl'
    },
    'nebula': {
        'size': (1600, 500),
        'colors': [(90,0,120), (130,20,40), (30,0,50)],
        'stars': 300,
        'effect': 'cloud'
    },
    'matrix': {
        'size': (1600, 500),
        'colors': [(0,0,0), (0,40,0), (0,80,0)],
        'columns': 140,
        'effect': 'code'
    },
    'flare': {
        'size': (1600, 500),
        'colors': [(250,30,10), (255,150,25), (70,0,0)],
        'effect': 'rays'
    },
    'wave': {
        'size': (1600, 500),
        'colors': [(100,65,165), (42,8,69), (25,10,40)],
        'effect': 'sine'
    },
}

OUTDIR = Path('chat/static/chat/covers')


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i]) * t) for i in range(3))


def base_gradient(size, colors):
    w, h = size
    img = Image.new('RGB', size, colors[0])
    pixels = img.load()
    for y in range(h):
        t = y / (h-1)
        if t < 0.5:
            c = lerp(colors[0], colors[1], t*2)
        else:
            c = lerp(colors[1], colors[2], (t-0.5)*2)
        for x in range(w):
            pixels[x,y] = c
    return img


def effect_swirl(img):
    draw = ImageDraw.Draw(img)
    w,h = img.size
    cx, cy = w//2, h//2
    for r in range(20, min(cx, cy), 25):
        angle_offset = r * 0.04
        for a in range(0, 360, 12):
            ang = math.radians(a + angle_offset)
            x = int(cx + r * math.cos(ang))
            y = int(cy + r * math.sin(ang) * 0.5)
            draw.rectangle([(x-2,y-2),(x+2,y+2)], fill=(255,255,255,))
    # Random small stars
    for _ in range(250):
        x = random.randint(0,w-1); y = random.randint(0,h-1)
        draw.point((x,y), fill=(255,255,255))
    return img


def effect_cloud(img):
    w,h = img.size
    draw = ImageDraw.Draw(img, 'RGBA')
    for _ in range(120):
        rx = random.randint(0,w)
        ry = random.randint(0,h)
        rw = random.randint(60,260)
        rh = random.randint(30,160)
        col = (255, 140+random.randint(-20,20), 200+random.randint(-40,10), random.randint(40,85))
        draw.ellipse([(rx-rw//2, ry-rh//2),(rx+rw//2, ry+rh//2)], fill=col)
    return img


def effect_code(img, columns):
    draw = ImageDraw.Draw(img)
    w,h = img.size
    col_width = w/columns
    for c in range(columns):
        x = int(c*col_width + col_width/2)
        glyph_count = random.randint(4,18)
        y = 10
        for _ in range(glyph_count):
            g_h = random.randint(14,34)
            col = (0, random.randint(150,255), 0)
            draw.rectangle([(x-6,y),(x+6,y+g_h)], fill=col)
            y += g_h + random.randint(4,14)
            if y > h-20:
                break
    return img


def effect_rays(img):
    draw = ImageDraw.Draw(img)
    w,h = img.size
    cx, cy = w//2, h//2
    for a in range(0,360,5):
        length = random.randint(h//2, h)
        ang = math.radians(a)
        x2 = int(cx + length * math.cos(ang))
        y2 = int(cy + length * math.sin(ang))
        col = (255, random.randint(80,160), 40)
        draw.line([(cx,cy),(x2,y2)], fill=col, width=2)
    return img


def effect_sine(img):
    draw = ImageDraw.Draw(img)
    w,h = img.size
    for band in range(8):
        amplitude = 20 + band*5
        offset = band * 50
        col = (150 - band*10, 120 - band*8, 200)
        pts=[]
        for x in range(0,w,8):
            y = int(h/2 + math.sin((x+offset)/80.0) * amplitude)
            pts.append((x,y))
        for p in pts:
            draw.ellipse([(p[0]-4,p[1]-4),(p[0]+4,p[1]+4)], fill=col)
    return img


EFFECT_FUNC = {
    'swirl': effect_swirl,
    'cloud': effect_cloud,
    'code': effect_code,
    'rays': effect_rays,
    'sine': effect_sine,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    created=[]; skipped=[]
    for name, cfg in COVERS.items():
        outfile = OUTDIR / f'{name}.jpg'
        if outfile.exists() and not args.overwrite:
            skipped.append(str(outfile)); continue
        img = base_gradient(cfg['size'], cfg['colors'])
        eff = cfg.get('effect')
        if eff == 'code':
            img = effect_code(img, cfg.get('columns', 120))
        else:
            img = EFFECT_FUNC[eff](img)
        img.save(outfile, quality=88, optimize=True)
        created.append(str(outfile))
    print('Created:', created)
    print('Skipped:', skipped)
    print('Done.')

if __name__ == '__main__':
    main()
