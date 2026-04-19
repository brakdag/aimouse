"""
Pygame-based GUI for the Training Ecosystem.
Minimalist version: Only the arena.
"""
import pygame
import sys
from src.training.app import TrainingApp
from src.training.visualizer import TrainingVisualizer

# --- Constants ---
WIDTH, HEIGHT = 640, 480
ARENA_WIDTH, ARENA_HEIGHT = 640, 480

COLOR_BG = (0, 0, 0)

class TrainingGUI:
    def __init__(self, app: TrainingApp):
        self.app = app
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neural Mouse Arena")
        self.clock = pygame.time.Clock()
        self.visualizer = TrainingVisualizer(ARENA_WIDTH, ARENA_HEIGHT)
        self.last_state = None

    def run(self):
        """Main GUI loop."""
        running = True
        while running:
            # Check if CLI requested shutdown
            if self.app.shutdown_requested:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_event(event)

            # Detect state changes to print config to console
            if self.app.state != self.last_state:
                if self.app.state == "MENU":
                    print("\n--- ENVIRONMENT CONFIG ---")
                    for k, v in self.app.config.items():
                        print(f"{k.capitalize()}: {v}")
                    print("--------------------------\n")
                self.last_state = self.app.state

            if self.app.state == "MENU":
                self._render_menu()
            elif self.app.state == "TRAINING":
                self._render_training_ui()
            elif self.app.state == "PAUSED":
                self._render_paused()

            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

    def _handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.app.state == "MENU":
                self.app.start_training()
            elif self.app.state == "TRAINING":
                self.app.pause_training()
            elif self.app.state == "PAUSED":
                self.app.resume_training()

    def _render_menu(self):
        self.screen.fill(COLOR_BG)

    def _render_training_ui(self):
        self.screen.fill(COLOR_BG)
        if self.app.optimizer and self.app.env and self.app.env.target_rect:
            self.visualizer.render(self.app.env.target_rect, self.app.optimizer.get_shared_data(), self.app.current_gen, self.app.best_fitness)
        self.screen.blit(self.visualizer.surface, (0, 0))

    def _render_paused(self):
        self.screen.fill(COLOR_BG)
        if self.app.optimizer and self.app.env and self.app.env.target_rect:
            self.visualizer.render(self.app.env.target_rect, self.app.optimizer.get_shared_data(), self.app.current_gen, self.app.best_fitness)
        self.screen.blit(self.visualizer.surface, (0, 0))
