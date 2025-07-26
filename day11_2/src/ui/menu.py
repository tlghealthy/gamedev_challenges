import pygame
import pygame_gui
from typing import Dict
from utils.constants import PLAYING, MENU

class MenuSystem:
    def __init__(self, gui_manager: pygame_gui.UIManager, settings: Dict, game_state=None):
        self.gui_manager = gui_manager
        self.settings = settings
        self.game_state = game_state
        self.buttons = {}
        self.create_buttons()
        self.show_buttons(True)
    
    def set_game_state(self, game_state):
        self.game_state = game_state
    
    def create_buttons(self):
        button_size = self.settings['ui']['button_size']
        # Start game button
        self.buttons['start'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.settings['display']['width']//2 - button_size[0]//2,
                380,
                button_size[0], button_size[1]
            ),
            text='Start Game',
            manager=self.gui_manager
        )
        # Settings button
        self.buttons['settings'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.settings['display']['width']//2 - button_size[0]//2,
                430,
                button_size[0], button_size[1]
            ),
            text='Settings',
            manager=self.gui_manager
        )
        # Quit button
        self.buttons['quit'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self.settings['display']['width']//2 - button_size[0]//2,
                480,
                button_size[0], button_size[1]
            ),
            text='Quit',
            manager=self.gui_manager
        )
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.buttons['start']:
                if self.game_state:
                    self.game_state.load_level(1)  # Load first level
                    self.show_buttons(False)
            elif event.ui_element == self.buttons['settings']:
                pass
            elif event.ui_element == self.buttons['quit']:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def update(self, dt: float):
        # Show/hide buttons based on game state
        if self.game_state:
            if self.game_state.state == MENU:
                self.show_buttons(True)
            else:
                self.show_buttons(False)
    
    def show_buttons(self, show: bool):
        for button in self.buttons.values():
            button.show() if show else button.hide() 