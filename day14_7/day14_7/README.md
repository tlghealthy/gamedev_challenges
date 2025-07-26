# Simple Physics-Based Game Prototype

## Controls

- **Aim & Launch:** Click and drag the mouse from the player (yellow ball) to set direction and power. Release to launch.
- **Advance Text:** Press SPACE to continue from level instructions.

## Rules

- Your goal is to launch the player (yellow ball) into the green goal area.
- Each level introduces a new mechanic:
  - **Level 1:** Learn to launch the ball to the goal.
  - **Level 2:** Avoid moving capsule obstacles while reaching the goal.
  - **Level 3:** Blue gravity zones will change the direction of gravity when entered.
- You can only launch once per level attempt.
- If you reach the goal, you advance to the next level.
- Complete all 3 levels to win!

## Requirements
- Python 3.8+
- `pygame-ce` and `pymunk` (install with `pip install pygame-ce pymunk`)

## How to Run

```bash
python game.py
``` 