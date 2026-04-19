"""
State Processor for the Inference Engine.
Handles normalization of distance and relative angle for the agent.
"""
import numpy as np
import math
from src.common.types import Point, Rect, InputState

class StateProcessor:
    def __init__(self, canvas_width: int, canvas_height: int):
        self.width = canvas_width
        self.height = canvas_height
        self.max_diagonal = np.sqrt(canvas_width**2 + canvas_height**2)

    def process(self, target_rect: Rect, agent_state: 'AgentState') -> InputState:
        """
        Transforms raw spatial data into a distance and relative angle pair.
        
        Args:
            target_rect: The target rectangle.
            agent_state: The current state of the agent (including angle).
            
        Returns:
            An InputState object with normalized distance and relative angle.
        """
        target_center = target_rect.center
        pos = agent_state.position
        
        # 1. Distance Calculation
        dist = np.sqrt((target_center.x - pos.x)**2 + (target_center.y - pos.y)**2)
        norm_dist = float(np.clip(dist / self.max_diagonal, 0.0, 1.0))
        # Map [0, 1] -> [-1, 1]
        mapped_dist = (norm_dist * 2.0) - 1.0
        
        # 2. Relative Angle Calculation
        # Angle from agent to target
        angle_to_target = math.atan2(target_center.y - pos.y, target_center.x - pos.x)
        
        # Difference between target angle and agent's current facing angle
        rel_angle = angle_to_target - agent_state.angle
        
        # Normalize angle to be within [-pi, pi]
        rel_angle = (rel_angle + math.pi) % (2 * math.pi) - math.pi
        
        # Map [-pi, pi] -> [-1, 1]
        mapped_angle = rel_angle / math.pi
        
        return InputState(distance=mapped_dist, relative_angle=mapped_angle)
