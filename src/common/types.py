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
    The 2-feature input vector for the model:
    [normalized_distance, relative_angle]
    Both values mapped to [-1, 1].
    """
    distance: float
    relative_angle: float

    def to_array(self) -> np.ndarray:
        return np.array([self.distance, self.relative_angle], dtype=np.float32)

@dataclass(frozen=True)
class ActionOutput:
    """
    The 3-feature output vector from the model:
    [move, rotate, arrived]
    Values in range [0, 1].
    """
    move: float
    rotate: float
    arrived: float

    def to_array(self) -> np.ndarray:
        return np.array([self.move, self.rotate, self.arrived], dtype=np.float32)

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
    angle: float
    has_fired: bool = False
    won: bool = False
