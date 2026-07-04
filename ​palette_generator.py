import os
from PIL import Image, ImageDraw

def draw_palette_preview(palette: list, save_path: str) -> bool:
    """Generates a high-quality visual reference card containing swatches of the palette."""
    try:
        width = 500
        height = 100
        block_w = width // len(palette)
        
        img = Image.new("RGB", (width, height), "#FFFFFF")
        draw = ImageDraw.Draw(img)
        
        for idx, color in enumerate(palette):
            left = idx * block_w
            right = left + block_w
            draw.rectangle([left, 0, right, height], fill=color['rgb'])
            
        img.save(save_path)
        return True
    except Exception:
        return False

def generate_export_format(palette: list, fmt: str) -> str:
    """Generates code snippets for developer workflows (CSS, SCSS, JSON, Tailwind)."""
    if fmt == "css":
        lines = [":root {"]
        for idx, c in enumerate(palette):
            lines.append(f"  --color-{idx+1}: {c['hex']};")
        lines.append("}")
        return "\n".join(lines)
        
    elif fmt == "tailwind":
        lines = ["colors: {"]
        for idx, c in enumerate(palette):
            lines.append(f"  brand_{idx+1}: '{c['hex']}',")
        lines.append("}")
        return "\n".join(lines)
        
    elif fmt == "json":
        import json
        return json.dumps([c['hex'] for c in palette], indent=2)
        
    return ""

