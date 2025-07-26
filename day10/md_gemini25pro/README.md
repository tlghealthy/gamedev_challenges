# Missile Defense - Classic Arcade Game

A faithful recreation of the classic missile defense arcade game using Pygame. Defend your cities from incoming missiles by launching interceptors to destroy them before they reach their targets.

## Features

- **8 Cities to Defend**: Strategically placed cities that you must protect
- **Incoming Missiles**: Missiles spawn from the top of the screen and target random cities
- **Interceptor System**: Click anywhere to launch interceptors from your ground-based launcher
- **Explosion Effects**: Visual explosion effects when missiles are destroyed or hit cities
- **Progressive Difficulty**: Game gets harder as you advance through levels
- **Score System**: Earn points for each missile destroyed
- **Lives System**: Lose lives when cities are destroyed
- **Visual Effects**: Missile trails, explosion animations, and city destruction effects

## How to Play

1. **Objective**: Prevent incoming missiles from hitting your cities
2. **Controls**: 
   - Left-click anywhere on the screen to launch an interceptor
   - Interceptors automatically travel toward your click location and explode
3. **Strategy**: 
   - Anticipate missile trajectories
   - Use explosion radius to destroy multiple missiles
   - Prioritize missiles closest to cities
4. **Scoring**: +100 points per missile destroyed
5. **Lives**: You lose a life each time a city is destroyed
6. **Levels**: Advance to higher levels by destroying more missiles (10 per level)

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python missile_defense.py
   ```

## Game Mechanics

- **Missiles**: Spawn from random positions at the top, targeting random cities
- **Interceptors**: Launch from the center-bottom launcher, explode on impact or proximity
- **Explosions**: Have a radius that can destroy multiple missiles
- **Cities**: Show windows and roofs when intact, rubble when destroyed
- **Difficulty**: Missile spawn rate increases with each level

## Game Over

The game ends when you lose all 3 lives. Press 'R' to restart or 'Q' to quit.

Enjoy defending your cities! 