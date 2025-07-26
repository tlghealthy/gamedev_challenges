import pygame
import json
import math
from typing import List, Tuple, Optional
import numpy as np

class Particle:
    def __init__(self, x: float, y: float, mass: float = 1.0, radius: float = 5.0):
        self.position = np.array([x, y], dtype=np.float32)
        self.previous_position = np.array([x, y], dtype=np.float32)
        self.velocity = np.array([0.0, 0.0], dtype=np.float32)
        self.mass = mass
        self.radius = radius
        self.inv_mass = 1.0 / mass if mass > 0 else 0.0
        self.pinned = False
    
    def update_velocity(self, dt: float):
        """Update velocity using Verlet integration"""
        if not self.pinned:
            self.velocity = (self.position - self.previous_position) / dt
    
    def predict_position(self, dt: float, gravity: np.ndarray):
        """Predict next position using Verlet integration"""
        if not self.pinned:
            self.previous_position = self.position.copy()
            self.position += self.velocity + gravity * dt * dt

class Constraint:
    def __init__(self, stiffness: float = 1.0, damping: float = 0.0):
        self.stiffness = stiffness
        self.damping = damping

class DistanceConstraint(Constraint):
    def __init__(self, p1: Particle, p2: Particle, distance: float, 
                 stiffness: float = 1.0, damping: float = 0.0):
        super().__init__(stiffness, damping)
        self.p1 = p1
        self.p2 = p2
        self.rest_distance = distance
    
    def solve(self):
        """Solve distance constraint using position-based dynamics"""
        if self.p1.pinned and self.p2.pinned:
            return
        
        delta = self.p2.position - self.p1.position
        distance = np.linalg.norm(delta)
        
        if distance < 1e-6:
            return
        
        # Calculate constraint violation
        violation = distance - self.rest_distance
        correction = delta * (violation / distance) * self.stiffness
        
        # Apply correction based on inverse masses
        total_inv_mass = self.p1.inv_mass + self.p2.inv_mass
        if total_inv_mass < 1e-6:
            return
        
        p1_correction = correction * (self.p1.inv_mass / total_inv_mass)
        p2_correction = correction * (self.p2.inv_mass / total_inv_mass)
        
        if not self.p1.pinned:
            self.p1.position -= p1_correction
        if not self.p2.pinned:
            self.p2.position += p2_correction

class RopeConstraint(Constraint):
    def __init__(self, particles: List[Particle], stiffness: float = 0.8, 
                 damping: float = 0.1, max_stretch: float = 1.5):
        super().__init__(stiffness, damping)
        self.particles = particles
        self.max_stretch = max_stretch
        self.distance_constraints = []
        
        # Create distance constraints between consecutive particles
        for i in range(len(particles) - 1):
            distance = np.linalg.norm(particles[i+1].position - particles[i].position)
            constraint = DistanceConstraint(particles[i], particles[i+1], distance, stiffness, damping)
            self.distance_constraints.append(constraint)
    
    def solve(self):
        """Solve all rope constraints"""
        for constraint in self.distance_constraints:
            constraint.solve()

class RigidBodyConstraint(Constraint):
    def __init__(self, particles: List[Particle], stiffness: float = 1.0, 
                 damping: float = 0.02):
        super().__init__(stiffness, damping)
        self.particles = particles
        self.distance_constraints = []
        
        # Create distance constraints between all particle pairs
        for i in range(len(particles)):
            for j in range(i + 1, len(particles)):
                distance = np.linalg.norm(particles[j].position - particles[i].position)
                constraint = DistanceConstraint(particles[i], particles[j], distance, stiffness, damping)
                self.distance_constraints.append(constraint)
    
    def solve(self):
        """Solve all rigid body constraints"""
        for constraint in self.distance_constraints:
            constraint.solve()

