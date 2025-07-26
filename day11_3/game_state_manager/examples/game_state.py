"""
Example game state demonstrating gameplay and state transitions.
"""

import pygame
from ..state import BaseState


class GameState(BaseState):
    """Simple game state with player movement and pause functionality."""
    
    def init(self):
        """Initialize game resources."""
        self.font = pygame.font.Font(None, 36)
        self.player_pos = [400, 300]
        self.player_speed = 200
        self.score = 0
        self.level = 1
        self.background_color = (30, 100, 30)
        self.player_color = (255, 255, 0)
    
    def enter(self, data):
        """Handle data passed from previous state."""
        self.score = data.get("score", 0)
        self.level = data.get("level", 1)
        print(f"Entering game state - Level: {self.level}, Score: {self.score}")
    
    def update(self, dt):
        """Update game logic."""
        keys = pygame.key.get_pressed()
        
        # Player movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_pos[0] -= self.player_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_pos[0] += self.player_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_pos[1] -= self.player_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_pos[1] += self.player_speed * dt
        
        # Keep player on screen
        self.player_pos[0] = max(20, min(780, self.player_pos[0]))
        self.player_pos[1] = max(20, min(580, self.player_pos[1]))
        
        # Score increases over time
        self.score += int(dt * 10)
        
        # Pause functionality
        if keys[pygame.K_p]:
            from .pause_state import PauseState
            self.manager.push_state(PauseState(), {"score": self.score, "level": self.level})
        
        # Return to menu
        if keys[pygame.K_ESCAPE]:
            from .menu_state import MenuState
            self.manager.switch_state(MenuState())
    
    def render(self, surface):
        """Render game elements."""
        surface.fill(self.background_color)
        
        # Draw player
        pygame.draw.circle(surface, self.player_color, 
                         (int(self.player_pos[0]), int(self.player_pos[1])), 15)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        controls_text = self.font.render("WASD/Arrows: Move | P: Pause | ESC: Menu", True, (200, 200, 200))
        
        surface.blit(score_text, (10, 10))
        surface.blit(level_text, (10, 50))
        surface.blit(controls_text, (10, 550))
    
    def exit(self):
        """Save data when exiting."""
        print(f"Exiting game state - Final Score: {self.score}") 