"""
Main entry point for the Training Ecosystem.
Supports both GUI mode and Headless mode for command-line execution.
"""
import pygame
import sys
import threading
import numpy as np
from src.common.types import Rect
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

class TrainingApp:
    def __init__(self, headless=False):
        self.headless = headless
        self.config = {
            "cycles": 50,
            "spawning": 10,
            "population": 50,
            "elitism": 0.2,
            "generations": 2,
            "threshold": 5.0,
            "max_steps": 50
        }
        
        self.state = "MENU" 
        self.current_gen = 0
        self.best_fitness = 0.0
        self.optimizer = None
        self.env = None
        self.evaluator = None
        self.processor = None
        self.training_thread = None

        if not self.headless:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Neural Mouse Training Arena")
            self.clock = pygame.time.Clock()
            self.font_main = pygame.font.SysFont("Arial", 22)
            self.font_small = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 24, bold=True)
            self.visualizer = TrainingVisualizer(ARENA_WIDTH, ARENA_HEIGHT)

    def _evolution_thread_target(self):
        """Background thread for headless or GUI training."""
        try:
            # Setup components
            self.env = MouseEnvironment(width=ARENA_WIDTH, height=ARENA_HEIGHT)
            self.evaluator = FitnessEvaluator(max_steps=self.config["max_steps"])
            self.processor = StateProcessor(ARENA_WIDTH, ARENA_HEIGHT)
            
            genome_size = (4 * 10) + 10 + (10 * 10) + 10 + (10 * 5) + 5
            
            self.optimizer = EvolutionaryOptimizer(
                input_size=4, hidden_size=10, output_size=5,
                env=self.env, evaluator=self.evaluator,
                pop_size=self.config["population"],
                spawning=self.config["spawning"]
            )
            
            # Target for training (can be randomized in a real loop)
            target = Rect(370, 270, 60, 60)

            print("\n[TRAINING] Starting evolution loop...")
            
            for gen in range(self.config["generations"]):
                if self.optimizer.stop_event.is_set():
                    break
                
                # Wait if paused
                self.optimizer.pause_event.wait()
                
                # Run one generation
                best_ind = self.optimizer.evolve(self.processor)
                
                self.current_gen = gen + 1
                self.best_fitness = best_ind.fitness
                
                print(f"[GEN {self.current_gen}] Best Fitness: {self.best_fitness:.4f}")

            print("\n[TRAINING] Process completed.")
            if not self.headless:
                self.state = "MENU"

        except Exception as e:
            print(f"\n[ERROR] Training thread failed: {e}")
            self.state = "MENU"

    def run(self):
        if self.headless:
            self._run_headless()
        else:
            self._run_gui()

    def _run_headless(self):
        """Execution loop for console-only mode."""
        self._evolution_thread_target()

    def _run_gui(self):
        """Execution loop for Pygame-based GUI mode."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.optimizer:
                        self.optimizer.stop_event.set()
                    running = False
                self._handle_event(event)

            if self.state == "MENU":
                self._render_menu()
            elif self.state == "TRAINING":
                self._render_training_ui()
            elif self.state == "PAUSED":
                self._render_paused()

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def _handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.state == "MENU":
                if 440 < pos[1] < 475: self._start_training()
            elif self.state == "TRAINING":
                if 440 < pos[1] < 475: self.state = "PAUSED"
                elif 480 < pos[1] < 515: self._start_training()
                elif 520 < pos[1] < 555: self._stop_training()
            elif self.state == "PAUSED":
                if 440 < pos[1] < 475: self.state = "TRAINING"
                elif 480 < pos[1] < 515: self._start_training()
                elif 520 < pos[1] < 555: self._stop_training()

    def _start_training(self):
        self.state = "TRAINING"
        self.training_thread = threading.Thread(target=self._evolution_thread_target, daemon=True)
        self.training_thread.start()

    def _stop_training(self):
        if self.optimizer:
            self.optimizer.stop_event.set()
            self.optimizer.pause_event.set()
        self.state = "MENU"

    def _render_menu(self):
        self.screen.fill(COLOR_BG)
        pygame.draw.rect(self.screen, COLOR_MENU, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        title = self.font_bold.render("ENVIRONMENT", True, COLOR_ACCENT)
        self.screen.blit(title, (20, 20))
        y = 60
        for k, v in self.config.items():
            txt = self.font_small.render(f"{k.capitalize()}: {v}", True, COLOR_TEXT)
            self.screen.blit(txt, (20, y))
            y += 30
        pygame.draw.rect(self.screen, COLOR_BTN, (20, 440, 150, 35))
        self.screen.blit(self.font_small.render("START", True, COLOR_TEXT), (35, 448))

    def _render_training_ui(self):
        self.screen.fill(COLOR_BG)
        pygame.draw.rect(self.screen, COLOR_MENU, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        
        # Stats
        title = self.font_bold.render("NERD STATS", True, COLOR_ACCENT)
        self.screen.blit(title, (20, 20))
        y = 60
        stats = [f"Gen: {self.current_gen}", f"Best Fit: {self.best_fitness:.4f}", f"Pop: {self.config['population']}"]
        for s in stats:
            txt = self.font_small.render(s, True, COLOR_TEXT)
            self.screen.blit(txt, (20, y))
            y += 30

        # Controls
        pygame.draw.rect(self.screen, COLOR_BTN, (20, 440, 150, 35))
        self.screen.blit(self.font_small.render("PAUSE", True, COLOR_TEXT), (35, 448))
        pygame.draw.rect(self.screen, COLOR_BTN, (20, 480, 150, 35))
        self.screen.blit(self.font_small.render("RESET", True, COLOR_TEXT), (35, 488))
        pygame.draw.rect(self.screen, COLOR_BTN, (20, 520, 150, 35))
        self.screen.blit(self.font_small.render("STOP", True, COLOR_TEXT), (35, 528))

        # Arena
        if self.optimizer and self.env:
            self.visualizer.render(self.env.target_rect, self.optimizer.get_shared_data(), self.current_gen, self.best_fitness)
        self.screen.blit(self.visualizer.screen, (SIDEBAR_WIDTH + 20, 20))

    def _render_paused(self):
        self._render_training_ui()
        overlay = self.font_bold.render("PAUSED", True, (255, 255, 0))
        self.screen.blit(overlay, (WIDTH//2 - 40, HEIGHT//2))

if __name__ == "__main__":
    is_headless = "--headless" in sys.argv
    app = TrainingApp(headless=is_headless)
    app.run()
