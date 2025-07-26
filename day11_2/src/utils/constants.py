import json
from pathlib import Path

def load_settings():
    """Load settings from settings.json"""
    settings_path = Path(__file__).parent.parent.parent / "settings.json"
    with open(settings_path, 'r') as f:
        return json.load(f)

# Game states
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
VICTORY = "victory"

# Tower types
TOWER_RED = "red"
TOWER_BLUE = "blue"
TOWER_GREEN = "green"

# Enemy types
ENEMY_SMALL = "small"
ENEMY_MEDIUM = "medium"
ENEMY_LARGE = "large"
ENEMY_FAST = "fast"
ENEMY_TANK = "tank"

# UI elements
UI_BUTTON = "button"
UI_PANEL = "panel"
UI_LABEL = "label"

# Events
EVENT_TOWER_PLACED = "tower_placed"
EVENT_ENEMY_KILLED = "enemy_killed"
EVENT_WAVE_COMPLETE = "wave_complete"
EVENT_LEVEL_COMPLETE = "level_complete"
EVENT_GAME_OVER = "game_over" 