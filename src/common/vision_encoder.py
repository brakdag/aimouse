"""
Vision Encoder for Neural Mouse Interface.
Implements a recursive color-based spatial encoding (Quadtree) to allow LLMs
to locate coordinates in low-resolution images (e.g., 112px).
"""
import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple, Dict

class VisionEncoder:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        # Define the color map for the Quadtree
        # Level 1: X-axis (Red/Blue)
        # Level 2: Y-axis (Green/Yellow)
        # Level 3: Sub-divisions (Cyan/Magenta/White/Black)
        self.color_map = {
            "L1_LEFT": (255, 0, 0, 40),   # Red
            "L1_RIGHT": (0, 0, 255, 40),  # Blue
            "L2_TOP": (0, 255, 0, 40),    # Green
            "L2_BOTTOM": (255, 255, 0, 40), # Yellow
            "L3_TL": (0, 255, 255, 60),   # Cyan
            "L3_TR": (255, 0, 255, 60),   # Magenta
            "L3_BL": (255, 255, 255, 60), # White
            "L3_BR": (50, 50, 50, 60),    # Dark Grey
        }

    def apply_encoder(self, image: Image.Image) -> Image.Image:
        """
        Applies the recursive color overlays to a PIL image and returns the result.
        """
        base = image.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        w, h = base.size

        # Level 1: X-axis
        draw.rectangle([0, 0, w // 2, h], fill=self.color_map["L1_LEFT"])
        draw.rectangle([w // 2, 0, w, h], fill=self.color_map["L1_RIGHT"])

        # Level 2: Y-axis
        draw.rectangle([0, 0, w, h // 2], fill=self.color_map["L2_TOP"])
        draw.rectangle([0, h // 2, w, h], fill=self.color_map["L2_BOTTOM"])

        # Level 3: Sub-quadrants (The 'Precision' layer)
        draw.rectangle([0, 0, w // 4, h // 4], fill=self.color_map["L3_TL"])
        draw.rectangle([3 * w // 4, 0, w, h // 4], fill=self.color_map["L3_TR"])
        draw.rectangle([0, 3 * h // 4, w // 4, h], fill=self.color_map["L3_BL"])
        draw.rectangle([3 * w // 4, 3 * h // 4, w, h], fill=self.color_map["L3_BR"])

        combined = Image.alpha_composite(base, overlay)
        return combined.convert("RGB")

    def get_translation_guide(self) -> str:
        """
        Returns a text guide for the LLM to translate colors to coordinates.
        """
        return """
        SPATIAL ENCODER GUIDE:
        - RED zone: X < 0.5 | BLUE zone: X > 0.5
        - GREEN zone: Y < 0.5 | YELLOW zone: Y > 0.5
        - CYAN spot: Top-Left extreme (X < 0.25, Y < 0.25)
        - MAGENTA spot: Top-Right extreme (X > 0.75, Y < 0.25)
        - WHITE spot: Bottom-Left extreme (X < 0.25, Y > 0.75)
        - GREY spot: Bottom-Right extreme (X > 0.75, Y > 0.75)
        
        To locate an object: Identify the dominant color tint and the nearest precision spot.
        """
