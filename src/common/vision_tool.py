"""
Vision Tool for Neural Mouse Interface.
Handles image processing, encoding, and base64 conversion for LLM consumption.
"""
import os
import io
import base64
import logging
from typing import Optional, List, Union
from PIL import Image
from .core_tools import context, ToolError
from .vision_encoder import VisionEncoder
from ..core.validation import BaseValidator, ValidationError

logger = logging.getLogger("tools")

class SeeImageArgs(BaseValidator):
    path: Optional[str] = None
    crop: Optional[List[int]] = None

    def __init__(self, path: Optional[str] = None, crop: Optional[List[int]] = None):
        self.path = path
        self.crop = crop
        if self.crop and len(self.crop) != 4:
            raise ValidationError("El parámetro 'crop' debe ser una lista de 4 enteros: [left, top, right, bottom].")

def see_image(image_input: Union[str, Image.Image], crop: Optional[List[int]] = None) -> dict:
    """
    Permite al agente ver una imagen (ruta o objeto PIL) con validación de argumentos.
    """
    try:
        # 1. Handle input: Path or PIL Image
        if isinstance(image_input, str):
            safe_path = context.get_safe_path(image_input)
            if not os.path.isfile(safe_path):
                raise ToolError(f"Imagen no encontrada en '{image_input}'.")
            img = Image.open(safe_path)
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            raise ToolError("El input debe ser una ruta de archivo (str) o un objeto PIL Image.")

        # 2. Crop if requested
        if crop:
            crop_tuple = (crop[0], crop[1], crop[2], crop[3])
            img = img.crop(crop_tuple)

        # 3. Process for LLM (Resize and Encode)
        # We apply the Spatial Encoder before resizing to maintain color block integrity
        encoder = VisionEncoder()
        img = encoder.apply_encoder(img)

        width, height = img.size
        aspect_ratio = width / height
        if width < height:
            new_width = 112
            new_height = int(112 / aspect_ratio)
        else:
            new_height = 112
            new_width = int(112 * aspect_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return {
            "mime_type": "image/jpeg",
            "data": base64_data,
            "resolution": f"{new_width}x{new_height}"
        }

    except Exception as e:
        logger.exception(f"Error procesando imagen: {e}")
        raise ToolError(f"Error procesando la imagen: {e}")