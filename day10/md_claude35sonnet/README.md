# Missile Defense - Arcade Classic

A modern implementation of the classic arcade missile defense game using Pygame. Defend your cities from incoming enemy missiles by launching interceptors to destroy them before they reach their targets.

## Features

### Core Gameplay
- **City Defense**: Protect 6 cities from enemy missile attacks
- **Missile Interception**: Launch defensive missiles from 4 launcher positions
- **Progressive Difficulty**: Enemy missiles become faster and more numerous as levels increase
- **Real-time Combat**: Fast-paced action requiring quick reflexes and strategic thinking

### Enhanced Mechanics
- **Health System**: Cities have health bars and can take damage before being destroyed
- **Ammunition System**: Launchers have limited ammo and require reloading
- **Power-ups**: Collect special items for temporary advantages:
  - **Rapid Fire**: Faster missile firing rate
  - **Shield**: Cities become temporarily invulnerable
  - **Multi Shot**: Fire from multiple launchers simultaneously

### Visual Effects
- **Particle Systems**: Missile trails and explosion effects
- **Damage Animation**: Visual feedback when cities take damage
- **Power-up Indicators**: Clear UI showing active power-up timers
- **Starfield Background**: Immersive space environment

### Game Features
- **Score System**: Earn points for successful interceptions
- **Level Progression**: Increasing difficulty with each wave
- **Pause Function**: Press P to pause/resume the game
- **Game Over Screen**: Final score display with restart option

## Controls

- **Mouse Click**: Fire missile from nearest launcher
- **P**: Pause/Resume game
- **R**: Restart game (when game over)
- **ESC**: Quit game

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python missile_defense.py
   ```

## Game Strategy

### Basic Tips
- **Prioritize Threats**: Focus on missiles targeting cities with lower health
- **Manage Ammo**: Don't waste missiles on targets that will miss
- **Use Power-ups Wisely**: Save rapid fire for intense waves
- **Position Awareness**: Know which launcher is closest to your mouse

### Advanced Techniques
- **Predictive Shooting**: Lead your shots based on missile trajectory
- **Wave Management**: Clear current missiles before new ones spawn
- **Resource Conservation**: Balance ammo usage across all launchers
- **Power-up Timing**: Activate shields during heavy bombardment

## Technical Details

### Architecture
- **Object-Oriented Design**: Clean separation of game entities
- **Component System**: Modular classes for different game elements
- **Event-Driven**: Responsive input handling and game state management
- **Performance Optimized**: Efficient collision detection and rendering

### Game Objects
- **City**: Defendable targets with health system
- **MissileLauncher**: Player-controlled defense systems
- **PlayerMissile**: Interceptor projectiles
- **EnemyMissile**: Hostile incoming threats
- **Explosion**: Visual feedback for impacts
- **PowerUp**: Temporary ability enhancements

### Difficulty Scaling
- **Wave Size**: Increases from 3 to 12 missiles per wave
- **Missile Speed**: Gradually increases with level
- **Spawn Rate**: Faster missile spawning at higher levels
- **Power-up Rarity**: Strategic timing becomes more important

## Development

This implementation focuses on:
- **Authentic Arcade Feel**: True to the original game mechanics
- **Modern Polish**: Enhanced visuals and smooth gameplay
- **Balanced Progression**: Fair difficulty curve
- **Responsive Controls**: Precise and intuitive input handling

The game successfully captures the essence of the classic missile defense arcade game while adding modern enhancements that make it more engaging and visually appealing. 