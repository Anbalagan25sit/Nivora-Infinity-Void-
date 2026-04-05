"""
Generate PNG icons from SVG for Chrome extension
Requires: pip install cairosvg pillow
"""

import os
from pathlib import Path

# Try to import cairosvg, if not available use PIL to create simple icons
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

from PIL import Image, ImageDraw

ICON_DIR = Path(__file__).parent / "icons"
SIZES = [16, 32, 48, 128]

def create_icon_with_pil(size: int) -> Image:
    """Create a simple gradient icon using PIL"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw gradient circle background
    center = size // 2
    radius = size // 2 - 2

    for y in range(size):
        for x in range(size):
            # Check if point is within circle
            dx = x - center
            dy = y - center
            if dx*dx + dy*dy <= radius*radius:
                # Gradient from teal to purple
                t = (x + y) / (2 * size)
                r = int(45 + (147 - 45) * t)
                g = int(212 + (51 - 212) * t)
                b = int(191 + (234 - 191) * t)
                img.putpixel((x, y), (r, g, b, 255))

    # Draw microphone icon (simplified)
    mic_color = (255, 255, 255, 255)

    # Microphone body
    mic_width = size // 4
    mic_height = size // 2.5
    mic_x = center - mic_width // 2
    mic_y = center - mic_height // 2 - size // 10

    draw.rounded_rectangle(
        [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height],
        radius=mic_width // 2,
        fill=mic_color
    )

    # Microphone stand arc
    arc_y = center + size // 10
    arc_radius = size // 4
    draw.arc(
        [center - arc_radius, arc_y - arc_radius // 2,
         center + arc_radius, arc_y + arc_radius],
        start=0, end=180, fill=mic_color, width=max(2, size // 16)
    )

    # Microphone stand
    stand_top = arc_y + arc_radius // 2
    stand_bottom = stand_top + size // 8
    draw.line(
        [(center, stand_top), (center, stand_bottom)],
        fill=mic_color, width=max(2, size // 16)
    )

    return img


def main():
    ICON_DIR.mkdir(exist_ok=True)

    for size in SIZES:
        output_path = ICON_DIR / f"icon{size}.png"

        if HAS_CAIROSVG:
            # Convert SVG to PNG using cairosvg
            svg_path = ICON_DIR / "icon.svg"
            if svg_path.exists():
                cairosvg.svg2png(
                    url=str(svg_path),
                    write_to=str(output_path),
                    output_width=size,
                    output_height=size
                )
                print(f"Created {output_path} from SVG")
            else:
                # Create with PIL as fallback
                img = create_icon_with_pil(size)
                img.save(output_path)
                print(f"Created {output_path} with PIL")
        else:
            # Create with PIL
            img = create_icon_with_pil(size)
            img.save(output_path)
            print(f"Created {output_path} with PIL")

    print("\nAll icons generated!")
    print("To use cairosvg for better quality, run: pip install cairosvg")


if __name__ == "__main__":
    main()
