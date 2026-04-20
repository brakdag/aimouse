"""
Visualizer for the Training Ecosystem using Pygame.
Renders the training arena with agents and targets onto a surface.
"""
import pygame
from src.common.types import Rect, AgentState

class TrainingVisualizer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))

    def render(self, target_rect: Rect, agents: list[tuple[AgentState, float, float]], generation: int, best_fitness: float):
        """
        Renders the current state of the arena onto its internal surface.
        
        Args:
            target_rect: The target rectangle.
            agents: List of (state, alpha, arrived_signal).
            generation: Current generation.
            best_fitness: Best fitness of the population.
        """
        # 1. Clear Surface (Black Background)
        self.surface.fill((0, 0, 0))

        # 2. Draw Target (White Rectangle)
        target_surface = pygame.Surface((target_rect.width, target_rect.height))
        target_surface.fill((255, 255, 255))
        self.surface.blit(target_surface, (target_rect.x, target_rect.y))

        # 3. Draw Agents
        for state, alpha, arrived in agents:
            agent_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            
            # Color logic:
            if state.won:
                color = (0, 0, 255, int(alpha * 255)) # Blue: Winner!
            elif state.has_fired:
                color = (100, 100, 100, int(alpha * 255)) # Grey: Out of ammo
            elif arrived > 0.5:
                color = (0, 255, 0, int(alpha * 255)) # Green: Firing!
            else:
                color = (255, 0, 0, int(alpha * 255))   # Red: Searching
                
            pygame.draw.circle(agent_surf, color, (5, 5), 5)
            self.surface.blit(agent_surf, (state.position.x - 5, state.position.y - 5))
