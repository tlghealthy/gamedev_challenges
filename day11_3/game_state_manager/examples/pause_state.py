"""
Example pause state demonstrating overlay functionality.
"""

import pygame
from ..state import BaseState


class PauseState(BaseState):
    """Pause overlay state that preserves game state."""
    
    def init(self):
        """Initialize pause resources."""
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        self.resume_text = self.small_font.render("Press P to Resume", True, (200, 200, 200))
        self.menu_text = self.small_font.render("Press ESC for Menu", True, (200, 200, 200))
        self.overlay_color = (0, 0, 0, 128)  # Semi-transparent black
    
    def enter(self, data):
        """Store game data for resuming."""
        self.game_data = data.copy()
        print(f"Paused - Score: {data.get('score', 0)}, Level: {data.get('level', 1)}")
    
    def update(self, dt):
        """Handle pause menu input."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            # Resume game with preserved data
            self.manager.pop_state(self.game_data)
        elif keys[pygame.K_ESCAPE]:
            # Return to main menu
            from .menu_state import MenuState
            self.manager.switch_state(MenuState())
    
    def render(self, surface):
        """Render pause overlay."""
        # Create semi-transparent overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        surface.blit(overlay, (0, 0))
        
        # Center the pause text
        pause_rect = self.pause_text.get_rect(center=(surface.get_width() // 2, 250))
        surface.blit(self.pause_text, pause_rect)
        
        # Center the options
        resume_rect = self.resume_text.get_rect(center=(surface.get_width() // 2, 320))
        surface.blit(self.resume_text, resume_rect)
        
        menu_rect = self.menu_text.get_rect(center=(surface.get_width() // 2, 360))
        surface.blit(self.menu_text, menu_rect) 