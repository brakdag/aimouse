"""
Screen Manager for Neural Mouse Interface.
Handles high-speed screen capture using 'mss' to keep all data in RAM.
"""
import mss
from PIL import Image
import logging

logger = logging.getLogger("screen_manager")

class ScreenManager:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self) -> Image.Image:
        """
        Captures the primary monitor and returns a PIL Image object.
        No files are written to disk.
        """
        try:
            # Capture the primary monitor
            monitor = self.sct.monitors[1]
            sct_img = self.sct.grab(monitor)
            
            # Convert raw mss pixels to PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            return img
        except Exception as e:
            logger.error(f"MSS capture failed: {e}")
            raise RuntimeError(f"Failed to capture screen in memory: {e}")

    def fast_crop(self, img: Image.Image, crop_rect: list[int]) -> Image.Image:
        """
        Crops a PIL image in memory.
        crop_rect: [left, top, right, bottom]
        """
        return img.crop(crop_rect)
