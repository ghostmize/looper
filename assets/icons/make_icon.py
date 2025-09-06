#!/usr/bin/env python3
"""
Generate a proper multi-size .ico file from PNG logos
This ensures Windows displays the correct icon in the taskbar
"""

from PIL import Image
from pathlib import Path

def main():
    SIZES = [32, 48, 64, 128, 256]
    base = Path(__file__).parent.parent / "logos"
    
    imgs = []
    for s in SIZES:
        # Try different naming patterns for the logo files
        possible_names = [
            f"looper_logo_{s}.png",
            f"looper_logo_{s}x{s}.png",
            "looper_logo.png"  # Fallback to main logo
        ]
        
        src_path = None
        for name in possible_names:
            candidate = base / name
            if candidate.exists():
                src_path = candidate
                break
        
        if src_path is None:
            print(f"⚠️ Warning: No logo found for size {s}, skipping...")
            continue
            
        try:
            im = Image.open(src_path).convert("RGBA").resize((s, s), Image.Resampling.LANCZOS)
            imgs.append(im)
            print(f"✓ Added {s}x{s} icon from {src_path.name}")
        except Exception as e:
            print(f"✗ Failed to process {src_path}: {e}")
    
    if not imgs:
        print("✗ No valid images found to create icon")
        return False
    
    # Save as multi-size ICO
    out = Path(__file__).parent / "looper_icon.ico"
    try:
        imgs[0].save(out, format="ICO", sizes=[(i.width, i.height) for i in imgs])
        print(f"✅ Generated multi-size icon: {out}")
        print(f"   Sizes: {[f'{i.width}x{i.height}' for i in imgs]}")
        return True
    except Exception as e:
        print(f"✗ Failed to save ICO: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
