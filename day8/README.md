# Tic Tac Toe Evolution - Prototype

A competitive, ever-changing twist on the classic game of tic tac toe. Two players face off in a series of rounds, starting with the familiar 3x3 grid. After each round, players vote on unique "Game Modifiers" that alter the rules, board, or win conditions for the next round.

## Features (Current Prototype)

- **Classic Tic Tac Toe Gameplay**: Standard 3x3 grid with X and O players
- **Round-based System**: Best of 10 rounds (first to 6 wins)
- **Modifier Voting System**: After each round, players vote on game modifiers
- **Implemented Modifiers**:
  - **Board Expansion**: Increases board size by 1 in both directions (stacks - can be applied multiple times)
  - **Double Move**: Each player takes two moves per turn (stacks - multiple instances work together)
  - **Random Adjacent**: After each move, an additional mark is placed in a random adjacent cell (stacks - multiple instances place multiple marks)
  - **Diagonal Only**: Only diagonal wins count (no horizontal/vertical wins)
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