class PhysicsEngine:
    def __init__(self, settings_file: str = "settings.json"):
        with open(settings_file, 'r') as f:
            self.settings = json.load(f)
        
        self.particles: List[Particle] = []
        self.constraints: List[Constraint] = []
        self.gravity = np.array(self.settings["physics"]["gravity"], dtype=np.float32)
        self.substeps = self.settings["physics"]["substeps"]
        self.iterations = self.settings["physics"]["iterations"]
        self.damping = self.settings["physics"]["damping"]
        self.friction = self.settings["physics"]["friction"]
        self.restitution = self.settings["physics"]["restitution"]
        
        # Collision boundaries
        self.bounds = None
    
    def add_particle(self, x: float, y: float, mass: float = None, radius: float = None) -> Particle:
        """Add a particle to the physics world"""
        if mass is None:
            mass = self.settings["particles"]["default_mass"]
        if radius is None:
            radius = self.settings["particles"]["default_radius"]
        
        particle = Particle(x, y, mass, radius)
        self.particles.append(particle)
        return particle
    
    def add_rope(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], 
                 segments: int, stiffness: float = None, damping: float = None) -> List[Particle]:
        """Create a rope between two points"""
        if stiffness is None:
            stiffness = self.settings["constraints"]["rope"]["default_stiffness"]
        if damping is None:
            damping = self.settings["constraints"]["rope"]["default_damping"]
        
        particles = []
        for i in range(segments + 1):
            t = i / segments
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            particle = self.add_particle(x, y)
            particles.append(particle)
        
        rope = RopeConstraint(particles, stiffness, damping, 
                            self.settings["constraints"]["rope"]["max_stretch"])
        self.constraints.append(rope)
        return particles
    
    def add_rigid_body(self, positions: List[Tuple[float, float]], 
                      stiffness: float = None, damping: float = None) -> List[Particle]:
        """Create a rigid body from a list of positions"""
        if stiffness is None:
            stiffness = self.settings["constraints"]["rigid"]["default_stiffness"]
        if damping is None:
            damping = self.settings["constraints"]["rigid"]["default_damping"]
        
        particles = []
        for pos in positions:
            particle = self.add_particle(pos[0], pos[1])
            particles.append(particle)
        
        rigid_body = RigidBodyConstraint(particles, stiffness, damping)
        self.constraints.append(rigid_body)
        return particles
    
    def add_distance_constraint(self, p1: Particle, p2: Particle, 
                               stiffness: float = None, damping: float = None):
        """Add a distance constraint between two particles"""
        if stiffness is None:
            stiffness = self.settings["constraints"]["distance"]["default_stiffness"]
        if damping is None:
            damping = self.settings["constraints"]["distance"]["default_damping"]
        
        distance = np.linalg.norm(p2.position - p1.position)
        constraint = DistanceConstraint(p1, p2, distance, stiffness, damping)
        self.constraints.append(constraint)
    
    def set_bounds(self, left: float, top: float, right: float, bottom: float):
        """Set collision boundaries"""
        self.bounds = (left, top, right, bottom)
    
    def solve_collisions(self):
        """Solve particle-particle and particle-boundary collisions"""
        # Particle-particle collisions
        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                p1, p2 = self.particles[i], self.particles[j]
                delta = p2.position - p1.position
                distance = np.linalg.norm(delta)
                min_distance = p1.radius + p2.radius
                
                if distance < min_distance and distance > 1e-6:
                    # Collision detected
                    normal = delta / distance
                    penetration = min_distance - distance
                    
                    # Move particles apart
                    correction = normal * penetration * 0.5
                    if not p1.pinned:
                        p1.position -= correction
                    if not p2.pinned:
                        p2.position += correction
        
        # Boundary collisions
        if self.bounds:
            left, top, right, bottom = self.bounds
            for particle in self.particles:
                if particle.pinned:
                    continue
                
                # Left boundary
                if particle.position[0] - particle.radius < left:
                    particle.position[0] = left + particle.radius
                    particle.velocity[0] *= -self.restitution
                
                # Right boundary
                if particle.position[0] + particle.radius > right:
                    particle.position[0] = right - particle.radius
                    particle.velocity[0] *= -self.restitution
                
                # Top boundary
                if particle.position[1] - particle.radius < top:
                    particle.position[1] = top + particle.radius
                    particle.velocity[1] *= -self.restitution
                
                # Bottom boundary
                if particle.position[1] + particle.radius > bottom:
                    particle.position[1] = bottom - particle.radius
                    particle.velocity[1] *= -self.restitution
    
    def update(self, dt: float):
        """Update physics simulation"""
        dt_substep = dt / self.substeps
        
        for _ in range(self.substeps):
            # Predict positions
            for particle in self.particles:
                particle.predict_position(dt_substep, self.gravity)
            
            # Solve constraints
            for _ in range(self.iterations):
                for constraint in self.constraints:
                    constraint.solve()
                self.solve_collisions()
            
            # Update velocities and apply damping
            for particle in self.particles:
                particle.update_velocity(dt_substep)
                particle.velocity *= self.damping
    
    def render(self, screen: pygame.Surface):
        """Render all physics objects"""
        if not self.settings["rendering"]["draw_particles"]:
            return
        
        # Draw particles
        color = tuple(self.settings["rendering"]["particle_color"])
        for particle in self.particles:
            pos = (int(particle.position[0]), int(particle.position[1]))
            pygame.draw.circle(screen, color, pos, int(particle.radius))
        
        # Draw constraints
        if self.settings["rendering"]["draw_constraints"]:
            for constraint in self.constraints:
                if isinstance(constraint, DistanceConstraint):
                    color = tuple(self.settings["rendering"]["rope_color"])
                    start_pos = (int(constraint.p1.position[0]), int(constraint.p1.position[1]))
                    end_pos = (int(constraint.p2.position[0]), int(constraint.p2.position[1]))
                    pygame.draw.line(screen, color, start_pos, end_pos, 2)
                elif isinstance(constraint, RopeConstraint):
                    color = tuple(self.settings["rendering"]["rope_color"])
                    for i in range(len(constraint.particles) - 1):
                        start_pos = (int(constraint.particles[i].position[0]), 
                                   int(constraint.particles[i].position[1]))
                        end_pos = (int(constraint.particles[i+1].position[0]), 
                                 int(constraint.particles[i+1].position[1]))
                        pygame.draw.line(screen, color, start_pos, end_pos, 2)
                elif isinstance(constraint, RigidBodyConstraint):
                    color = tuple(self.settings["rendering"]["rigid_color"])
                    for i in range(len(constraint.particles)):
                        for j in range(i + 1, len(constraint.particles)):
                            start_pos = (int(constraint.particles[i].position[0]), 
                                       int(constraint.particles[i].position[1]))
                            end_pos = (int(constraint.particles[j].position[0]), 
                                     int(constraint.particles[j].position[1]))
                            pygame.draw.line(screen, color, start_pos, end_pos, 1) 