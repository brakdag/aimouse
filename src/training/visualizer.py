"""
Visualizer for the Training Ecosystem using Pygame.
Renders the training arena with agents and targets.
"""
import pygame
import numpy as np
from src.common.types import Rect, AgentState

class TrainingVisualizer:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Neural Mouse Training Arena")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

    def render(self, target_rect: Rect, agents: list[tuple[AgentState, float]], generation: int, best_fitness: float):
        """
        Renders the current state of the arena.
        
        Args:
            target_rect: The target rectangle.
            agents: A list of tuples (AgentState, alpha) where alpha is transparency.
            generation: Current generation number.
            best_fitness: Best fitness in current generation.
        """
        # 1. Clear Screen (Black Background)
        self.screen.fill((0, 0, 0))

        # 2. Draw Target (White Rectangle)
        target_surface = pygame.Surface((target_rect.width, target_rect.height))
        target_surface.fill((255, 255, 255))
        self.screen.blit(target_surface, (target_rect.x, target_rect.y))

        # 3. Draw Agents (Red Translucent Circles/Rects)
        # We use a separate surface for transparency
        for state, alpha in agents:
            agent_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            # Red color with alpha (0-255)
            color = (255, 0, 0, int(alpha * 255))
            pygame.draw.circle(agent_surf, color, (5, 5), 5)
            self.screen.blit(agent_surf, (state.position.x - 5, state.position.y - 5))

        # 4. Draw UI Text
        gen_text = self.font.render(f"Generation: {generation}", True, (255, 255, 255))
        fit_text = self.font.render(f"Best Fitness: {best_fitness:.4f}", True, (255, 255, 255))
        self.screen.blit(gen_text, (10, 10))
        self.screen.blit(fit_text, (10, 30))

        pygame.display.flip()

    def tick(self, fps: int = 15):
        self.clock.tick(fps)

    def handle_events(self) -> bool:
        """Returns False if the user wants to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def close(self):
        pygame.quit()
