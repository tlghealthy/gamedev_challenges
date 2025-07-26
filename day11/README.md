# Defend Game

A compact pygame-ce-based defense game where you protect 6 squares from waves of attackers.

## Game Description

**Objective**: Protect 6 bottom squares for 5 waves.
- Lose wave → ≥3 squares gone
- Win game → clear wave 5 with ≥1 square left

**Controls**:
- Mouse = aim
- Left-click = fire (1 second reload)
- Shot = green 6px circle from bottom center → detonates at click point, spawns 0.6s green ring (35px)

**Threats**: "Attackers" = orange 6px circles from screen top
- Direction: random bottom-square ±15°
- Speed by wave: 80, 110, 140, 170, 200 px/s
- Count by wave: 6, 10, 14, 18, 24
- Gap shrinks from 1.2s to 0.4s
- Touch explosion/square/floor → small orange blast (VFX)

**Scoring**:
- +10 per attacker intercepted
- -25 per square lost
- Wave-clear bonus = 100 × squares alive
- HUD (top): Score #### •• Lvl n/5

**Game Flow**:
1. Show "DEFEND" → first click hides text → spawn attackers until list empty
2. If <3 squares lost ⇒ next wave (reload shots, reset lost-this-level)
3. Else game-over
4. After wave 5 or on loss: display final score

**Feedback Cues**:
- Intercept → ring flash
- Square hit → square flashes red, then disappears
- Wave clear → "Wave Clear!" banner 1s

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game:
   ```bash
   python defend.py
   ```

## Customization

All game settings can be easily modified in `settings.json`:
- Window dimensions and FPS
- Colors
- Game mechanics (wave counts, speeds, timings)
- Scoring values
- Visual elements (sizes, positions)

## Code Structure

The game uses a compact, class-based architecture:
- `Settings`: Loads and manages configuration from JSON
- `Explosion`: Handles visual explosion effects with fade-out
- `Shot`: Manages projectile movement and collision
- `Attacker`: Controls enemy movement patterns
- `Square`: Manages protectable targets with hit feedback
- `Game`: Main game loop and state management

Each class is designed for clarity and minimal code while maintaining functionality.

## Technology

Built with **pygame-ce** (Community Edition), the actively maintained fork of pygame that provides:
- Better performance and compatibility
- Active development and bug fixes
- Enhanced features and improvements
- Drop-in replacement for pygame 