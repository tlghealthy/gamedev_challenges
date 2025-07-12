# ECS Fighting Platformer

A 2-player fighting platformer game built using Entity-Component-System (ECS) architecture with pygame and pymunk.

## Features

- **ECS Architecture**: Clean separation of concerns with entities, components, and systems
- **2-Player Combat**: WASD + Left Ctrl for Player 1, Arrow Keys + Right Ctrl for Player 2
- **Physics**: Realistic physics using pymunk with gravity, collision, and knockback
- **Damage System**: Players take damage and get knocked back further with each hit
- **Configurable**: All game constants stored in `settings.json` for easy tweaking

## Controls

### Player 1 (Red)
- **WASD**: Movement and jumping
- **Left Ctrl**: Attack

### Player 2 (Blue)
- **Arrow Keys**: Movement and jumping
- **Right Ctrl**: Attack

## Architecture

### Components
- `Position`: Entity position in world
- `Velocity`: Entity velocity
- `Player`: Player-specific data (controls, damage, facing direction)
- `Physics`: Pymunk physics body reference
- `Renderable`: Visual representation data
- `Attack`: Attack mechanics and cooldowns
- `Stage`: Platform/stage data

### Systems
- `InputSystem`: Handles player input and movement
- `PhysicsSystem`: Manages physics simulation
- `AttackSystem`: Processes attacks and collision detection
- `RenderSystem`: Handles all rendering

### Key Classes
- `Game`: Main orchestrator and game loop
- `World`: Manages entities and systems
- `EntityFactory`: Creates entities with proper components
- `PhysicsEngine`: Wrapper for pymunk physics

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game:
```bash
python run_game.py
```

## Configuration

Edit `settings.json` to adjust:
- Screen dimensions
- Colors
- Physics constants (gravity, movement speed, jump velocity)
- Combat mechanics (attack cooldown, damage, knockback)

## ECS Benefits

This architecture provides:
- **Modularity**: Easy to add new features without modifying existing code
- **Testability**: Systems can be tested independently
- **Extensibility**: New entity types and behaviors can be added easily
- **Maintainability**: Clear separation of concerns makes code easier to understand

## Future Enhancements

- Add more attack types
- Implement special moves
- Add power-ups
- Create multiple stages
- Add sound effects and music
- Implement AI opponents 