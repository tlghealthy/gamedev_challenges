# Missile Defense Arcade Game

A classic arcade-style missile defense game built with Pygame where you must defend cities from incoming missile attacks.

## Features

- **5 Cities to Defend**: Protect your cities from enemy missiles
- **Mouse Control**: Click anywhere to launch defensive missiles
- **Progressive Difficulty**: Speed and spawn rate increase with each level
- **Score System**: Earn points for each successful interception
- **Visual Effects**: Explosions and missile trails for immersive gameplay
- **Lives System**: You have 3 lives before game over

## How to Play

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game**:
   ```bash
   python missile_defense.py
   ```

## Controls

- **Left Mouse Click**: Launch defensive missile at cursor position
- **R Key**: Restart game (when game over)

## Game Mechanics

- **Enemy Missiles**: Red missiles fall from the top targeting your cities
- **Player Missiles**: Green missiles launched from your launcher (blue rectangle at bottom)
- **Explosions**: When your missile hits an enemy missile, both are destroyed with an explosion effect
- **City Destruction**: If an enemy missile reaches a city, it's destroyed and you lose a life
- **Level Progression**: Every 1000 points advances you to the next level with increased difficulty

## Game Over Conditions

- All 3 lives are lost
- All cities are destroyed

## Scoring

- **Missile Interception**: 100 points per successful hit
- **Level Bonus**: Higher levels provide more challenging gameplay

Enjoy defending your cities! 