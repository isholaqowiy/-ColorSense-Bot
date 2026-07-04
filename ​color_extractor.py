import numpy as np
import colorsys
from PIL import Image
from sklearn.cluster import KMeans

def rgb_to_cmyk(r, g, b):
    """Converts standard RGB ranges down to CMYK boundaries maps."""
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100
    c = 1 - (r / 255)
    m = 1 - (g / 255)
    y = 1 - (b / 255)
    k = min(c, m, y)
    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    return int(c * 100), int(m * 100), int(y * 100), int(k * 100)

def extract_palette(image_path: str, num_colors: int = 5) -> list:
    """Uses K-Means clustering to extract dominant color channels from an image."""
    try:
        with Image.open(image_path) as img:
            # Downsample the image dimension matrix to boost execution speed
            img.thumbnail((150, 150))
            img_rgb = img.convert('RGB')
            pixels = np.array(img_rgb).reshape(-1, 3)
            
        # Execute clustering model calculations
        kmeans = KMeans(n_clusters=num_colors, n_init='auto', random_state=42)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        # Calculate pixel coverage percentages
        counts = np.bincount(labels)
        total_pixels = len(labels)
        
        palette_data = []
        for i in range(len(colors)):
            rgb = tuple(colors[i])
            hex_code = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()
            coverage = int((counts[i] / total_pixels) * 100)
            
            # Calculate alternate color space transformations
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            hls = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            cmyk = rgb_to_cmyk(*rgb)
            
            palette_data.append({
                "hex": hex_code,
                "rgb": rgb,
                "hsv": (int(hsv[0]*360), int(hsv[1]*100), int(hsv[2]*100)),
                "hsl": (int(hls[0]*360), int(hls[2]*100), int(hls[1]*100)),
                "cmyk": cmyk,
                "coverage": coverage
            })
            
        # Sort colors from highest coverage to lowest
        palette_data.sort(key=lambda x: x['coverage'], reverse=True)
        return palette_data
    except Exception:
        return []

