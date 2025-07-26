import pygame
import sys
from physics_engine import PhysicsEngine
import math

class PhysicsDemo:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Position-Based Dynamics Physics Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize physics engine
        self.physics = PhysicsEngine()
        self.physics.set_bounds(0, 0, width, height)
        
        # Demo objects
        self.setup_demo()
        
        # Mouse interaction
        self.selected_particle = None
        self.mouse_pos = (0, 0)
    
    def setup_demo(self):
        """Setup demo physics objects"""
        # Create a soft rope
        rope_particles = self.physics.add_rope(
            start_pos=(100, 50),
            end_pos=(100, 200),
            segments=10,
            stiffness=0.7,
            damping=0.1
        )
        # Pin the top particle
        rope_particles[0].pinned = True
        
        # Create a rigid square
        square_size = 40
        square_center = (300, 150)
        square_positions = [
            (square_center[0] - square_size//2, square_center[1] - square_size//2),
            (square_center[0] + square_size//2, square_center[1] - square_size//2),
            (square_center[0] + square_size//2, square_center[1] + square_size//2),
            (square_center[0] - square_size//2, square_center[1] + square_size//2),
        ]
        self.physics.add_rigid_body(square_positions, stiffness=1.0, damping=0.02)
        
        # Create a triangle
        triangle_center = (500, 150)
        triangle_size = 30
        triangle_positions = [
            (triangle_center[0], triangle_center[1] - triangle_size),
            (triangle_center[0] - triangle_size, triangle_center[1] + triangle_size),
            (triangle_center[0] + triangle_size, triangle_center[1] + triangle_size),
        ]
        self.physics.add_rigid_body(triangle_positions, stiffness=0.9, damping=0.05)
        
        # Create some free particles
        for i in range(5):
            x = 200 + i * 50
            y = 300
            particle = self.physics.add_particle(x, y, mass=2.0, radius=8)
        
        # Create a chain of connected particles
        chain_start = (600, 100)
        for i in range(8):
            particle = self.physics.add_particle(chain_start[0], chain_start[1] + i * 20, mass=1.5, radius=6)
            if i > 0:
                self.physics.add_distance_constraint(
                    self.physics.particles[-2], 
                    self.physics.particles[-1],
                    stiffness=0.8,
                    damping=0.1
                )
        
        # Pin the first chain particle
        self.physics.particles[-8].pinned = True
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.select_particle(event.pos)
                elif event.button == 3:  # Right click
                    self.add_particle_at_mouse(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.selected_particle = None
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if self.selected_particle:
                    self.selected_particle.position[0] = event.pos[0]
                    self.selected_particle.position[1] = event.pos[1]
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.add_rope_at_mouse()
                elif event.key == pygame.K_r:
                    self.reset_demo()
                elif event.key == pygame.K_c:
                    self.clear_all()
    
    def select_particle(self, pos):
        """Select particle closest to mouse position"""
        min_distance = float('inf')
        closest_particle = None
        
        for particle in self.physics.particles:
            distance = math.sqrt((particle.position[0] - pos[0])**2 + 
                               (particle.position[1] - pos[1])**2)
            if distance < particle.radius + 10 and distance < min_distance:
                min_distance = distance
                closest_particle = particle
        
        self.selected_particle = closest_particle
    
    def add_particle_at_mouse(self, pos):
        """Add a new particle at mouse position"""
        self.physics.add_particle(pos[0], pos[1], mass=1.0, radius=6)
    
    def add_rope_at_mouse(self):
        """Add a rope at mouse position"""
        rope_particles = self.physics.add_rope(
            start_pos=(self.mouse_pos[0], self.mouse_pos[1] - 50),
            end_pos=(self.mouse_pos[0], self.mouse_pos[1] + 50),
            segments=8,
            stiffness=0.6,
            damping=0.15
        )
        # Pin the top particle
        rope_particles[0].pinned = True
    
    def reset_demo(self):
        """Reset the demo to initial state"""
        self.physics.particles.clear()
        self.physics.constraints.clear()
        self.setup_demo()
    
    def clear_all(self):
        """Clear all physics objects"""
        self.physics.particles.clear()
        self.physics.constraints.clear()
    
    def draw_ui(self):
        """Draw UI elements"""
        font = pygame.font.Font(None, 24)
        
        # Instructions
        instructions = [
            "Left Click: Select/Drag particles",
            "Right Click: Add particle",
            "Space: Add rope at mouse",
            "R: Reset demo",
            "C: Clear all"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (255, 255, 255))
            self.screen.blit(text, (10, 10 + i * 25))
        
        # Particle count
        particle_count = font.render(f"Particles: {len(self.physics.particles)}", True, (255, 255, 255))
        self.screen.blit(particle_count, (10, self.height - 30))
        
        # Mouse position
        mouse_text = font.render(f"Mouse: {self.mouse_pos}", True, (255, 255, 255))
        self.screen.blit(mouse_text, (200, self.height - 30))
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds
            
            self.handle_events()
            
            # Update physics
            self.physics.update(dt)
            
            # Render
            self.screen.fill((30, 30, 30))
            self.physics.render(self.screen)
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    demo = PhysicsDemo()
    demo.run() 