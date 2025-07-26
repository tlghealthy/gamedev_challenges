# Position-Based Dynamics Physics Engine for Pygame

A lightweight, reusable physics engine for pygame prototypes that uses position-based dynamics for stable and controllable physics simulation. Perfect for games with less than 200 physics objects.

## Features

- **Position-Based Dynamics**: Stable physics simulation using constraint solving
- **Soft Ropes**: Realistic rope simulation with adjustable stiffness and damping
- **Rigid Bodies**: Create rigid objects from particle configurations
- **Distance Constraints**: Connect particles with customizable stiffness
- **Collision Detection**: Particle-particle and boundary collision handling
- **Configurable**: All physics parameters adjustable via `settings.json`
- **Lightweight**: Optimized for small-scale simulations (< 200 objects)
- **Interactive**: Built-in mouse interaction and particle manipulation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the demo:
```bash
python demo.py
```

## Quick Start

```python
import pygame
from physics_engine import PhysicsEngine

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 600))
physics = PhysicsEngine()
physics.set_bounds(0, 0, 800, 600)

# Create a rope
rope_particles = physics.add_rope(
    start_pos=(100, 50),
    end_pos=(100, 200),
    segments=10,
    stiffness=0.7
)
rope_particles[0].pinned = True  # Pin the top

# Create a rigid square
square_positions = [
    (300, 150), (340, 150), (340, 190), (300, 190)
]
physics.add_rigid_body(square_positions)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000.0
    
    # Update physics
    physics.update(dt)
    
    # Render
    screen.fill((30, 30, 30))
    physics.render(screen)
    pygame.display.flip()
```

## API Reference

### PhysicsEngine

Main physics engine class that manages all particles and constraints.

#### Methods

- `add_particle(x, y, mass=None, radius=None)` → Particle
  - Add a free particle to the world
  
- `add_rope(start_pos, end_pos, segments, stiffness=None, damping=None)` → List[Particle]
  - Create a rope between two points
  
- `add_rigid_body(positions, stiffness=None, damping=None)` → List[Particle]
  - Create a rigid body from particle positions
  
- `add_distance_constraint(p1, p2, stiffness=None, damping=None)`
  - Connect two particles with a distance constraint
  
- `set_bounds(left, top, right, bottom)`
  - Set collision boundaries
  
- `update(dt)`
  - Update physics simulation
  
- `render(screen)`
  - Render all physics objects

### Particle

Represents a physics particle with position, velocity, and mass.

#### Properties

- `position`: Current position (numpy array)
- `velocity`: Current velocity (numpy array)
- `mass`: Particle mass
- `radius`: Collision radius
- `pinned`: Whether particle is fixed in place

### Constraint Types

#### DistanceConstraint
Connects two particles with a fixed distance.

#### RopeConstraint
Creates a chain of particles forming a rope.

#### RigidBodyConstraint
Creates a rigid body from multiple particles.

## Configuration

All physics parameters are configurable in `settings.json`:

```json
{
  "physics": {
    "gravity": [0, 980],
    "substeps": 3,
    "iterations": 2,
    "damping": 0.98,
    "friction": 0.3,
    "restitution": 0.5
  },
  "constraints": {
    "rope": {
      "default_stiffness": 0.8,
      "default_damping": 0.1
    },
    "rigid": {
      "default_stiffness": 1.0,
      "default_damping": 0.02
    }
  }
}
```

## Demo Controls

- **Left Click**: Select and drag particles
- **Right Click**: Add new particle
- **Space**: Add rope at mouse position
- **R**: Reset demo
- **C**: Clear all objects

## Performance Tips

1. **Use appropriate substeps**: More substeps = more stable but slower
2. **Limit iterations**: 2-3 iterations usually sufficient
3. **Adjust stiffness**: Higher stiffness = more rigid but less stable
4. **Pin particles**: Pin static objects to improve performance
5. **Use appropriate damping**: Prevents excessive oscillation

## Examples

### Creating a Chain
```python
# Create a chain of connected particles
chain_particles = []
for i in range(10):
    particle = physics.add_particle(100, 50 + i * 20)
    chain_particles.append(particle)
    if i > 0:
        physics.add_distance_constraint(chain_particles[i-1], particle)
```

