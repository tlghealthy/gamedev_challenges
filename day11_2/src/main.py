#!/usr/bin/env python3
import sys
import json
import pygame
import pygame_gui
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from game.game_state import GameState
from game.renderer import Renderer
from ui.menu import MenuSystem
from utils.constants import load_settings

def main():
    # Load settings
    settings = load_settings()
    
    # Initialize pygame
    pygame.init()
    pygame.display.set_caption(settings['display']['title'])
    
    # Create display
    screen = pygame.display.set_mode((
        settings['display']['width'], 
        settings['display']['height']
    ))
    
    # Initialize GUI manager
    gui_manager = pygame_gui.UIManager((
        settings['display']['width'], 
        settings['display']['height']
    ))
    
    # Initialize game systems
    game_state = GameState(settings)
    menu_system = MenuSystem(gui_manager, settings, game_state)
    renderer = Renderer(screen, settings)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        time_delta = clock.tick(settings['display']['fps']) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to systems
            gui_manager.process_events(event)
            game_state.handle_event(event)
            menu_system.handle_event(event)
        
        # Update systems
        gui_manager.update(time_delta)
        game_state.update(time_delta)
        menu_system.update(time_delta)
        
        # Render
        renderer.render(game_state, menu_system)
        gui_manager.draw_ui(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 