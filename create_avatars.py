from PIL import Image, ImageDraw
import os

def create_pixel_avatar(name, primary_color, secondary_color, pattern_type="basic"):
    """Create a simple pixel art avatar"""
    # Create 64x64 image
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Scale factor for pixel art effect
    pixel_size = 4
    
    if pattern_type == "robot":
        # Robot face pattern
        # Head
        draw.rectangle([8, 8, 56, 56], fill=primary_color)
        # Eyes
        draw.rectangle([16, 20, 24, 28], fill=secondary_color)
        draw.rectangle([40, 20, 48, 28], fill=secondary_color)
        # Mouth
        draw.rectangle([24, 40, 40, 44], fill=secondary_color)
        # Antenna
        draw.rectangle([28, 4, 36, 12], fill=secondary_color)
    elif pattern_type == "alien":
        # Alien face pattern
        # Head (larger, oval-ish)
        draw.ellipse([4, 8, 60, 52], fill=primary_color)
        # Large eyes
        draw.ellipse([12, 16, 24, 28], fill=secondary_color)
        draw.ellipse([40, 16, 52, 28], fill=secondary_color)
        # Small mouth
        draw.rectangle([28, 36, 36, 40], fill=secondary_color)
    elif pattern_type == "knight":
        # Knight helmet pattern
        # Helmet
        draw.rectangle([8, 8, 56, 56], fill=primary_color)
        # Visor
        draw.rectangle([16, 20, 48, 32], fill=secondary_color)
        # Breathing holes
        draw.rectangle([20, 36, 24, 40], fill=secondary_color)
        draw.rectangle([28, 36, 32, 40], fill=secondary_color)
        draw.rectangle([36, 36, 40, 40], fill=secondary_color)
        draw.rectangle([44, 36, 48, 40], fill=secondary_color)
    elif pattern_type == "wizard":
        # Wizard hat and face
        # Hat
        draw.polygon([(32, 4), (12, 20), (52, 20)], fill=primary_color)
        # Face
        draw.rectangle([16, 20, 48, 52], fill=secondary_color)
        # Eyes
        draw.rectangle([20, 28, 24, 32], fill=primary_color)
        draw.rectangle([40, 28, 44, 32], fill=primary_color)
        # Beard
        draw.rectangle([20, 44, 44, 56], fill=primary_color)
    elif pattern_type == "cat":
        # Cat face
        # Head
        draw.ellipse([12, 16, 52, 52], fill=primary_color)
        # Ears
        draw.polygon([(16, 16), (24, 8), (20, 20)], fill=primary_color)
        draw.polygon([(40, 20), (44, 8), (48, 16)], fill=primary_color)
        # Eyes
        draw.ellipse([18, 24, 26, 32], fill=secondary_color)
        draw.ellipse([38, 24, 46, 32], fill=secondary_color)
        # Nose
        draw.polygon([(30, 32), (34, 32), (32, 36)], fill=secondary_color)
        # Mouth
        draw.arc([26, 36, 38, 44], 0, 180, fill=secondary_color)
    else:  # basic pattern
        # Simple geometric pattern
        draw.rectangle([16, 16, 48, 48], fill=primary_color)
        draw.ellipse([20, 20, 32, 32], fill=secondary_color)
        draw.ellipse([32, 32, 44, 44], fill=secondary_color)
    
    return img

# Avatar configurations
avatars = [
    ("robot", "#4ECDC4", "#FF6B6B", "robot"),
    ("alien", "#96CEB4", "#FECA57", "alien"),
    ("knight", "#718096", "#4ECDC4", "knight"),
    ("wizard", "#9F7AEA", "#ED8936", "wizard"),
    ("ninja", "#2D3748", "#4ECDC4", "basic"),
    ("pirate", "#8B4513", "#FFD700", "basic"),
    ("cat", "#F7931E", "#FFFFFF", "cat"),
    ("dog", "#8B4513", "#FFFFFF", "basic"),
    ("dragon", "#E53E3E", "#68D391", "basic"),
    ("unicorn", "#ED64A6", "#FFFFFF", "basic"),
    ("ghost", "#FFFFFF", "#4A5568", "basic"),
    ("monster", "#38B2AC", "#E53E3E", "basic"),
    ("astronaut", "#FFFFFF", "#4299E1", "basic"),
    ("viking", "#8B4513", "#FFD700", "basic"),
    ("samurai", "#2D3748", "#E53E3E", "basic"),
    ("mage", "#805AD5", "#4299E1", "wizard"),
]

# Create directory if it doesn't exist
avatar_dir = "C:/Users/Acer Nitro 5/Desktop/project 3/chat/static/chat/images/pixel_avatars"
os.makedirs(avatar_dir, exist_ok=True)

# Generate avatar images
for name, primary, secondary, pattern in avatars:
    img = create_pixel_avatar(name, primary, secondary, pattern)
    img.save(f"{avatar_dir}/{name}.png", "PNG")
    print(f"Created {name}.png")

# Create default avatar and cover images
default_avatar = create_pixel_avatar("default", "#4ECDC4", "#FF6B6B", "basic")
default_avatar.save("C:/Users/Acer Nitro 5/Desktop/project 3/chat/static/chat/images/default_avatar.png", "PNG")

# Create default cover image
cover_img = Image.new('RGB', (1200, 400), '#FF6B6B')
draw = ImageDraw.Draw(cover_img)
# Add gradient effect
for y in range(400):
    r = int(255 * (1 - y/400) + 78 * (y/400))  
    g = int(107 * (1 - y/400) + 205 * (y/400))  
    b = int(107 * (1 - y/400) + 196 * (y/400))  
    draw.line([(0, y), (1200, y)], fill=(r, g, b))

cover_img.save("C:/Users/Acer Nitro 5/Desktop/project 3/chat/static/chat/images/default_cover.jpg", "JPEG")

print("All avatar images created successfully!")