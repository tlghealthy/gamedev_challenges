import math
import pygame
from physics_engine import PhysicsEngine
from typing import List, Tuple

def create_circle(physics: PhysicsEngine, center: Tuple[float, float], radius: float, 
                  segments: int = 8, stiffness: float = 0.8) -> List:
    """Create a circular soft body"""
    particles = []
    
    for i in range(segments):
        angle = i * 2 * math.pi / segments
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        particle = physics.add_particle(x, y)
        particles.append(particle)
    
    # Connect all particles to form a circle
    for i in range(segments):
        next_i = (i + 1) % segments
        physics.add_distance_constraint(particles[i], particles[next_i], stiffness=stiffness)
    
    return particles

def create_rectangle(physics: PhysicsEngine, center: Tuple[float, float], width: float, 
                     height: float, stiffness: float = 1.0) -> List:
    """Create a rectangular rigid body"""
    half_w, half_h = width / 2, height / 2
    positions = [
        (center[0] - half_w, center[1] - half_h),
        (center[0] + half_w, center[1] - half_h),
        (center[0] + half_w, center[1] + half_h),
        (center[0] - half_w, center[1] + half_h),
    ]
    return physics.add_rigid_body(positions, stiffness=stiffness)

def create_triangle(physics: PhysicsEngine, center: Tuple[float, float], size: float, 
                    stiffness: float = 1.0) -> List:
    """Create a triangular rigid body"""
    positions = [
        (center[0], center[1] - size),
        (center[0] - size, center[1] + size),
        (center[0] + size, center[1] + size),
    ]
    return physics.add_rigid_body(positions, stiffness=stiffness)

def create_chain(physics: PhysicsEngine, start_pos: Tuple[float, float], 
                 end_pos: Tuple[float, float], segments: int, stiffness: float = 0.8) -> List:
    """Create a chain between two points"""
    particles = []
    
    for i in range(segments + 1):
        t = i / segments
        x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
        y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
        particle = physics.add_particle(x, y)
        particles.append(particle)
        
        if i > 0:
            physics.add_distance_constraint(particles[i-1], particle, stiffness=stiffness)
    
    return particles

def create_soft_body_grid(physics: PhysicsEngine, center: Tuple[float, float], 
                          width: int, height: int, spacing: float, stiffness: float = 0.6) -> List:
    """Create a soft body grid (like cloth)"""
    particles = []
    
    # Create particles in a grid
    for y in range(height):
        row = []
        for x in range(width):
            pos_x = center[0] + (x - width//2) * spacing
            pos_y = center[1] + (y - height//2) * spacing
            particle = physics.add_particle(pos_x, pos_y)
            row.append(particle)
        particles.append(row)
    
    # Connect particles with distance constraints
    for y in range(height):
        for x in range(width):
            current = particles[y][x]
            
            # Connect to right neighbor
            if x + 1 < width:
                physics.add_distance_constraint(current, particles[y][x+1], stiffness=stiffness)
            
            # Connect to bottom neighbor
            if y + 1 < height:
                physics.add_distance_constraint(current, particles[y+1][x], stiffness=stiffness)
            
            # Connect diagonally (optional)
            if x + 1 < width and y + 1 < height:
                physics.add_distance_constraint(current, particles[y+1][x+1], stiffness=stiffness * 0.7)
    
    return particles

def apply_force_to_particle(particle, force: Tuple[float, float]):
    """Apply a force to a particle"""
    particle.velocity[0] += force[0]
    particle.velocity[1] += force[1]

def apply_force_to_body(particles: List, force: Tuple[float, float]):
    """Apply a force to all particles in a body"""
    for particle in particles:
        apply_force_to_particle(particle, force)

def apply_impulse_to_particle(particle, impulse: Tuple[float, float]):
    """Apply an impulse to a particle"""
    particle.velocity[0] += impulse[0] * particle.inv_mass
    particle.velocity[1] += impulse[1] * particle.inv_mass

def create_explosion(physics: PhysicsEngine, center: Tuple[float, float], 
                     radius: float, force: float, particles: List):
    """Create an explosion effect at a point"""
    for particle in particles:
        if particle in physics.particles:
            dx = particle.position[0] - center[0]
            dy = particle.position[1] - center[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < radius and distance > 0:
                # Normalize direction and apply force
                direction_x = dx / distance
                direction_y = dy / distance
                
                # Force decreases with distance
                force_magnitude = force * (1 - distance / radius)
                apply_force_to_particle(particle, (direction_x * force_magnitude, direction_y * force_magnitude))

def create_wind_effect(physics: PhysicsEngine, wind_force: Tuple[float, float], 
                      affected_particles: List = None):
    """Apply wind effect to particles"""
    if affected_particles is None:
        affected_particles = physics.particles
    
    for particle in affected_particles:
        if not particle.pinned:
            apply_force_to_particle(particle, wind_force)

def pin_particles(particles: List, pin_indices: List[int]):
    """Pin specific particles in a list"""
    for i in pin_indices:
        if 0 <= i < len(particles):
            particles[i].pinned = True

def unpin_particles(particles: List, unpin_indices: List[int]):
    """Unpin specific particles in a list"""
    for i in unpin_indices:
        if 0 <= i < len(particles):
            particles[i].pinned = False

def get_center_of_mass(particles: List) -> Tuple[float, float]:
    """Calculate center of mass of a group of particles"""
    if not particles:
        return (0, 0)
    
    total_mass = sum(p.mass for p in particles)
    if total_mass == 0:
        return (0, 0)
    
    center_x = sum(p.position[0] * p.mass for p in particles) / total_mass
    center_y = sum(p.position[1] * p.mass for p in particles) / total_mass
    
    return (center_x, center_y)

def get_bounding_box(particles: List) -> Tuple[float, float, float, float]:
    """Get bounding box of a group of particles"""
    if not particles:
        return (0, 0, 0, 0)
    
    min_x = min(p.position[0] - p.radius for p in particles)
    max_x = max(p.position[0] + p.radius for p in particles)
    min_y = min(p.position[1] - p.radius for p in particles)
    max_y = max(p.position[1] + p.radius for p in particles)
    
    return (min_x, min_y, max_x, max_y)

def is_particle_in_bounds(particle, bounds: Tuple[float, float, float, float]) -> bool:
    """Check if a particle is within given bounds"""
    left, top, right, bottom = bounds
    x, y = particle.position[0], particle.position[1]
    radius = particle.radius
    
    return (left <= x - radius and x + radius <= right and 
            top <= y - radius and y + radius <= bottom)

def remove_particles_outside_bounds(physics: PhysicsEngine, bounds: Tuple[float, float, float, float]):
    """Remove particles that are outside the given bounds"""
    particles_to_remove = []
    
    for particle in physics.particles:
        if not is_particle_in_bounds(particle, bounds):
            particles_to_remove.append(particle)
    
    for particle in particles_to_remove:
        physics.particles.remove(particle)

def create_spring(physics: PhysicsEngine, p1, p2, rest_length: float = None, 
                  stiffness: float = 0.8, damping: float = 0.1):
    """Create a spring between two particles"""
    if rest_length is None:
        rest_length = math.sqrt((p2.position[0] - p1.position[0])**2 + 
                               (p2.position[1] - p1.position[1])**2)
    
    physics.add_distance_constraint(p1, p2, stiffness=stiffness, damping=damping)
    return rest_length 