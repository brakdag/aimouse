"""
High-level API for the Neural Mouse Interface.
This class serves as the main entry point for external software to interact
with the screen capture, vision encoding, and organic movement systems.
"""
import logging
import time
from src.common.screen_manager import ScreenManager
from src.common.vision_tool import see_image
from src.common.vision_encoder import VisionEncoder
from src.inference.engine import InferenceEngine
from src.common.types import Rect
from src.common.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT

logger = logging.getLogger("nmi_api")

class NeuralMouseInterface:
    def __init__(self, model_path: str = "models/elite_model.onnx"):
        self.screen = ScreenManager()
        self.encoder = VisionEncoder()
        self.model_path = model_path
        self.engine = InferenceEngine(
            model_weights_path=model_path, 
            canvas_width=DEFAULT_CANVAS_WIDTH, 
            canvas_height=DEFAULT_CANVAS_HEIGHT
        )

    def capture_and_encode(self) -> dict:
        """
        Captures the screen in RAM, applies the spatial color encoder, 
        and returns the data ready for an LLM.
        """
        try:
            # Capture directly to PIL Image (In-Memory)
            img = self.screen.capture()
            # Pass the image object directly to vision_tool
            result = see_image(img)
            return result
        except Exception as e:
            logger.error(f"Capture and encode failed: {e}")
            return {"error": str(e)}

    def move_to_rect(self, x: float, y: float, w: float, h: float):
        """
        Moves the mouse organically to a specific normalized rectangle [0, 1].
        """
        try:
            rect_x = x * DEFAULT_CANVAS_WIDTH
            rect_y = y * DEFAULT_CANVAS_HEIGHT
            rect_w = w * DEFAULT_CANVAS_WIDTH
            rect_h = h * DEFAULT_CANVAS_HEIGHT
            
            target_rect = Rect(rect_x, rect_y, rect_w, rect_h)
            success = self.engine.run_task(target_rect)
            return "OK" if success else "ERR: Target not reached"
        except Exception as e:
            logger.error(f"Movement failed: {e}")
            return f"ERR: {e}"

    def perform_action(self, x: float, y: float, w: float, h: float) -> dict:
        """
        The Complete Cycle: 
        1. Move to rect -> 2. Nail the dart & Click -> 3. Wait for UI -> 4. Capture.
        """
        # 1 & 2: Move and Click
        move_result = self.move_to_rect(x, y, w, h)
        
        if "ERR" in move_result:
            return {"status": move_result, "vision": None}

        # 3: Wait for the UI to react (0.5s delay)
        time.sleep(0.5)

        # 4: Capture and Encode the result
        vision_data = self.capture_and_encode()
        
        return {
            "status": "SUCCESS",
            "vision": vision_data
        }

    def get_vision_guide(self) -> str:
        """
        Returns the translation guide for the LLM to interpret the color encoder.
        """
        return self.encoder.get_translation_guide()

# Singleton instance for easy access
nmi = NeuralMouseInterface()