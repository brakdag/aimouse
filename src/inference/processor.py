"""
State Processor for the Inference Engine.
Handles normalization of spatial coordinates to the [-1, 1] range.
"""
import numpy as np
from src.common.types import Point, Rect, InputState

class StateProcessor:
    def __init__(self, canvas_width: int, canvas_height: int):
        self.width = canvas_width
        self.height = canvas_height
        self.center_x = canvas_width / 2
        self.center_y = canvas_height / 2
        self.half_w = self.center_x
        self.half_h = self.center_y

    def normalize_coordinate(self, x: float, y: float) -> tuple[float, float]:
        """Converts pixel coordinates to [-1, 1] range.
        
        Args:
            x: Pixel X coordinate.
            y: Pixel Y coordinate.
            
        Returns:
            Tuple of (norm_x, norm_y).
        """
        norm_x = (x - self.center_x) / self.half_w
        norm_y = (y - self.center_y) / self.half_h
        # Clip to ensure strict adherence to range due to float precision
        return float(np.clip(norm_x, -1.0, 1.0)), float(np.clip(norm_y, -1.0, 1.0))

    def process(self, target_rect: Rect, current_pos: Point) -> InputState:
        """Transforms raw spatial data into the 4-feature InputState.
        
        Args:
            target_rect: The target rectangle.
            current_pos: The current cursor position in pixels.
            
        Returns:
            An InputState object with normalized values.
        """
        target_center = target_rect.center
        
        norm_target_x, norm_target_y = self.normalize_coordinate(target_center.x, target_center.y)
        norm_curr_x, norm_curr_y = self.normalize_coordinate(current_pos.x, current_pos.y)
        
        return InputState(
            target_x=norm_target_x,
            target_y=norm_target_y,
            current_x=norm_curr_x,
            current_y=norm_curr_y
        )
