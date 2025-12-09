"""
Simple Python script to create extension icons
Uses PIL/Pillow to generate PNG icons
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    print("🎨 Creating extension icons...")
    
    # Ensure icons directory exists
    icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # Vidéotron brand color
    yellow = (255, 210, 0)
    black = (2, 4, 1)
    
    # Create icons for each size
    sizes = [16, 48, 128]
    
    for size in sizes:
        # Create image
        img = Image.new('RGB', (size, size), yellow)
        draw = ImageDraw.Draw(img)
        
        # Draw "E" letter
        font_size = int(size * 0.6)
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw text centered
        text = "E"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill=black, font=font)
        
        # Save
        output_path = os.path.join(icons_dir, f'icon{size}.png')
        img.save(output_path, 'PNG')
        print(f"✅ Created {output_path}")
    
    print("\n🎉 All icons created successfully!")
    print(f"📁 Location: {icons_dir}")
    print("\n✅ You can now load the extension in Chrome!")
    print("   1. Open Chrome: chrome://extensions/")
    print("   2. Enable Developer mode")
    print("   3. Click 'Load unpacked'")
    print("   4. Select: elia-token-extension folder")
    
except ImportError:
    print("❌ PIL/Pillow not installed")
    print("\n📋 Installing Pillow...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'pillow'])
    print("\n✅ Pillow installed! Run this script again.")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📋 Alternative: Create icons manually")
    print("   1. Create 3 simple PNG files (any color)")
    print("   2. Name them: icon16.png, icon48.png, icon128.png")
    print("   3. Place in: elia-token-extension/icons/")
