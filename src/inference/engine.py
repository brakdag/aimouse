"""
Inference Engine Core.
Orchestrates the loading, processing, inference, and actuation loop.
"""
import numpy as np
from pynput.mouse import Controller
from src.common.types import Point, Rect, ActionOutput
from src.inference.loader import ModelLoader
from src.inference.processor import StateProcessor
from src.inference.actuator import MouseActuator

class InferenceEngine:
    def __init__(self, model_weights_path: str, canvas_width: int, canvas_height: int, sensitivity: float = 10.0):
        self.loader = ModelLoader()
        self.weights, self.metadata = self.loader.load(model_weights_path)
        
        self.processor = StateProcessor(canvas_width, canvas_height)
        self.actuator = MouseActuator(sensitivity=sensitivity)
        self.mouse_controller = Controller()
        
        # Architecture matching the optimizer: 4 -> 10 -> 10 -> 5
        self.input_size = 4
        self.hidden_size = 10
        self.output_size = 5

    def _forward_pass(self, input_vec: np.ndarray) -> ActionOutput:
        idx = 0
        
        # Layer 1: Input -> Hidden 1
        w1_end = idx + (self.input_size * self.hidden_size)
        w1 = self.weights[idx:w1_end].reshape((self.input_size, self.hidden_size))
        idx = w1_end
        b1_end = idx + self.hidden_size
        b1 = self.weights[idx:b1_end]
        idx = b1_end
        
        # Layer 2: Hidden 1 -> Hidden 2
        w2_end = idx + (self.hidden_size * self.hidden_size)
        w2 = self.weights[idx:w2_end].reshape((self.hidden_size, self.hidden_size))
        idx = w2_end
        b2_end = idx + self.hidden_size
        b2 = self.weights[idx:b2_end]
        idx = b2_end
        
        # Layer 3: Hidden 2 -> Output
        w3_end = idx + (self.hidden_size * self.output_size)
        w3 = self.weights[idx:w3_end].reshape((self.hidden_size, self.output_size))
        idx = w3_end
        b3_end = idx + self.output_size
        b3 = self.weights[idx:b3_end]

        # Computation with Tanh for hidden layers
        h1 = np.tanh(np.dot(input_vec, w1) + b1)
        h2 = np.tanh(np.dot(h1, w2) + b2)
        
        # Computation with Sigmoid for output layer
        out = 1.0 / (1.0 + np.exp(-np.dot(h2, w3) + b3))
        
        return ActionOutput(
            dx_plus=float(out[0]),
            dy_plus=float(out[1]),
            dx_minus=float(out[2]),
            dy_minus=float(out[3]),
            arrived=float(out[4])
        )

    def run_task(self, target_rect: Rect, max_steps: int = 500) -> bool:
        print(f"Starting task: Target {target_rect}")
        
        for step in range(max_steps):
            curr_pos = Point(self.mouse_controller.position[0], self.mouse_controller.position[1])
            input_state = self.processor.process(target_rect, curr_pos)
            action = self._forward_pass(input_state.to_array())
            self.actuator.execute(action)
            
            if action.arrived > 0.8:
                print(f"Target reached at step {step} (Model signal).")
                return True
            
        print("Task timed out.")
        return False
