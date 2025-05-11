from PIL import Image, ImageDraw, ImageFont
import os

def create_splash_image():
    # Create a new image with dark background
    width, height = 800, 450
    background_color = (18, 18, 18, 230)  # Semi-transparent dark background
    
    # Create image with alpha channel for transparency
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw background with rounded corners
    corner_radius = 20
    
    # Draw background
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=corner_radius,
        fill=background_color
    )
    
    # Add logo or app name
    try:
        # Try to load a font
        font_size = 60
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Draw app name
        app_name = "OnaPlay"
        text_bbox = draw.textbbox((0, 0), app_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the text
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with a subtle shadow
        draw.text((x+2, y+2), app_name, fill=(0, 0, 0, 150), font=font)
        draw.text((x, y), app_name, fill=(255, 255, 255), font=font)
        
        # Add version text
        version = "v1.0.0"
        version_font_size = 20
        try:
            version_font = ImageFont.truetype("arial.ttf", version_font_size)
        except IOError:
            version_font = ImageFont.load_default()
            
        version_bbox = draw.textbbox((0, 0), version, font=version_font)
        version_width = version_bbox[2] - version_bbox[0]
        version_x = (width - version_width) // 2
        version_y = y + text_height + 10
        
        draw.text((version_x+1, version_y+1), version, fill=(0, 0, 0, 150), font=version_font)
        draw.text((version_x, version_y), version, fill=(200, 200, 200), font=version_font)
        
    except Exception as e:
        print(f"Error adding text: {e}")
    
    # Save the image
    os.makedirs("assets/images", exist_ok=True)
    output_path = os.path.join("assets", "images", "splash.png")
    image.save(output_path, "PNG")
    print(f"Splash screen saved to: {output_path}")

if __name__ == "__main__":
    create_splash_image()
