# Procedural Shmup Game

A procedurally generated shoot 'em up game with randomized enemy patterns and attacks, ensuring each 10-minute run feels unique.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game:
```bash
python shmup.py
```

## Controls

- **Arrow Keys**: Move your ship
- **Space**: Shoot
- **ESC**: Exit game

## Gameplay

- Survive for 10 minutes while fighting procedurally generated enemy waves
- Each enemy type has unique movement patterns and attack styles
- Difficulty increases over time
- Your ship has 5 health points and temporary invulnerability after taking damage

## Enemy Types

Each enemy type features unique shapes, colors, and behaviors:

1. **Basic**: Fast-moving enemies with triangular, square, or diamond shapes
   - Fire aimed shots at the player
   - 15% chance to drop: Health, Rapid Fire, or Damage powerups

2. **Heavy**: Large, tanky enemies with hexagonal, octagonal, or square shapes
   - Slowly track the player while firing spread shots
   - 25% chance to drop: Shield, Health, Damage, or Triple Shot powerups

3. **Sine**: Wave-pattern enemies with diamond, star, or triangle shapes
   - Move in sinusoidal patterns while firing circular bursts
   - 20% chance to drop: Speed, Rapid Fire, or Triple Shot powerups

4. **Spiral**: Complex movement enemies with star, cross, or hexagon shapes
   - Spiral movement with rotating triple shots
   - 30% chance to drop: Shield, Speed, Damage, or Health powerups

All enemies feature:
- Randomized vibrant colors using various color schemes
- Stretched shapes (vertically or horizontally) for visual variety
- Rotating animations for dynamic appearance

## Powerups

Powerups can be collected in two ways:
1. **Random spawns** that fall from the top of the screen periodically
2. **Enemy drops** when defeating enemies (each enemy type has specific drop chances and powerup types)

Each powerup has a unique visual design:

1. **Health (Pink +)**: Restores 1 health point
2. **Rapid Fire (Yellow ⚡)**: Increases fire rate for 5 seconds
3. **Triple Shot (Cyan •••)**: Shoots 3 bullets at once for 7 seconds
4. **Shield (Blue Hexagon)**: Protects from one hit for 10 seconds
5. **Damage Boost (Orange ★)**: Doubles bullet damage for 8 seconds
6. **Speed Boost (Purple ↑)**: 50% faster movement for 6 seconds

## Features

- Procedurally generated wave patterns
- Enemies with diverse geometric shapes (triangles, squares, diamonds, hexagons, stars, crosses)
- Dynamic shape stretching and rotation for visual variety
- Wide range of vibrant color schemes (pure hues, pastels, neon, deep colors)
- Enemy-specific powerup drops with varying drop chances
- 6 different powerup types with unique visual indicators
- Particle effects for explosions
- Dynamic difficulty scaling
- Score system based on enemies defeated and current difficulty
- Active powerup indicators showing remaining duration

Each run is unique thanks to randomized:
- Enemy spawn patterns and formations
- Enemy shapes, colors, and size variations
- Shape stretching and rotation speeds
- Attack timings, patterns, and projectile speeds
- Movement parameters and behaviors
- Wave compositions
- Powerup drops from enemies based on type
- Random powerup spawns 