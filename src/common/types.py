"""
Type definitions for the Neural Mouse Interface.
All spatial values are normalized to the range [-1, 1], where (0,0) is the screen center.
"""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)

@dataclass(frozen=True)
class InputState:
    """
    The 4-feature input vector for the model:
    [target_x, target_y, current_x, current_y]
    All values in range [-1, 1].
    """
    target_x: float
    target_y: float
    current_x: float
    current_y: float

    def to_array(self) -> np.ndarray:
        return np.array([self.target_x, self.target_y, self.current_x, self.current_y], dtype=np.float32)

@dataclass(frozen=True)
class ActionOutput:
    """
    The 5-feature output vector from the model:
    [dx_plus, dy_plus, dx_minus, dy_minus, arrived]
    Values typically in range [0, 1].
    """
    dx_plus: float
    dy_plus: float
    dx_minus: float
    dy_minus: float
    arrived: float

    def to_array(self) -> np.ndarray:
        return np.array([self.dx_plus, self.dy_plus, self.dx_minus, self.dy_minus, self.arrived], dtype=np.float32)

@dataclass(frozen=True)
class FitnessScore:
    accuracy: float
    speed: float
    smoothness: float
    anti_detection: float

    @property
    def total(self) -> float:
        return (self.accuracy * 0.4) + (self.speed * 0.2) + (self.smoothness * 0.2) + (self.anti_detection * 0.2)

@dataclass(frozen=True)
class AgentState:
    """
    Represents the state of the agent at a specific point in time.
    """
    position: Point
    velocity: Point
