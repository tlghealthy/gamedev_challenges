# Game Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Theme System
class Theme:
    """Centralized theme system for easy color management"""
    
    # Dark Theme (Current)
    DARK = {
        'background': (0, 0, 0),
        'text_primary': (255, 255, 255),
        'text_secondary': (200, 200, 200),
        'text_muted': (128, 128, 128),
        'grid_lines': (40, 40, 40),
        'ui_background': (40, 40, 40),
        'ui_border': (200, 200, 200),
        'player_x': (255, 100, 100),
        'player_o': (100, 150, 255),
        'accent_yellow': (255, 255, 100),
        'accent_green': (100, 255, 100),
        'accent_orange': (255, 165, 0),
        'accent_blue': (100, 150, 255),
        'highlight': (255, 255, 100),
        'warning': (255, 165, 0),
        'success': (100, 255, 100)
    }
    
    # Light Theme (Alternative)
    LIGHT = {
        'background': (255, 255, 255),
        'text_primary': (0, 0, 0),
        'text_secondary': (64, 64, 64),
        'text_muted': (128, 128, 128),
        'grid_lines': (200, 200, 200),
        'ui_background': (240, 240, 240),
        'ui_border': (100, 100, 100),
        'player_x': (255, 0, 0),
        'player_o': (0, 0, 255),
        'accent_yellow': (255, 200, 0),
        'accent_green': (0, 200, 0),
        'accent_orange': (255, 140, 0),
        'accent_blue': (0, 100, 255),
        'highlight': (255, 200, 0),
        'warning': (255, 140, 0),
        'success': (0, 200, 0)
    }
    
    # Cyberpunk Theme (Alternative)
    CYBERPUNK = {
        'background': (10, 10, 20),
        'text_primary': (0, 255, 255),
        'text_secondary': (200, 200, 255),
        'text_muted': (100, 100, 150),
        'grid_lines': (50, 50, 80),
        'ui_background': (20, 20, 40),
        'ui_border': (0, 255, 255),
        'player_x': (255, 50, 100),
        'player_o': (50, 200, 255),
        'accent_yellow': (255, 255, 0),
        'accent_green': (0, 255, 100),
        'accent_orange': (255, 150, 0),
        'accent_blue': (100, 150, 255),
        'highlight': (255, 255, 0),
        'warning': (255, 150, 0),
        'success': (0, 255, 100)
    }

# Current theme - change this to switch themes
CURRENT_THEME = Theme.CYBERPUNK

# Legacy color definitions for backward compatibility
# These will automatically use the current theme
def get_color(color_name):
    """Get color from current theme"""
    return CURRENT_THEME.get(color_name, (255, 255, 255))

# Legacy color assignments
WHITE = get_color('text_primary')
BLACK = get_color('background')
GRAY = get_color('text_muted')
LIGHT_GRAY = get_color('text_secondary')
DARK_GRAY = get_color('ui_background')
RED = get_color('player_x')
BLUE = get_color('player_o')
GREEN = get_color('success')
YELLOW = get_color('highlight')
ORANGE = get_color('warning')

# Board Settings
BOARD_SIZE = 3  # 3x3 grid
CELL_SIZE = 80
BOARD_MARGIN = 50
BOARD_OFFSET_X = (WINDOW_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
BOARD_OFFSET_Y = (WINDOW_HEIGHT - BOARD_SIZE * CELL_SIZE) // 2

# Game Settings
ROUNDS_TO_WIN = 6  # Best of 10 rounds
TOTAL_ROUNDS = 10

# Font Settings
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24 