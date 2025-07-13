# Tic Tac Toe Evolution - Prototype

A competitive, ever-changing twist on the classic game of tic tac toe. Two players face off in a series of rounds, starting with the familiar 3x3 grid. After each round, players vote on unique "Game Modifiers" that alter the rules, board, or win conditions for the next round.

## Features (Current Prototype)

- **Classic Tic Tac Toe Gameplay**: Standard 3x3 grid with X and O players
- **Round-based System**: Best of 10 rounds (first to 6 wins)
- **Modifier Voting System**: After each round, players vote on game modifiers
- **Implemented Modifiers**:
  - **Board Expansion**: Increases board size by 1 in both directions (stacks - can be applied multiple times)
  - **+1 Extra Move per turn**: Each player takes one extra move per turn (stacks - multiple instances work together)
  - **Random Adjacent**: After each move, place an additional mark in a random adjacent cell (stacks - multiple instances place multiple marks)
  - **Random Adjacent Chance**: After each move, 50% chance to place an additional mark in a random adjacent cell
  - **Random Adjacent Flip**: After each move, flip an adjacent enemy piece to your side
  - **Diagonal Win Reduction**: Reduce diagonal win requirement by 1 piece (stacks - multiple instances reduce further)
  - **Horizontal Win Reduction**: Reduce horizontal win requirement by 1 piece (stacks - multiple instances reduce further)
- **Modular Architecture**: Designed for easy extension with new modifiers
- **Clean UI**: Clear visual feedback and game state information
- **Dynamic Board Rendering**: UI adapts to different board sizes

## Project Structure

```
day8/
├── game.py              # Main game class and entry point
├── game_state.py        # Game state management and phases
├── board.py             # Tic-tac-toe board logic
├── modifier_system.py   # Modifier system foundation
├── ui_manager.py        # User interface and rendering
├── settings.py          # Game configuration and constants
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game**:
   ```bash
   python game.py
   ```

## How to Play

1. **Title Screen**: Click anywhere to start a new game
2. **Gameplay**: Players take turns clicking on empty cells to place X or O
3. **Round End**: When a round ends (win or tie), click to continue
4. **Modifier Voting**: Click on a modifier to vote for it
5. **Next Round**: The winning modifier is applied and the next round begins
6. **Game End**: First player to win 6 rounds wins the game

## Architecture Overview

### Game State Management
- `GameState` class manages the overall game flow
- Tracks scores, current player, round number, and active modifiers
- Handles transitions between different game phases

### Board System
- `Board` class handles the tic-tac-toe grid
- Manages moves, win detection, and board state
- Designed to be extensible for different board sizes and configurations

### Modifier System
- `ModifierSystem` provides the foundation for game modifiers
- Handles voting, modifier application, and stacking
- `Modifier` base class allows easy creation of new modifiers

### UI Management
- `UIManager` handles all rendering and user interaction
- Clean separation between game logic and presentation
- Responsive design that adapts to different game states

## Extending the Game

### Theme System

The game now includes a flexible theme system that makes it easy to customize colors and switch between different visual styles.

#### Available Themes
- **Dark Theme** (default): Black background with bright, readable text
- **Light Theme**: White background with dark text (classic look)
- **Cyberpunk Theme**: Dark blue background with cyan accents

#### Switching Themes

**Method 1: Command Line**
```bash
# Switch to light theme
python theme_switcher.py light

# Switch to cyberpunk theme  
python theme_switcher.py cyberpunk

# Switch back to dark theme
python theme_switcher.py dark
```

**Method 2: In Code**
```python
from theme_manager import switch_theme

# Switch themes programmatically
switch_theme('light')
switch_theme('cyberpunk')
switch_theme('dark')
```

#### Creating Custom Themes

To add a new theme, edit `settings.py` and add a new theme dictionary:

```python
# In settings.py, add to the Theme class:
CUSTOM = {
    'background': (25, 25, 35),
    'text_primary': (255, 255, 255),
    'text_secondary': (200, 200, 200),
    'text_muted': (128, 128, 128),
    'grid_lines': (60, 60, 80),
    'ui_background': (40, 40, 60),
    'ui_border': (150, 150, 200),
    'player_x': (255, 120, 120),
    'player_o': (120, 180, 255),
    'accent_yellow': (255, 255, 120),
    'accent_green': (120, 255, 120),
    'accent_orange': (255, 180, 120),
    'accent_blue': (120, 180, 255),
    'highlight': (255, 255, 120),
    'warning': (255, 180, 120),
    'success': (120, 255, 120)
}
```

Then switch to it with: `python theme_switcher.py custom`

#### Theme Color Categories

Each theme defines these color categories:
- `background`: Main background color
- `text_primary`: Primary text color (titles, important info)
- `text_secondary`: Secondary text color (instructions, descriptions)
- `text_muted`: Muted text color (less important info)
- `grid_lines`: Board grid line color
- `ui_background`: UI element backgrounds
- `ui_border`: UI element borders
- `player_x`: Player X color
- `player_o`: Player O color
- `accent_*`: Various accent colors for highlights
- `highlight`: General highlight color
- `warning`: Warning/alert color
- `success`: Success/positive color

### Adding New Modifiers

1. Create a new class that inherits from `Modifier`
2. Implement the `apply()` and `can_apply()` methods
3. Add the modifier to the pool in `_initialize_modifiers()`

Example:
```python
class MyModifier(Modifier):
    def __init__(self):
        super().__init__("My Modifier", "Description", "Category")
    
    def can_apply(self, game_state, board):
        return True
    
    def apply(self, game_state, board):
        # Implement modifier logic here
        return True
```

### Adding New Game Phases

1. Add the new phase to the `GamePhase` enum in `game_state.py`
2. Add handling in the main game loop in `game.py`
3. Add rendering logic in `ui_manager.py`

### Modifying Game Rules

- Board size: Modify `BOARD_SIZE` in `settings.py`
- Win conditions: Modify `check_winner()` in `board.py`
- Round count: Modify `ROUNDS_TO_WIN` and `TOTAL_ROUNDS` in `settings.py`

## Future Enhancements

This prototype provides a solid foundation for the full game. Future development could include:

- **100+ Unique Modifiers**: Expand the modifier pool with complex interactions
- **Animated Effects**: Visual feedback for modifier applications
- **Sound Effects**: Audio feedback for game events
- **Difficulty Settings**: Different modifier pools for different skill levels
- **Tournament Mode**: Balanced modifier sets for competitive play
- **Save/Load System**: Save game progress and modifier preferences
- **AI Opponent**: Single-player mode with computer opponent

## Technical Notes

- Built with Pygame for cross-platform compatibility
- Modular design allows for easy testing and extension
- Clean separation of concerns between game logic and presentation
- Type hints used throughout for better code maintainability
- Designed to handle complex modifier interactions efficiently 