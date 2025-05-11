from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Create an application icon with the specified size."""
    # Create a new image with transparent background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle with the accent color
    accent_color = (139, 92, 246, 255)  # Purple accent
    margin = int(size * 0.1)
    
    # Draw circle background
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=accent_color
    )
    
    # Draw play triangle
    triangle_size = int(size * 0.4)
    triangle_margin = int(size * 0.3)
    triangle_points = [
        (int(size * 0.4), int(size * 0.3)),  # Left point
        (int(size * 0.4), int(size * 0.7)),  # Bottom left point
        (int(size * 0.7), int(size * 0.5)),  # Right point
    ]
    
    # Draw the triangle
    draw.polygon(triangle_points, fill=(255, 255, 255, 255))
    
    # Save the icon
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)

def generate_all_icons():
    """Generate icons in all required sizes."""
    sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    
    for size in sizes:
        output_path = os.path.join("assets", "icons", f"app_icon_{size}.png")
        create_icon(size, output_path)
        print(f"Generated {output_path}")
    
    # Also create ICO file for Windows
    ico_path = os.path.join("assets", "icons", "app_icon.ico")
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Create a list of images in different sizes
    icons = []
    for width, height in icon_sizes:
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw circle
        margin = int(min(width, height) * 0.1)
        draw.ellipse(
            [margin, margin, width - margin, height - margin],
            fill=(139, 92, 246, 255)
        )
        
        # Draw play triangle
        triangle_size = int(min(width, height) * 0.4)
        triangle_points = [
            (int(width * 0.4), int(height * 0.3)),
            (int(width * 0.4), int(height * 0.7)),
            (int(width * 0.7), int(height * 0.5)),
        ]
        draw.polygon(triangle_points, fill=(255, 255, 255, 255))
        
        icons.append(img)
    
    # Save as ICO
    if icons:
        icons[0].save(ico_path, sizes=[(s[0], s[1]) for s in icon_sizes])
        print(f"Generated {ico_path}")

if __name__ == "__main__":
    generate_all_icons()
