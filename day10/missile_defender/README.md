# Missile Defender

A classic arcade-style missile defense game built with Pygame.

## Game Description

Defend your cities from incoming enemy missiles! You control three missile launchers positioned along the bottom of the screen. Click near a launcher to fire missiles that will intercept the incoming threats before they reach your cities.

## Features

- **5 Cities to Defend**: Each city has a unique building design with windows and roofs
- **3 Missile Launchers**: Strategic positioning allows for tactical defense
- **Progressive Difficulty**: Each level increases the number of incoming missiles
- **Realistic Physics**: Missiles follow calculated trajectories to their targets
- **Visual Effects**: Explosions with alpha blending and particle effects
- **Score System**: Earn points for each successful interception
- **Game Over**: When all cities are destroyed, the game ends

## Controls

- **Left Click**: Fire a missile from the nearest launcher to your mouse position
- **R Key**: Restart the game when game over
- **Close Window**: Quit the game

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python missile_defender.py
   ```

2. **Objective**: Prevent enemy missiles (red) from hitting your cities (gray buildings)

3. **Strategy**: 
   - Click near a launcher to fire defensive missiles (white)
   - Time your shots to intercept incoming threats
   - Watch the missile trajectories to predict where to aim
   - Each launcher has a reload time, so plan your shots carefully

4. **Scoring**: 
   - +100 points for each successful missile interception
   - Survive as long as possible to achieve high scores

5. **Difficulty**: 
   - Level 1: 5 missiles per wave
   - Each level increases missile count and speed
   - Waves come faster as you progress

## Game Elements

- **Cities**: Gray buildings with yellow windows and green roofs
- **Missile Launchers**: Gray structures with black barrels
- **Player Missiles**: White missiles with red tips and orange exhaust trails
- **Enemy Missiles**: Red missiles with white tips targeting cities
- **Explosions**: Yellow expanding circles when missiles collide

## Technical Details

- Built with Pygame 2.5.2
- 60 FPS gameplay
- 800x600 resolution
- Object-oriented design with separate classes for each game element
- Collision detection using bounding box calculations
- Alpha blending for explosion effects

Enjoy defending your cities! 