"""
Environment Simulator for the Neural Mouse Interface.
Supports randomized starting positions and targets.
"""
import numpy as np
import random
from src.common.types import Point, Rect, ActionOutput, AgentState
from src.common.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT, COMPLETION_DISTANCE_THRESHOLD

class MouseEnvironment:
    def __init__(self, width: int = DEFAULT_CANVAS_WIDTH, height: int = DEFAULT_CANVAS_HEIGHT):
        self.width = width
        self.height = height
        self.agent_state = AgentState(position=Point(width/2, height/2), velocity=Point(0, 0))
        self.target_rect = None
        self.steps_taken = 0
        self.max_steps = 50  # Fixed to 50 cycles as requested
        self.pixel_scale = 15.0

    def reset(self) -> tuple[AgentState, Rect]:
        """Resets the environment with a random start position and a random target.
        
        Returns:
            A tuple of (initial_agent_state, target_rect).
        """
        # 1. Randomize Target
        t_w, t_h = 20, 20
        t_x = random.randint(0, self.width - t_w)
        t_y = random.randint(0, self.height - t_h)
        self.target_rect = Rect(t_x, t_y, t_w, t_h)

        # 2. Randomize Agent Start Position
        start_x = random.uniform(0, self.width)
        start_y = random.uniform(0, self.height)
        
        self.agent_state = AgentState(position=Point(start_x, start_y), velocity=Point(0, 0))
        self.steps_taken = 0
        return self.agent_state, self.target_rect

    def step(self, action: ActionOutput) -> tuple[AgentState, float, bool]:
        self.steps_taken += 1
        
        move_x = 0.0
        move_y = 0.0

        if action.dx_plus > action.dx_minus:
            move_x = action.dx_plus
        else:
            move_x = -action.dx_minus
            
        if action.dy_plus > action.dy_minus:
            move_y = action.dy_plus
        else:
            move_y = -action.dy_minus

        new_pos_x = np.clip(self.agent_state.position.x + (move_x * self.pixel_scale), 0, self.width)
        new_pos_y = np.clip(self.agent_state.position.y + (move_y * self.pixel_scale), 0, self.height)
        
        self.agent_state = AgentState(
            position=Point(new_pos_x, new_pos_y),
            velocity=Point(move_x, move_y)
        )

        reward = self._calculate_reward()
        done = self._check_done()
        
        return self.agent_state, reward, done

    def _calculate_reward(self) -> float:
        if self.target_rect is None:
            return 0.0
        target_center = self.target_rect.center
        dist = np.sqrt((self.agent_state.position.x - target_center.x)**2 + 
                       (self.agent_state.position.y - target_center.y)**2)
        return 1.0 / (dist + 1.0)

    def _check_done(self) -> bool:
        if self.steps_taken >= self.max_steps:
            return True
        if self.target_rect is None:
            return True
        target_center = self.target_rect.center
        dist = np.sqrt((self.agent_state.position.x - target_center.x)**2 + 
                       (self.agent_state.position.y - target_center.y)**2)
        return dist < COMPLETION_DISTANCE_THRESHOLD
