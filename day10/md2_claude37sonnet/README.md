# Missile Defender

A classic arcade-style missile defense game built with Pygame where you must protect cities from incoming missile attacks.

## Game Description

Missile Defender is a strategic defense game where you control missile launchers to intercept incoming enemy missiles before they destroy your cities. The game features progressive difficulty with multiple levels, each increasing in challenge.

## Features

- **Progressive Difficulty**: 5 levels with increasing challenge
- **Multiple Cities**: Defend 3-7 cities depending on the level
- **Multiple Launchers**: Control 1-3 missile launchers
- **Visual Effects**: Missile trails, explosions, and city destruction
- **Score System**: Earn points for successful interceptions
- **Victory Condition**: Complete all 5 levels to win

## Controls

- **Mouse Click**: Fire defense missiles at the cursor position
- **SPACE**: Restart game (when game over or victory)
- **ESC**: Quit game

## Level Progression

- **Level 1**: 1 launcher, 3 cities, slow missiles (5 per wave)
- **Level 2**: 1 launcher, 4 cities, faster missiles (6 per wave)
- **Level 3**: 2 launchers, 5 cities, even faster missiles (7 per wave)
- **Level 4**: 2 launchers, 6 cities, fast missiles (8 per wave)
- **Level 5**: 3 launchers, 7 cities, very fast missiles (10 per wave)

## Scoring

- **Successful Interception**: +100 points
- **City Destroyed**: -200 points

## Installation

1. Make sure you have Python 3.6+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python missile_defender.py
   ```

2. **Objective**: Click to fire defense missiles (green) at incoming enemy missiles (red)

3. **Strategy**: 
   - Lead your shots - missiles take time to reach their target
   - Prioritize missiles closest to cities
   - Use multiple launchers strategically in later levels
   - Watch your reload times - launchers can't fire continuously

4. **Win Condition**: Complete all 5 levels by surviving each wave of missiles

5. **Lose Condition**: All cities are destroyed

## Game Elements

- **Cities**: Gray buildings with yellow windows at the bottom of the screen
- **Missile Launchers**: Green bases with blue radar dishes
- **Enemy Missiles**: Red missiles coming from the top of the screen
- **Defense Missiles**: Green missiles fired from your launchers
- **Explosions**: Orange explosions when missiles collide or hit cities

## Tips

- Start with the first level to get familiar with the controls
- Pay attention to missile trajectories and lead your shots
- In later levels, use multiple launchers to cover different areas
- Don't panic - take your time to aim accurately
- Watch the missile spawn rate increase in higher levels

Enjoy defending your cities! 