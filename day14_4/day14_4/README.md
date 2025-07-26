# Abstract Arcade: Orbital Dodge

A unique arcade game prototype using pygame-ce. Control a colored shape orbiting a center, collect orbs, and dodge enemies!

## How to Play
- You control a blue circle orbiting the center of the screen.
- Use **Left Arrow** and **Right Arrow** keys to rotate around the center.
- Collect yellow orbs to score points.
- Avoid red enemy shapes that orbit at different radii and speeds.
- Every 3 orbs collected, a new enemy appears.
- You have 3 lives. Colliding with an enemy costs a life.
- The game ends when you lose all lives. Press **R** to restart.

## Controls
- **Left Arrow**: Rotate counterclockwise
- **Right Arrow**: Rotate clockwise
- **R**: Restart after game over
- **ESC** or close window: Quit

## Requirements
- Python 3.8+
- `pygame-ce` (install with `pip install pygame-ce`)

## Unique Mechanics
- Player is locked to a circular orbit, not free movement.
- Enemies and orbs appear on different orbits, creating layered movement and timing challenges.
- The number of enemies increases as you score, ramping up difficulty.

Enjoy this abstract, shape-based arcade challenge! 