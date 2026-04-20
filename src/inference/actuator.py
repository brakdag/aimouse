"""
Actuator for the Inference Engine.
Translates discrete directional signals into physical mouse movements.
"""
from pynput.mouse import Controller, Button
from src.common.types import ActionOutput

class MouseActuator:
    def __init__(self, sensitivity: float = 10.0):
        """
        Args:
            sensitivity: Multiplier to convert normalized deltas to pixels.
        """
        self.mouse = Controller()
        self.sensitivity = sensitivity

    def execute(self, action: ActionOutput):
        """
        Translates ActionOutput into physical mouse movement.
        """
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

        if move_x != 0 or move_y != 0:
            self.mouse.move(move_x * self.sensitivity, move_y * self.sensitivity)

    def click(self):
        """
        Performs a physical left-click.
        """
        self.mouse.click(Button.left, 1)
        pass
