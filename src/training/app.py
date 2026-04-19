"""
Core logic and state management for the Training Ecosystem.
"""
import threading
import numpy as np
import json
import os
from src.common.types import Rect
from src.training.simulator import MouseEnvironment
from src.training.evaluator import FitnessEvaluator
from src.training.optimizer import EvolutionaryOptimizer
from src.inference.processor import StateProcessor

class TrainingApp:
    def __init__(self, arena_width=800, arena_height=600, config=None):
        self.arena_width = arena_width
        self.arena_height = arena_height
        self.config = config or {
            "cycles": 50,
            "spawning": 10,
            "population": 50,
            "elitism": 0.2,
            "generations": 1,
            "threshold": 5.0,
            "max_steps": 50,
            "fps": 0,
            "mutation_rate": 0.1,
            "mutation_strength": 0.2
        }
        
        self.state = "MENU" 
        self.current_gen = 0
        self.best_fitness = 0.0
        self.optimizer = None
        self.env = None
        self.evaluator = None
        self.processor = None
        self.training_thread = None
        self.shutdown_requested = False

        # Ensure models directory exists
        self.models_dir = "models"
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

    def _evolution_thread_target(self, update_callback=None):
        """Background thread for training."""
        try:
            # Setup components
            self.env = MouseEnvironment(width=self.arena_width, height=self.arena_height)
            self.evaluator = FitnessEvaluator(max_steps=self.config["max_steps"])
            self.processor = StateProcessor(self.arena_width, self.arena_height)
            
            self.optimizer = EvolutionaryOptimizer(
                input_size=2, hidden_layers=[5, 5], output_size=3,
                env=self.env, evaluator=self.evaluator,
                pop_size=self.config["population"],
                spawning=self.config["spawning"],
                fps=self.config["fps"],
                elitism=self.config["elitism"],
                mutation_rate=self.config["mutation_rate"],
                mutation_strength=self.config["mutation_strength"]
            )
            
            # Target for training
            target = Rect(370, 270, 60, 60)

            print("\n[TRAINING] Starting evolution loop...")
            
            def internal_update(gen, fitness):
                self.current_gen = gen
                self.best_fitness = fitness
                if update_callback:
                    update_callback(gen, fitness)
                print(f"[GEN {gen}] Best Fitness: {fitness:.4f}")

            # Run evolution
            self.optimizer.evolve(self.processor, self.config["generations"], internal_update)
            
            print("\n[TRAINING] Process completed.")
            self.state = "MENU"

        except Exception as e:
            print(f"\n[ERROR] Training thread failed: {e}")
            self.state = "MENU"

    def start_training(self):
        if self.state == "TRAINING":
            print("[SYSTEM] Evolution is already running.")
            return
        self.state = "TRAINING"
        self.training_thread = threading.Thread(target=self._evolution_thread_target, daemon=True)
        self.training_thread.start()

    def stop_training(self):
        if self.optimizer:
            self.optimizer.stop_event.set()
            self.optimizer.pause_event.set()
        self.state = "MENU"

    def pause_training(self):
        if self.state == "TRAINING" and self.optimizer:
            self.state = "PAUSED"
            self.optimizer.pause_event.clear()

    def resume_training(self):
        if self.state == "PAUSED" and self.optimizer:
            self.state = "TRAINING"
            self.optimizer.pause_event.set()

    def set_generations(self, value):
        self.config["generations"] = value

    def set_population(self, value):
        self.config["population"] = value

    def set_fps(self, value):
        self.config["fps"] = value
        if self.optimizer:
            self.optimizer.fps = value

    def set_elitism(self, value):
        self.config["elitism"] = value
        if self.optimizer:
            self.optimizer.elitism = value

    def set_spawning(self, value):
        self.config["spawning"] = value
        if self.optimizer:
            self.optimizer.spawning = value

    def set_cycles(self, value):
        self.config["cycles"] = value
        self.config["max_steps"] = value
        if self.env:
            self.env.max_steps = value
        if self.evaluator:
            self.evaluator.max_steps = value

    def set_mutation_rate(self, value):
        self.config["mutation_rate"] = value
        if self.optimizer:
            self.optimizer.mutation_rate = value

    def set_mutation_strength(self, value):
        self.config["mutation_strength"] = value
        if self.optimizer:
            self.optimizer.mutation_strength = value

    def save_model(self, name):
        if not self.optimizer:
            return False, "No active optimizer to save from."
        
        weights = self.optimizer.get_best_weights()
        if weights is None:
            return False, "No weights available to save."
        
        filename = f"{name}.json" if not name.endswith(".json") else name
        path = os.path.join(self.models_dir, filename)
        
        try:
            with open(path, 'w') as f:
                json.dump({"weights": weights.tolist()}, f)
            return True, path
        except Exception as e:
            return False, str(e)

    def load_model(self, identifier):
        if not self.optimizer:
            return False, "No active optimizer to load into."
        
        # Get list of available models
        models = [f for f in os.listdir(self.models_dir) if f.endswith(".json")]
        
        target_file = None
        if identifier.isdigit():
            idx = int(identifier) - 1
            if 0 <= idx < len(models):
                target_file = models[idx]
            else:
                target_file = None
        else:
            filename = f"{identifier}.json" if not identifier.endswith(".json") else identifier
            if filename in models:
                target_file = filename
        
        if not target_file:
            return False, "Model not found."
        
        try:
            path = os.path.join(self.models_dir, target_file)
            with open(path, 'r') as f:
                data = json.load(f)
                weights = np.array(data["weights"])
                self.optimizer.inject_elite_weights(weights)
            return True, target_file
        except Exception as e:
            return False, str(e)

    def list_models(self):
        return [f for f in os.listdir(self.models_dir) if f.endswith(".json")]