### Creating a Soft Body
```python
# Create a soft circular body
import math
particles = []
for i in range(8):
    angle = i * 2 * math.pi / 8
    x = 400 + 30 * math.cos(angle)
    y = 300 + 30 * math.sin(angle)
    particle = physics.add_particle(x, y)
    particles.append(particle)

# Connect all particles to form a soft body
for i in range(len(particles)):
    for j in range(i + 1, len(particles)):
        physics.add_distance_constraint(particles[i], particles[j], stiffness=0.6)
```

### Interactive Physics
```python
# Add mouse interaction
def handle_mouse():
    mouse_pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:  # Left click
        physics.add_particle(mouse_pos[0], mouse_pos[1])
```

## Physics Samples

This project includes 10 progressive samples that demonstrate different physics concepts:

### **Sample 1: Draggable Triangle Rigid Body** ✅
- **File**: `sample01_triangle.py`
- **Goal**: Basic interaction with a simple rigid body
- **Features**: 
  - Single triangle made of 3 particles with rigid constraints
  - Mouse dragging with force application
  - Basic collision with boundaries
- **Learning**: Basic rigid body creation, mouse interaction, force application

### **Sample 2: Simple Pendulum**
- **File**: `sample02_pendulum.py`
- **Goal**: Demonstrate rope constraints and gravity
- **Features**:
  - Single rope with one end pinned
  - Natural pendulum motion
  - Mouse interaction to swing the pendulum
- **Learning**: Rope constraints, pinning particles, gravity effects

### **Sample 3: Particle Fountain**
- **File**: `sample03_fountain.py`
- **Goal**: Show particle system with gravity and collision
- **Features**:
  - Particles spawning from a point
  - Gravity pulling them down
  - Collision with ground boundary
  - Particle lifetime and cleanup
- **Learning**: Particle spawning, gravity, boundary collisions, particle management

### **Sample 4: Chain of Connected Objects**
- **File**: `sample04_chain.py`
- **Goal**: Demonstrate multiple connected rigid bodies
- **Features**:
  - Chain of small rigid squares connected by distance constraints
  - Top end pinned, bottom end draggable
  - Realistic chain-like behavior
- **Learning**: Multiple rigid bodies, distance constraints between different objects

### **Sample 5: Bouncing Ball with Obstacles**
- **File**: `sample05_bouncing.py`
- **Goal**: Show collision detection and response
- **Features**:
  - Single ball with high restitution
  - Static obstacles (pinned rigid bodies)
  - Realistic bouncing behavior
- **Learning**: Collision detection, restitution, static vs dynamic objects

### **Sample 6: Cloth Simulation**
- **File**: `sample06_cloth.py`
- **Goal**: Demonstrate complex constraint networks
- **Features**:
  - Grid of particles connected by distance constraints
  - Top row pinned, rest hanging freely
  - Wind effect (random forces)
  - Realistic cloth-like behavior
- **Learning**: Grid-based constraints, wind simulation, complex constraint networks

### **Sample 7: Jelly Cube**
- **File**: `sample07_jelly.py`
- **Goal**: Show soft body physics
- **Features**:
  - Cube made of particles with softer constraints
  - Deforms on collision with ground
  - Bounces and wobbles realistically
- **Learning**: Soft body simulation, deformation, multiple constraint types

### **Sample 8: Rope Bridge**
- **File**: `sample08_bridge.py`
- **Goal**: Demonstrate structural physics
- **Features**:
  - Horizontal rope with multiple support points
  - Objects can be placed on the bridge
  - Bridge deforms under weight
  - Realistic structural behavior
- **Learning**: Structural simulation, weight distribution, multiple support points

### **Sample 9: Particle Explosion**
- **File**: `sample09_explosion.py`
- **Goal**: Show dynamic force application
- **Features**:
  - Particles start in a tight cluster
  - Explosion force applied outward
  - Particles spread and fall with gravity
  - Multiple explosion points
- **Learning**: Dynamic force application, particle clustering, explosion effects

### **Sample 10: Interactive Physics Playground**
- **File**: `sample10_playground.py`
- **Goal**: Combine all features in an interactive demo
- **Features**:
  - Multiple object types (balls, ropes, rigid bodies)
  - Mouse interaction to create and manipulate objects
  - Different materials (bouncy, heavy, light)
  - Real-time object creation and destruction
- **Learning**: Integration of all features, user interaction, material properties

### Running the Samples

To run any sample:
```bash
python sample01_triangle.py
python sample02_pendulum.py
# ... etc
```

Each sample is self-contained and demonstrates specific physics concepts while being easy to understand and modify.

## License

This project is open source and available under the MIT License. 