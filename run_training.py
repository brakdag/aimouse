"""
Main entry point for the Training Ecosystem.
Implements a multi-threaded GUI for real-time evolutionary training.
"""
import pygame
import threading
import time
import numpy as np
from src.common.types import Rect, Point
from src.training.simulator import MouseEnvironment
from src.training.evaluator import FitnessEvaluator
from src.training.optimizer import EvolutionaryOptimizer
from src.training.visualizer import TrainingVisualizer
from src.inference.processor import StateProcessor

# --- Constants & Colors ---
WIDTH, HEIGHT = 1280, 720
ARENA_WIDTH, ARENA_HEIGHT = 800, 600
SIDEBAR_WIDTH = 480

COLOR_BG = (10, 10, 10)
COLOR_MENU = (30, 30, 30)
COLOR_TEXT = (220, 220, 220)
COLOR_ACCENT = (0, 150, 255)
COLOR_BTN = (50, 50, 50)
COLOR_BTN_HOVER = (70, 70, 70)

class TrainingApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neural Mouse Training Arena")
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_bold = pygame.font.SysFont("Arial", 24, bold=True)

        # --- Configuration State ---
        self.config = {
            "cycles": 50,
            "spawning": 10,
            "population": 50,
            "elitism": 0.2,
            "generations": 100,
            "threshold": 5.0,
            "max_steps": 50
        }
        
        # --- Simulation State ---
        self.state = "MENU"  # MENU, TRAINING, PAUSED
        self.current_gen = 0
        self.best_fitness = 0.0
        self.optimizer = None
        self.env = None
        self.evaluator = None
        self.processor = None
        self.visualizer = TrainingVisualizer(ARENA_WIDTH, ARENA_HEIGHT)
        
        # --- Threading Control ---
        self.training_thread = None

    def _evolution_thread_target(self):
        """The background thread that runs the actual evolution loop."""
        try:
            # We use a dummy processor for the optimizer's internal logic
            # In a real setup, this would be the real StateProcessor
            processor = self.processor
            
            # The evolve method is blocking, so it runs here
            best_ind = self.optimizer.evolve(processor)
            
            # Once finished, we update the UI
            self.best_fitness = best_ind.fitness
            self.state = "MENU"
            print("Evolution completed successfully.")
        except Exception as e:
            print(f"Error in training thread: {e}")
            self.state = "MENU"

    def _start_training(self):
        self.env = MouseEnvironment(width=ARENA_WIDTH, height=ARENA_HEIGHT)
        self.evaluator = FitnessEvaluator(max_steps=self.config["max_steps"])
        self.processor = StateProcessor(ARENA_WIDTH, ARENA_HEIGHT)
        
        genome_size = (4 * 16) + 16 + (16 * 5) + 5
        
        self.optimizer = EvolutionaryOptimizer(
            input_size=4, hidden_size=16, output_size=5,
            env=self.env, evaluator=self.evaluator,
            pop_size=self.config["population"],
            spawning=self.config["spawning"],
            mutation_rate=0.1,
            mutation_strength=0.2
        )
        
        self.current_gen = 0
        self.best_fitness = 0.0
        self.state = "TRAINING"
        
        # Launch the background thread
        self.training_thread = threading.Thread(target=self._evolution_thread_target, daemon=True)
        self.training_thread.start()

    def _stop_training(self):
        if self.optimizer:
            self.optimizer.stop_event.set()
            self.optimizer.pause_event.set() # Unpause to allow exit
        self.state = "MENU"

    def _pause_training(self):
        if self.optimizer:
            self.optimizer.pause_event.clear()
            self.state = "PAUSED"

    def _resume_training(self):
        if self.optimizer:
            self.optimizer.pause_event.set()
            self.state = "TRAINING"

    def _handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.state == "MENU":
                # Start Button
                if 440 < pos[1] < 475: self._start_training()
            elif self.state == "TRAINING":
                # Pause Button
                if 440 < pos[1] < 475: self._pause_training()
                # Reset Button
                if 480 < pos[1] < 515: self._start_training()
                # Stop Button
                if 520 < pos[1] < 555: self._stop_training()
            elif self.state == "PAUSED":
                # Resume Button
                if 440 < pos[1] < 475: self._resume_training()
                # Reset Button
                if 480 < pos[1] < 515: self._start_training()
                # Stop Button
                if 520 < pos[1] < 555: self._stop_training()

    def _render_menu(self):
        # Sidebar
        pygame.draw.rect(self.screen, COLOR_MENU, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        
        title = self.font_bold.render("ENVIRONMENT", True, COLOR_ACCENT)
        self.screen.blit(title, (20, 20))
        
        y_offset = 60
        for key, val in self.config.items():
            txt = self.font_small.render(f"{key.capitalize()}: {val}", True, COLOR_TEXT)
            self.screen.blit(txt, (20, y_offset))
            y_offset += 30

        # Controls
        ctrl_title = self.font_bold.render("CONTROLS", True, COLOR_ACCENT)
        self.screen.blit(ctrl_title, (20, 400))
        
        buttons = [("START", 440), ("STOP", 520)]
        for label, y in buttons:
            pygame.draw.rect(self.screen, COLOR_BTN, (20, y, 150, 35))
            txt = self.font_small.render(label, True, COLOR_TEXT)
            self.screen.blit(txt, (35, y + 8))

        # Arena Preview
        pygame.draw.rect(self.screen, (20, 20, 20), (SIDEBAR_WIDTH + 20, 20, ARENA_WIDTH, ARENA_HEIGHT))

    def _render_training_ui(self):
        # Sidebar
        pygame.draw.rect(self.screen, COLOR_MENU, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        
        # Nerd Stats
        stats_title = self.font_bold.render("NERD STATS", True, COLOR_ACCENT)
        self.screen.blit(stats_title, (20, 20))
        
        y_offset = 60
        stats = [
            (f"Gen: {self.current_gen}", ""),
            (f"Best Fit: {self.best_fitness:.4f}", ""),
            (f"Pop: {self.config['population']}", ""),
            (f"Spawning: {self.config['spawning']}", ""),
            (f"Elitism: {self.config['elitism']*100}%", ""),
            (f"Threshold: {self.config['threshold']}px", "")
        ]
        
        for label, val in stats:
            txt = self.font_small.render(label, True, COLOR_TEXT)
            self.screen.blit(txt, (20, y_offset))
            y_offset += 30

        # Controls
        ctrl_title = self.font_bold.render("CONTROLS", True, COLOR_ACCENT)
        self.screen.blit(ctrl_title, (20, 400))
        
        buttons = [("PAUSE", 440), ("RESET", 480), ("STOP", 520)]
        for label, y in buttons:
            pygame.draw.rect(self.screen, COLOR_BTN, (20, y, 150, 35))
            txt = self.font_small.render(label, True, COLOR_TEXT)
            self.screen.blit(txt, (35, y + 8))

        # Arena
        self.visualizer.render(self.env.target_rect, self.optimizer.get_shared_data(), self.current_gen, self.best_fitness)
        self.screen.blit(self.visualizer.screen, (SIDEBAR_WIDTH + 20, 20))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._stop_training()
                    running = False
                self._handle_event(event)

            if self.state == "MENU":
                self._render_menu()
            elif self.state == "TRAINING":
                self._render_training_ui()
                # In a real implementation, we'd update current_gen from the optimizer
                # For this skeleton, we'll just increment it to simulate progress
                # self.current_gen = self.optimizer.current_generation
            elif self.state == "PAUSED":
                self._render_training_ui()
                # Overlay Pause text
                overlay = self.font_bold.render("PAUSED", True, (255, 255, 0))
                self.screen.blit(overlay, (WIDTH//2 - 40, HEIGHT//2))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    app = TrainingApp()
    app.run()
