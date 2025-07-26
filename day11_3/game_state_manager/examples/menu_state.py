"""
Example menu state demonstrating basic state functionality.
"""

import pygame
from ..state import BaseState


class MenuState(BaseState):
    """Simple menu state with button interaction."""
    
    def init(self):
        """Initialize menu resources."""
        self.font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        self.title = self.font.render("Game State Manager Demo", True, (255, 255, 255))
        self.start_text = self.button_font.render("Press SPACE to Start Game", True, (200, 200, 200))
        self.quit_text = self.button_font.render("Press ESC to Quit", True, (200, 200, 200))
        self.background_color = (50, 50, 100)
    
    def update(self, dt):
        """Handle input and state transitions."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            from .game_state import GameState
            self.manager.switch_state(GameState(), {"level": 1, "score": 0})
        elif keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
    
    def render(self, surface):
        """Render menu elements."""
        surface.fill(self.background_color)
        
        # Center the title
        title_rect = self.title.get_rect(center=(surface.get_width() // 2, 200))
        surface.blit(self.title, title_rect)
        
        # Center the buttons
        start_rect = self.start_text.get_rect(center=(surface.get_width() // 2, 350))
        surface.blit(self.start_text, start_rect)
        
        quit_rect = self.quit_text.get_rect(center=(surface.get_width() // 2, 400))
        surface.blit(self.quit_text, quit_rect) 