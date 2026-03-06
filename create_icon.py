#!/usr/bin/env python3
"""
Create application icons for SAP AI Core LLM Proxy.
This script generates a simple icon using Pillow.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create application icons in various sizes."""
    # Create a 256x256 base icon
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle background with gradient-like effect
    # Main background color (purple/blue gradient simulation)
    for i in range(size):
        # Create a gradient from purple to blue
        r = int(102 + (118 - 102) * i / size)  # 667eea to 764ba2
        g = int(126 + (75 - 126) * i / size)
        b = int(234 + (162 - 234) * i / size)
        draw.line([(0, i), (size, i)], fill=(r, g, b, 255))
    
    # Create a circular mask for rounded corners
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    # Draw rounded rectangle
    corner_radius = 50
    mask_draw.rounded_rectangle([(0, 0), (size-1, size-1)], radius=corner_radius, fill=255)
    
    # Apply mask
    img.putalpha(mask)
    
    # Draw "AI" text
    # Try to use a system font, fallback to default if not available
    try:
        # Try different font paths
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 120)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Draw text "AI" in white
    text = "AI"
    draw = ImageDraw.Draw(img)
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]
    
    # Draw text with shadow for depth
    shadow_offset = 3
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 100), font=font)
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Draw a small "SAP" text at bottom
    try:
        small_font = ImageFont.truetype(font_paths[0] if os.path.exists(font_paths[0]) else font_paths[1], 30)
    except:
        small_font = ImageFont.load_default()
    
    sap_text = "SAP"
    sap_bbox = draw.textbbox((0, 0), sap_text, font=small_font)
    sap_width = sap_bbox[2] - sap_bbox[0]
    sap_x = (size - sap_width) // 2
    sap_y = size - 50
    draw.text((sap_x, sap_y), sap_text, fill=(255, 255, 255, 200), font=small_font)
    
    # Save in different sizes
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Create icons directory if it doesn't exist
    os.makedirs('icons', exist_ok=True)
    
    # Save PNG icons
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(f'icons/icon_{s}x{s}.png')
        print(f"Created icons/icon_{s}x{s}.png")
    
    # Save main icon as icon.png
    img.save('icons/icon.png')
    print("Created icons/icon.png")
    
    # Create ICO file (Windows icon format) with multiple sizes
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []
    for s in ico_sizes:
        resized = img.resize(s, Image.Resampling.LANCZOS)
        ico_images.append(resized)
    
    # Save as ICO
    img.save('icons/app.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("Created icons/app.ico")
    
    print("\nIcon creation complete!")
    print("Files created in 'icons/' directory:")
    for f in os.listdir('icons'):
        print(f"  - {f}")


if __name__ == '__main__':
    create_icon()