# Abstract Tower Defense - Systems Design

## Game Overview
An abstract tower defense game using colored shapes and minimal text. Players place towers to defend against waves of enemies following paths to reach the goal.

## Core Systems

### 1. Game Engine & Rendering
- **Pygame-CE**: Main game engine for rendering and input handling
- **Pygame-GUI**: UI elements (buttons, panels, tooltips)
- **Game Loop**: Fixed timestep for consistent gameplay
- **Renderer**: Shape-based rendering (circles, rectangles, triangles)

### 2. Game State Management
- **Game States**: Menu, Playing, Paused, Game Over, Victory
- **Level Management**: Progressive difficulty with unlock system
- **Save System**: Level progress and settings persistence

### 3. Tower System
- **Tower Types**: 
  - Red Circle: Fast, low damage (anti-swarm)
  - Blue Triangle: Medium range, medium damage (balanced)
  - Green Square: Slow, high damage (anti-boss)
- **Placement**: Grid-based with visual feedback
- **Upgrades**: Damage, range, fire rate improvements
- **Targeting**: Nearest enemy, strongest enemy, first in path

### 4. Enemy System
- **Enemy Types**:
  - Small Circle: Fast, low health
  - Medium Triangle: Balanced stats
  - Large Square: Slow, high health
- **Pathfinding**: Pre-calculated paths with waypoints
- **Wave System**: Progressive difficulty with boss waves
- **Health Display**: Color intensity indicates remaining health

### 5. Economy System
- **Resources**: Single currency (points) earned from kills
- **Costs**: Tower placement and upgrades
- **Income**: Bonus points for wave completion

### 6. Level Design
- **Path Layouts**: Various configurations (straight, curved, branching)
- **Difficulty Progression**:
  - Level 1: Single path, 3 waves, basic enemies
  - Level 2: Two paths, 5 waves, mixed enemies
  - Level 3: Complex path, 7 waves, boss enemy
  - Level 4+: Advanced layouts with multiple enemy types

### 7. Visual Design
- **Color Scheme**: High contrast for accessibility
- **Shapes**: Geometric abstraction for clarity
- **Animations**: Smooth transitions and effects
- **Feedback**: Visual cues for all actions

### 8. Audio System
- **Sound Effects**: Tower placement, enemy death, wave start
- **Background Music**: Ambient tracks for different states

## Technical Architecture

### File Structure
```
src/
├── main.py              # Entry point
├── game/
│   ├── __init__.py
│   ├── game_state.py    # State management
│   ├── renderer.py      # Rendering system
│   └── audio.py         # Audio management
├── entities/
│   ├── __init__.py
│   ├── tower.py         # Tower logic
│   ├── enemy.py         # Enemy logic
│   └── projectile.py    # Projectile system
├── systems/
│   ├── __init__.py
│   ├── pathfinding.py   # Path calculation
│   ├── wave_manager.py  # Wave spawning
│   └── economy.py       # Resource management
├── levels/
│   ├── __init__.py
│   ├── level_data.py    # Level definitions
│   └── level_loader.py  # Level loading
├── ui/
│   ├── __init__.py
│   ├── menu.py          # Menu system
│   ├── hud.py           # Heads-up display
│   └── buttons.py       # UI components
└── utils/
    ├── __init__.py
    ├── constants.py     # Game constants
    └── helpers.py       # Utility functions
```

### Data Flow
1. **Input** → Game State → Systems → Entities → Renderer
2. **Level Data** → Wave Manager → Enemy Spawning
3. **Player Actions** → Economy → Tower Placement
4. **Game Events** → Audio → Visual Feedback

### Performance Considerations
- Object pooling for projectiles and effects
- Spatial partitioning for collision detection
- Efficient pathfinding with pre-calculated routes
- Minimal texture usage (shapes only)

## Settings Configuration
All adjustable parameters stored in `settings.json`:
- Screen dimensions and scaling
- Game balance (tower costs, enemy health, wave timing)
- Visual preferences (colors, animation speed)
- Audio levels
- Difficulty multipliers

## Development Phases
1. **Core Engine**: Basic rendering and game loop
2. **Tower System**: Placement, targeting, upgrades
3. **Enemy System**: Movement, health, waves
4. **Level System**: Multiple levels with progression
5. **UI/UX**: Menus, HUD, visual feedback
6. **Polish**: Audio, animations, balance
7. **Testing**: Playtesting and difficulty tuning 