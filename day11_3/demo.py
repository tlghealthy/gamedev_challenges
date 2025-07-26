#!/usr/bin/env python3
"""
Standalone demo for the Game State Manager.

Run this script to see the game state manager in action.
Features demonstrated:
- Menu state with navigation
- Game state with player movement
- Pause state with overlay
- State transitions with data passing
- Shared data management
"""

import pygame
import sys
import os

# Add the game_state_manager to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_state_manager import GameStateManager
from game_state_manager.examples import MenuState


def main():
    """Run the game state manager demo."""
    print("Starting Game State Manager Demo...")
    print("Controls:")
    print("  SPACE - Start game from menu")
    print("  WASD/Arrows - Move player in game")
    print("  P - Pause game")
    print("  ESC - Return to menu or quit")
    print()
    
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
    print("Demo finished.")
    sys.exit()


if __name__ == "__main__":
    main() 