# Missile Defense - Classic Arcade Game

A classic missile defense arcade game built with Pygame where you must defend cities from incoming missiles by launching interceptors.

## Game Features

- **8 Cities to Defend**: Protect your cities from destruction
- **Incoming Missiles**: Missiles spawn from the top and target random cities
- **Interceptor System**: Click near missiles to launch interceptors from the bottom
- **Progressive Difficulty**: Game gets harder as you play with more missiles and faster spawn rates
- **Score System**: Earn points for destroying missiles, lose points when cities are hit
- **Visual Effects**: Explosions, missile trails, and city destruction animations

## How to Play

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game**:
   ```bash
   python missile_defense.py
   ```

3. **Controls**:
   - **Mouse Click**: Click near incoming missiles to launch interceptors
   - **ESC**: Quit the game

## Game Mechanics

- **Cities**: 8 cities at the bottom of the screen that you must protect
- **Missiles**: Red missiles fall from the top targeting random cities
- **Interceptors**: Blue missiles you launch by clicking near incoming missiles
- **Scoring**: 
  - +100 points for each missile destroyed
  - -200 points for each city destroyed
- **Game Over**: When all cities are destroyed

## Technical Features

- **Smooth Physics**: Realistic missile and interceptor trajectories
- **Collision Detection**: Precise collision detection between missiles, interceptors, and cities
- **Visual Polish**: Explosion effects, missile trails, and city destruction animations
- **Progressive Difficulty**: Spawn rate increases and more missiles appear over time
- **Clean Code Structure**: Well-organized classes for each game element

## Game Classes

- `City`: Represents cities that can be destroyed
- `Missile`: Incoming missiles that target cities
- `Interceptor`: Player-launched missiles to destroy incoming missiles
- `Explosion`: Visual explosion effects
- `Game`: Main game loop and state management

Enjoy defending your cities! 