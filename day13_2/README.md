# Phase 1 Physics Engine - Position Based Dynamics (PBD)

This is a baseline Position Based Dynamics (PBD) physics engine that satisfies all Phase 1 requirements.

## Phase 1 Requirements

### Core Goal
Mini-engine with basic PBD implementation

### Must-have Deliverables
- ✅ **World, Node, Edge classes** - Implemented with proper structure
- ✅ **Fixed Δt accumulator (1/120 s)** - Implemented with time accumulator pattern
- ✅ **Point-edge contact projection (no broad-phase)** - Implemented in `_solve_collisions()`

### Recommended Test Focus
- ✅ **Rope droop height vs analytical catenary** - Test implemented in `test_phase1.py`
- ✅ **Box stack of 3×3 survives 5s without exploding** - Stability test implemented

## Implementation Details

### Fixed Timestep Implementation
The engine uses a fixed timestep of 1/120 seconds (120 Hz) with an accumulator pattern:

```python
def step(self, dt: float):
    self.accumulator += dt
    while self.accumulator >= self.fixed_dt:
        self._step_fixed(self.fixed_dt)
        self.accumulator -= self.fixed_dt
```

This ensures consistent physics simulation regardless of frame rate variations.

### Core Classes

#### Node
- Represents a point mass with position and previous position
- Supports locked nodes (immovable)
- Implements Verlet integration

#### Edge
- Represents a distance constraint between two nodes
- Implements constraint satisfaction with stiffness parameter
- Maintains rest length for proper behavior

#### World
- Manages all nodes and edges
- Handles integration and constraint solving
- Implements point-edge collision detection
- Provides factory methods for common shapes (rope, box, capsule)

### Collision Detection
- Point-edge contact projection without broad-phase optimization
- Uses closest point on line segment calculation
- Applies collision response with proper mass distribution

## Usage

### Basic Setup
```python
import pygame
from physics_engine import World

world = World(gravity=(0, 600), fixed_dt=1/120.0)
```

### Creating Objects
```python
# Create a rope
rope_nodes = world.rope((150, 120), seg_len=40, count=12, k=0.8)

# Create a box
box_nodes = world.box((350, 120), 80, 80, k=0.9)

# Create a 3x3 stack
for r in range(3):
    for c in range(3):
        world.box((350 + c*120, 120 + r*120), 80, 80)
```

### Simulation Loop
```python
while running:
    dt = clock.tick(60) / 1000
    world.step(dt)  # Fixed timestep handled internally
    world.debug_render(screen)
```

## Testing

Run the test suite to verify Phase 1 requirements:

```bash
python test_phase1.py
```

This will:
1. Show a visual demonstration
2. Test rope catenary behavior
3. Test box stack stability for 5 seconds
4. Report pass/fail status for all requirements

## Performance Characteristics

- **Fixed timestep**: 120 Hz (1/120 seconds)
- **Constraint iterations**: 5 (configurable)
- **Collision detection**: O(n×e) where n=nodes, e=edges
- **Memory efficient**: Uses pygame.Vector2 for positions

## Next Steps (Phase 2+)

This baseline implementation provides the foundation for:
- Broad-phase collision detection
- More complex constraints
- Performance optimizations
- Additional shape types 