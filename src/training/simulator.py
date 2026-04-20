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
        self.rotation_speed = math.pi / 2

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
        rotation_delta = (action.rotate - 0.5) * 2.0 * self.rotation_speed
        new_angle = state.angle + rotation_delta

        # 2. Update Position (Movement)
        move_magnitude = (action.move - 0.5) * 2.0 * self.pixel_scale
        
        new_pos_x = np.clip(state.position.x + math.cos(new_angle) * move_magnitude, 0, self.width)
        new_pos_y = np.clip(state.position.y + math.sin(new_angle) * move_magnitude, 0, self.height)
        
        new_state = AgentState(
            position=Point(new_pos_x, new_pos_y),
            velocity=Point(math.cos(new_angle) * move_magnitude, math.sin(new_angle) * move_magnitude),
            angle=new_angle
        )

        # 3. Handle Arrival Signal (The 'One Bullet' Logic)
        target_center = self.target_rect.center
        dist = np.sqrt((new_state.position.x - target_center.x)**2 + 
                       (new_state.position.y - target_center.y)**2)

        # Only allow firing if the agent hasn't fired yet
        if action.arrived > 0.5 and not state.has_fired:
            # Mark as fired in the new state
            new_state = AgentState(
                position=new_state.position,
                velocity=new_state.velocity,
                angle=new_state.angle,
                has_fired=True
            )

            if dist < COMPLETION_DISTANCE_THRESHOLD:
                # HIT: The dart is nailed. Freeze and finish.
                frozen_state = AgentState(
                    position=new_state.position,
                    velocity=Point(0, 0),
                    angle=new_state.angle,
                    has_fired=True,
                    won=True
                )
                # MASSIVE REWARD: Make the 'Brave' agents dominate
                precision_bonus = 50.0 + (100.0 * (1.0 - (dist / COMPLETION_DISTANCE_THRESHOLD)))
                return frozen_state, precision_bonus, True 
            else:
                # MISS: Heavy flat penalty to discourage guessing
                return new_state, -30.0, False

        # Normal reward based on proximity if not firing or already fired
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
        # The only way to finish successfully is by signaling 'arrived'
        # We return False here to prevent auto-completion
        return False
