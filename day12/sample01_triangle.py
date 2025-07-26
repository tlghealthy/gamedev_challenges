import pygame
import sys
import math
import numpy as np
from physics_engine import PhysicsEngine

class TrianglePhysicsDemo:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sample 1: Draggable Triangle Rigid Body")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize physics with very low gravity for stable triangle
        self.physics = PhysicsEngine()
        self.physics.set_bounds(0, 0, width, height)
        # Very low gravity to prevent stretching
        self.physics.gravity = np.array([0, 50], dtype=np.float32)  # Minimal gravity
        # Increase damping to reduce oscillation
        self.physics.damping = 0.95
        
        # Mouse interaction state
        self.dragging = False
        self.drag_particle = None
        self.drag_offset = (0, 0)
        
        # Setup the triangle
        self.setup_triangle()
    
    def setup_triangle(self):
        """Create a triangle rigid body in the center of the screen"""
        # Triangle parameters
        center_x = self.width // 2
        center_y = self.height // 2
        size = 60  # Size of the triangle
        
        # Calculate triangle vertices (equilateral triangle)
        triangle_positions = [
            (center_x, center_y - size//2),  # Top vertex
            (center_x - size//2, center_y + size//2),  # Bottom left
            (center_x + size//2, center_y + size//2),  # Bottom right
        ]
        
        # Create the triangle as a rigid body with higher stiffness for stability
        self.triangle_particles = self.physics.add_rigid_body(
            triangle_positions,
            stiffness=1.0,  # Maximum stiffness to maintain shape
            damping=0.1     # Higher damping to reduce oscillation
        )
        
        # Don't give initial velocity - let it start stationary
        # The particles will move naturally due to gravity and interaction
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.start_drag(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.end_drag()
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.update_drag(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_triangle()
                elif event.key == pygame.K_SPACE:
                    self.add_impulse()
    
    def start_drag(self, mouse_pos):
        """Start dragging a particle"""
        # Find the closest particle to the mouse
        closest_particle = None
        closest_distance = float('inf')
        
        for particle in self.triangle_particles:
            distance = math.sqrt((mouse_pos[0] - particle.position[0])**2 + 
                               (mouse_pos[1] - particle.position[1])**2)
            if distance < closest_distance and distance < 30:  # Within 30 pixels
                closest_distance = distance
                closest_particle = particle
        
        if closest_particle:
            self.dragging = True
            self.drag_particle = closest_particle
            self.drag_offset = (mouse_pos[0] - closest_particle.position[0],
                              mouse_pos[1] - closest_particle.position[1])
    
    def update_drag(self, mouse_pos):
        """Update particle position while dragging"""
        if self.drag_particle:
            # Calculate target position
            target_x = mouse_pos[0] - self.drag_offset[0]
            target_y = mouse_pos[1] - self.drag_offset[1]
            
            # Apply force towards target position (gentler spring-like behavior)
            current_pos = self.drag_particle.position
            force_x = (target_x - current_pos[0]) * 5  # Reduced spring constant
            force_y = (target_y - current_pos[1]) * 5
            
            # Apply force to the particle (gentler)
            self.drag_particle.velocity[0] += force_x * 0.016  # dt approximation
            self.drag_particle.velocity[1] += force_y * 0.016
    
    def end_drag(self):
        """End dragging"""
        self.dragging = False
        self.drag_particle = None
    
    def reset_triangle(self):
        """Reset the triangle to its initial position"""
        # Clear existing triangle
        for particle in self.triangle_particles:
            if particle in self.physics.particles:
                self.physics.particles.remove(particle)
        
        # Clear constraints
        self.physics.constraints.clear()
        
        # Recreate triangle
        self.setup_triangle()
    
    def add_impulse(self):
        """Add a random impulse to the triangle"""
        for particle in self.triangle_particles:
            # Random impulse in all directions (gentler)
            impulse_x = (np.random.random() - 0.5) * 100  # Reduced from 200
            impulse_y = (np.random.random() - 0.5) * 100
            particle.velocity[0] += impulse_x
            particle.velocity[1] += impulse_y
    
    def draw_ui(self):
        """Draw UI elements"""
        font = pygame.font.Font(None, 36)
        
        # Title
        title_text = font.render("Draggable Triangle Rigid Body", True, (255, 255, 255))
        self.screen.blit(title_text, (10, 10))
        
        # Instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Left Click + Drag: Move triangle",
            "R: Reset triangle position",
            "Space: Add random impulse",
            "Triangle bounces off boundaries"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (10, self.height - 100 + i * 25))
        
        # Physics info
        if self.triangle_particles:
            center_x = sum(p.position[0] for p in self.triangle_particles) / len(self.triangle_particles)
            center_y = sum(p.position[1] for p in self.triangle_particles) / len(self.triangle_particles)
            velocity = sum(math.sqrt(p.velocity[0]**2 + p.velocity[1]**2) for p in self.triangle_particles) / len(self.triangle_particles)
            
            info_text = font_small.render(f"Center: ({int(center_x)}, {int(center_y)}) | Speed: {velocity:.1f}", True, (255, 255, 255))
            self.screen.blit(info_text, (10, 50))
    
    def draw_triangle_fill(self):
        """Draw the triangle with a filled color"""
        if len(self.triangle_particles) >= 3:
            # Get triangle vertices
            points = [(int(p.position[0]), int(p.position[1])) for p in self.triangle_particles]
            
            # Draw filled triangle
            pygame.draw.polygon(self.screen, (100, 150, 255), points)
            
            # Draw triangle border
            pygame.draw.polygon(self.screen, (255, 255, 255), points, 3)
            
            # Draw particle centers
            for particle in self.triangle_particles:
                pos = (int(particle.position[0]), int(particle.position[1]))
                pygame.draw.circle(self.screen, (255, 255, 255), pos, 4)
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            
            # Update physics
            self.physics.update(dt)
            
            # Render
            self.screen.fill((30, 30, 50))
            
            # Draw physics objects (constraints)
            self.physics.render(self.screen)
            
            # Draw filled triangle
            self.draw_triangle_fill()
            
            # Draw UI
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    demo = TrianglePhysicsDemo()
    demo.run() 