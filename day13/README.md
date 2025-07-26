# Verlet Physics Engine for Pygame Games

A lightweight, position-based physics engine built on Verlet integration, designed for creating small physics-based games with Pygame. This engine provides realistic physics simulation with minimal computational overhead, making it perfect for platformers, puzzle games, and interactive simulations.

## Features

### Core Physics System
- **Verlet Integration**: Stable position-based physics simulation
- **Rigid Body Physics**: Support for rectangles, circles, and polygons
- **Collision Detection**: AABB and shape-specific collision detection
- **Constraint System**: Distance and angle constraints for complex objects
- **Material Properties**: Configurable density, friction, restitution, and damping

### Game Development Features
- **Player Controller**: Built-in physics-based character movement
- **Physics World**: Centralized simulation management
- **Collision Callbacks**: Event-driven collision handling
- **Raycasting**: Line-of-sight and targeting systems
- **Utility Functions**: Pre-built objects for common game elements

### Performance Optimizations
- **Efficient Algorithms**: Optimized for small to medium-sized games
- **Configurable Iterations**: Adjustable constraint and collision iterations
- **Debug Support**: Built-in debugging and visualization tools

## Installation

1. Ensure you have Python 3.7+ and Pygame installed:
```bash
pip install pygame
```

2. Copy the physics engine files to your project:
   - `verlet_physics.py` - Main physics engine
   - `physics_config.json` - Configuration file (optional)

## Quick Start

### Basic Setup

```python
import pygame
from verlet_physics import *

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create physics world
world = PhysicsWorld(gravity=Vector2(0, 800), bounds=(800, 600))

# Create a player
player = create_player(world, 400, 300, 25)
player_controller = PlayerController(player, speed=350, jump_force=450)

# Create a platform
platform = create_platform(world, 400, 500, 200, 20)

# Game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update physics
    world.update(dt)
    
    # Handle player input
    keys = pygame.key.get_pressed()
    player_controller.handle_input(keys, dt)
    player_controller.update(dt)
    
    # Render
    screen.fill((30, 30, 30))
    # ... render your objects here
    pygame.display.flip()

pygame.quit()
```

### Creating Different Object Types

```python
# Static platforms
platform = create_platform(world, x, y, width, height)

# Dynamic player character
player = create_player(world, x, y, size)

# Bouncing balls
ball = create_ball(world, x, y, radius)

# Ropes and chains
rope = create_rope(world, start_pos, segments, segment_length, stiffness)

# Custom rigid bodies
rectangle = RectangleBody((x, y), width, height, body_type=BodyType.DYNAMIC)
circle = CircleBody((x, y), radius, body_type=BodyType.DYNAMIC)
polygon = PolygonBody(vertices, body_type=BodyType.DYNAMIC)
```

## Game Examples

### 1. Physics Demo (`physics_demo.py`)
A comprehensive demo showcasing all engine features:
- Interactive physics objects
- Mouse-based object creation and manipulation
- Real-time physics simulation
- Collision detection and response

**Controls:**
- WASD/Arrows: Move player
- Space: Jump
- Mouse: Click and drag objects
- UI Buttons: Add balls, ropes, clear objects
- R: Reset level

### 2. Platformer Game (`platformer_example.py`)
A complete platformer game demonstrating:
- Player movement and jumping
- Enemy AI with physics
- Collectible coins
- Multiple levels
- Score and lives system

**Controls:**
- WASD/Arrows: Move player
- Space: Jump
- R: Restart (when game over)
- Escape: Quit

## Advanced Usage

### Custom Materials

```python
# Create custom physics material
ice_material = PhysicsMaterial(
    density=1.0,
    friction=0.05,    # Very slippery
    restitution=0.1,  # Low bounce
    damping=0.98
)

# Apply to objects
ice_platform = RectangleBody((x, y), width, height, 
                           body_type=BodyType.STATIC, 
                           material=ice_material)
```

### Collision Handling

```python
def on_collision(body1, body2):
    # Handle specific collision types
    if body1 == player and body2 in enemies:
        player_hit()
    elif body1 == player and body2 in coins:
        collect_coin(body2)

# Register collision callback
world.add_collision_callback(on_collision)
```

