"""
Complete demo showcasing the game state manager features.
"""

import pygame
import sys
from game_state_manager import GameStateManager
from .menu_state import MenuState


def main():
    """Run the game state manager demo."""
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game State Manager Demo")
    clock = pygame.time.Clock()
    
    # Initialize state manager
    manager = GameStateManager()
    manager.push_state(MenuState())
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update and render
        dt = clock.tick(60) / 1000.0
        manager.update(dt)
        manager.render(screen)
        
        # Update display
        pygame.display.flip()
    
    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main() 