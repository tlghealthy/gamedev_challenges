# Abstract Dash Collector

A unique arcade game prototype made with pygame-ce. Collect orbs, avoid enemies, and use your dash ability to survive and score as high as possible!

## How to Play
- **Move** your player (blue circle) using the arrow keys or WASD.
- **Collect yellow orbs** to gain points. Orbs move in circular patterns.
- **Avoid red enemies**. If you touch an enemy while not dashing, it's game over!
- **Dash** (press SPACE) to phase through enemies for a short time. Dash has a cooldown (watch the arc around your player).
- The game ends if you collide with an enemy while not dashing. Press **R** to restart after a game over.

## Controls
- **Arrow Keys / WASD**: Move
- **Spacebar**: Dash (temporary invulnerability, cooldown applies)
- **R**: Restart after game over
- **Esc / Window Close**: Quit

## Objective
- Collect as many orbs as possible before getting caught by an enemy!

## Requirements
- Python 3.8+
- `pygame-ce` (install with `pip install pygame-ce`)

## Run the Game
```bash
python game.py
```

Enjoy the abstract challenge! 