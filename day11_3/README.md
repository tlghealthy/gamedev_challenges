# Pygame-CE Game State Manager

A lightweight, drop-in game state manager for pygame-ce projects that provides clean state management with minimal overhead.

## Systems Design Plan

### Core Architecture

#### 1. State Management Pattern
- **State Stack**: Maintains a stack of game states for hierarchical navigation
- **State Interface**: Each state implements a common interface with lifecycle methods
- **State Transitions**: Clean push/pop/switch operations with optional data passing

#### 2. State Lifecycle
```
init() → enter(data) → update(dt) → render(surface) → exit() → cleanup()
```

#### 3. Core Components

**GameStateManager**
- Manages the state stack
- Handles state transitions
- Provides global state access
- Manages shared resources

**BaseState**
- Abstract base class for all states
- Default implementations for common operations
- Optional lifecycle hooks

**State Interface**
```python
class GameState:
    def init(self) -> None
    def enter(self, data: dict) -> None
    def update(self, dt: float) -> None
    def render(self, surface: pygame.Surface) -> None
    def exit(self) -> None
    def cleanup(self) -> None
```

#### 4. Key Features

**Simple Integration**
- Single import, minimal setup
- Works with existing pygame-ce projects
- No external dependencies beyond pygame-ce

**Flexible State Transitions**
- Push: Add state to stack (pause current)
- Pop: Remove top state (resume previous)
- Switch: Replace current state
- Clear: Reset to single state

**Data Passing**
- Pass data between states during transitions
- Access shared data from any state
- Type-safe data storage

**Resource Management**
- Automatic cleanup on state exit
- Shared resource pool
- Memory leak prevention

#### 5. Usage Pattern

```python
# Initialize
manager = GameStateManager()
manager.push_state(MenuState())

# Main loop
while running:
    dt = clock.tick(60) / 1000.0
    manager.update(dt)
    manager.render(screen)
```

#### 6. State Examples

**Menu State**: Handle user input, render UI
**Game State**: Core gameplay logic
**Pause State**: Overlay with resume options
**Loading State**: Asset loading with progress

#### 7. Error Handling
- Graceful state transition failures
- Invalid state stack recovery
- Resource cleanup on exceptions

#### 8. Performance Considerations
- Minimal overhead per frame
- Efficient state switching
- Memory-conscious design
- No unnecessary object creation

### File Structure
```
game_state_manager/
├── __init__.py
├── manager.py          # Core GameStateManager
├── state.py           # BaseState abstract class
├── examples/
│   ├── menu_state.py
│   ├── game_state.py
│   └── demo.py
└── tests/
    └── test_manager.py
```

### Integration Strategy
1. Copy manager files to project
2. Import GameStateManager
3. Create state classes inheriting from BaseState
4. Initialize manager with initial state
5. Integrate into main game loop

This design provides a robust foundation for state management while maintaining simplicity and ease of integration.

## Quick Start

### Installation

1. Install pygame-ce:
```bash
pip install pygame-ce
```

2. Copy the `game_state_manager` folder to your project.

### Basic Usage

```python
import pygame
from game_state_manager import GameStateManager, BaseState

# Create a custom state
class MyGameState(BaseState):
    def init(self):
        self.font = pygame.font.Font(None, 36)
    
    def update(self, dt):
        # Handle input and game logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.manager.pop_state()
    
    def render(self, surface):
        # Render your game
        text = self.font.render("My Game!", True, (255, 255, 255))
        surface.blit(text, (100, 100))

# Initialize and use
pygame.init()
screen = pygame.display.set_mode((800, 600))
manager = GameStateManager()
manager.push_state(MyGameState())

# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000.0
    manager.update(dt)
    manager.render(screen)
    pygame.display.flip()
```

### Running the Demo

```bash
python demo.py
```

### Running Tests

```bash
python -m unittest game_state_manager.tests.test_manager
```

## Features Demonstrated

- **State Stack Management**: Push, pop, switch, and clear states
- **Data Passing**: Pass data between states during transitions
- **Shared Data**: Access global data from any state
- **Lifecycle Management**: Proper init, enter, update, render, exit, cleanup
- **Resource Management**: Automatic cleanup and memory management
- **Error Handling**: Graceful handling of edge cases

## Integration Tips

1. **Minimal Setup**: Just import and create a manager instance
2. **State Inheritance**: Inherit from `BaseState` for your game states
3. **Data Flow**: Use the data parameter to pass information between states
4. **Shared Resources**: Use `manager.set_shared_data()` for global state
5. **Clean Transitions**: Always call the appropriate transition method

The game state manager is designed to be lightweight and easy to integrate into existing pygame-ce projects while providing powerful state management capabilities. 