### Raycasting

```python
# Cast a ray from player position
start = player.get_center()
direction = Vector2(1, 0)  # Right direction
hit_body = world.raycast(start, direction, 100)

if hit_body:
    print(f"Hit: {hit_body}")
```

### Custom Constraints

```python
# Create distance constraint between two nodes
constraint = DistanceConstraint(node1, node2, rest_length, stiffness)

# Create angle constraint between three nodes
angle_constraint = AngleConstraint(node1, node2, node3, rest_angle, stiffness)

# Add to body
body.add_constraint(constraint)
```

## Configuration

The engine can be configured via `physics_config.json`:

```json
{
    "debug_print": false,
    "physics": {
        "gravity": [0, 800],
        "damping": 0.99,
        "constraint_iterations": 3
    },
    "materials": {
        "ice": {
            "density": 1.0,
            "friction": 0.05,
            "restitution": 0.1
        }
    }
}
```

## Game Types You Can Create

### Platformers
- Physics-based character movement
- Dynamic platforms and obstacles
- Enemy AI with physics
- Collectibles and power-ups

### Puzzle Games
- Physics-based puzzles
- Rope and chain mechanics
- Ball rolling and bouncing
- Gravity manipulation

### Fighting Games
- Physics-based combat
- Ragdoll physics
- Environmental interactions
- Weapon physics

### Simulation Games
- Sandbox environments
- Particle systems
- Fluid simulation (basic)
- Vehicle physics

## Performance Tips

1. **Limit Object Count**: Keep dynamic objects under 100 for best performance
2. **Use Static Objects**: Mark non-moving objects as static
3. **Adjust Iterations**: Reduce constraint iterations for better performance
4. **Optimize Collision**: Use simple shapes when possible
5. **Batch Updates**: Update physics less frequently for distant objects

## Troubleshooting

### Common Issues

**Objects passing through each other:**
- Increase constraint iterations
- Reduce time step
- Check collision detection settings

**Unstable physics:**
- Reduce gravity or damping
- Increase object mass
- Check constraint stiffness values

**Poor performance:**
- Reduce number of dynamic objects
- Use simpler collision shapes
- Lower constraint iterations

### Debug Mode

Enable debug mode in `physics_config.json`:
```json
{
    "debug_print": true,
    "rendering": {
        "show_debug_info": true,
        "show_collision_bounds": true
    }
}
```

## Extending the Engine

### Adding New Shapes

```python
class TriangleBody(RigidBody):
    def __init__(self, center, size, **kwargs):
        super().__init__(**kwargs)
        self.shape_type = CollisionShape.POLYGON
        
        # Create triangle vertices
        vertices = [
            (center[0], center[1] - size),
            (center[0] - size, center[1] + size),
            (center[0] + size, center[1] + size)
        ]
        
        # Add nodes and constraints
        for vertex in vertices:
            self.add_node(vertex)
        
        # Create triangular constraints
        for i in range(3):
            j = (i + 1) % 3
            dist = (self.nodes[i].pos - self.nodes[j].pos).length()
            self.add_constraint(DistanceConstraint(self.nodes[i], self.nodes[j], dist))
```

### Custom Physics Behaviors

```python
class SpringBody(RigidBody):
    def __init__(self, anchor, mass, spring_constant, **kwargs):
        super().__init__(**kwargs)
        self.anchor = Vector2(anchor)
        self.spring_constant = spring_constant
        
    def update(self, dt, gravity):
        super().update(dt, gravity)
        
        # Apply spring force
        center = self.get_center()
        displacement = center - self.anchor
        spring_force = -displacement * self.spring_constant
        self.apply_force_at_point(spring_force, center)
```

## License

This physics engine is provided as-is for educational and game development purposes. Feel free to modify and extend it for your projects.

## Contributing

Contributions are welcome! Areas for improvement:
- More collision detection algorithms
- Additional constraint types
- Performance optimizations
- More example games
- Documentation improvements 