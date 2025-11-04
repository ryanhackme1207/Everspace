"""Convert PPM files to JPG using Pillow."""
from pathlib import Path
from PIL import Image

ppm_dir = Path('chat/static/chat/covers')
for ppm_file in ppm_dir.glob('*.ppm'):
    jpg_file = ppm_file.with_suffix('.jpg')
    print(f'Converting {ppm_file.name} -> {jpg_file.name}')
    img = Image.open(ppm_file)
    img.save(jpg_file, 'JPEG', quality=90, optimize=True)
    ppm_file.unlink()  # Delete PPM after conversion
print('✅ Done! All covers converted to JPG.')
