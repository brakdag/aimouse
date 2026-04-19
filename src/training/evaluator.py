"""
Evaluator for the Training Ecosystem.
Implements a hierarchical fitness function: Arrival > Speed > Proximity.
"""
import numpy as np
from src.common.types import AgentState, FitnessScore, Rect

class FitnessEvaluator:
    def __init__(self, max_steps: int):
        self.max_steps = max_steps

    def evaluate(self, trajectory: list[AgentState], target_rect: Rect, steps_taken: int) -> FitnessScore:
        if not trajectory:
            return FitnessScore(0, 0, 0, 0)

        target_center = target_rect.center
        
        # 1. Calculate Minimum Distance achieved
        min_dist = float('inf')
        for state in trajectory:
            dist = np.sqrt((state.position.x - target_center.x)**2 + 
                           (state.position.y - target_center.y)**2)
            if dist < min_dist:
                min_dist = dist

        # 2. Determine Arrival (Accuracy)
        # We use a threshold to define arrival. If min_dist is very small, accuracy is 1.0
        # If not, accuracy scales down.
        arrival_threshold = 5.0 
        if min_dist <= arrival_threshold:
            accuracy = 1.0
        else:
            # Scale accuracy based on distance, but keep it below 1.0
            accuracy = max(0.0, 1.0 - (min_dist / 500.0))

        # 3. Calculate Speed (Only relevant if arrived)
        # If arrived, speed is high for low steps. If not arrived, speed is 0.
        speed = 0.0
        if accuracy >= 1.0:
            speed = 1.0 - (steps_taken / self.max_steps)

        # 4. Smoothness & Anti-Detection (Placeholders for now)
        smoothness = 1.0
        anti_detection = 1.0

        return FitnessScore(
            accuracy=accuracy,
            speed=speed,
            smoothness=smoothness,
            anti_detection=anti_detection
        )
