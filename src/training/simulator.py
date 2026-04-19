"""
Environment Simulator for the Neural Mouse Interface.
Supports randomized starting positions and targets.
"""
import numpy as np
import random
import math
from src.common.types import Point, Rect, ActionOutput, AgentState
from src.common.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT, COMPLETION_DISTANCE_THRESHOLD

class MouseEnvironment:
    def __init__(self, width: int = DEFAULT_CANVAS_WIDTH, height: int = DEFAULT_CANVAS_HEIGHT):
        self.width = width
        self.height = height
        self.target_rect = None
        self.pixel_scale = 15.0
        self.rotation_speed = math.pi / 2  # 90 degrees per step for maximum freedom

    def reset_target(self) -> Rect:
        t_w, t_h = 20, 20
        t_x = random.randint(0, self.width - t_w)
        t_y = random.randint(0, self.height - t_h)
        self.target_rect = Rect(t_x, t_y, t_w, t_h)
        return self.target_rect

    def reset_agent(self) -> AgentState:
        start_x = random.uniform(0, self.width)
        start_y = random.uniform(0, self.height)
        start_angle = random.uniform(0, 2 * math.pi)
        return AgentState(position=Point(start_x, start_y), velocity=Point(0, 0), angle=start_angle)

    def step(self, state: AgentState, action: ActionOutput) -> tuple[AgentState, float, bool]:
        # 1. Update Angle (Rotation)
        # rotate: 0.0 (CCW) to 1.0 (CW). Center is 0.5
        rotation_delta = (action.rotate - 0.5) * 2.0 * self.rotation_speed
        new_angle = state.angle + rotation_delta

        # 2. Update Position (Movement)
        # move: 0.0 (Backward) to 1.0 (Forward). Center is 0.5
        move_magnitude = (action.move - 0.5) * 2.0 * self.pixel_scale
        
        new_pos_x = np.clip(state.position.x + math.cos(new_angle) * move_magnitude, 0, self.width)
        new_pos_y = np.clip(state.position.y + math.sin(new_angle) * move_magnitude, 0, self.height)
        
        new_state = AgentState(
            position=Point(new_pos_x, new_pos_y),
            velocity=Point(math.cos(new_angle) * move_magnitude, math.sin(new_angle) * move_magnitude),
            angle=new_angle
        )

        reward = self._calculate_reward(new_state)
        done = self._check_done(new_state)
        
        return new_state, reward, done

    def _calculate_reward(self, state: AgentState) -> float:
        if self.target_rect is None:
            return 0.0
        target_center = self.target_rect.center
        dist = np.sqrt((state.position.x - target_center.x)**2 + 
                       (state.position.y - target_center.y)**2)
        return 1.0 / (dist + 1.0)

    def _check_done(self, state: AgentState) -> bool:
        if self.target_rect is None:
            return True
        target_center = self.target_rect.center
        dist = np.sqrt((state.position.x - target_center.x)**2 + 
                       (state.position.y - target_center.y)**2)
        return dist < COMPLETION_DISTANCE_THRESHOLD
