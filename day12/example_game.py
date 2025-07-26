import pygame
import sys
import math
from physics_engine import PhysicsEngine

class SimplePhysicsGame:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Simple Physics Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize physics
        self.physics = PhysicsEngine()
        self.physics.set_bounds(0, 0, width, height)
        
        # Game state
        self.score = 0
        self.game_time = 0
        self.targets = []
        self.player_rope = None
        
        # Setup game
        self.setup_game()
    
    def setup_game(self):
        """Setup the initial game state"""
        # Create player rope (pendulum)
        self.player_rope = self.physics.add_rope(
            start_pos=(self.width // 2, 50),
            end_pos=(self.width // 2, 200),
            segments=12,
            stiffness=0.7,
            damping=0.05
        )
        # Pin the top of the rope
        self.player_rope[0].pinned = True
        
        # Add some initial movement to make it more interesting
        if len(self.player_rope) > 1:
            self.player_rope[-1].velocity[0] = 50  # Small initial push
        
        # Create some targets (rigid bodies)
        self.create_targets()
    
    def create_targets(self):
        """Create target objects to hit"""
        target_positions = [
            (100, 520), (200, 520), (300, 520), (400, 520), (500, 520), (600, 520), (700, 520)
        ]
        
        for pos in target_positions:
            # Create a small rigid square as target
            square_size = 25
            square_positions = [
                (pos[0] - square_size//2, pos[1] - square_size//2),
                (pos[0] + square_size//2, pos[1] - square_size//2),
                (pos[0] + square_size//2, pos[1] + square_size//2),
                (pos[0] - square_size//2, pos[1] + square_size//2),
            ]
            target_particles = self.physics.add_rigid_body(square_positions, stiffness=1.0)
            self.targets.append(target_particles)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.swing_rope(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset_game()
                elif event.key == pygame.K_r:
                    self.create_targets()
    
    def swing_rope(self, mouse_pos):
        """Apply force to the rope based on mouse position"""
        if self.player_rope:
            # Get the bottom particle of the rope
            bottom_particle = self.player_rope[-1]
            
            # Calculate direction from rope to mouse
            direction = pygame.math.Vector2(mouse_pos[0] - bottom_particle.position[0],
                                          mouse_pos[1] - bottom_particle.position[1])
            
            if direction.length() > 0:
                direction = direction.normalize()
                # Apply force to the bottom particle
                force = direction * 800
                bottom_particle.velocity[0] += force.x
                bottom_particle.velocity[1] += force.y
                
                # Also apply some force to nearby particles for more natural movement
                for i in range(max(0, len(self.player_rope) - 3), len(self.player_rope)):
                    if i < len(self.player_rope):
                        particle = self.player_rope[i]
                        factor = (i - (len(self.player_rope) - 3)) / 3.0
                        particle.velocity[0] += force.x * factor * 0.3
                        particle.velocity[1] += force.y * factor * 0.3
    
    def check_collisions(self):
        """Check for collisions between rope and targets"""
        if not self.player_rope:
            return
        
        # Get the bottom particle of the rope
        rope_end = self.player_rope[-1]
        
        for i, target in enumerate(self.targets):
            if target and target[0] in self.physics.particles:  # Check if target still exists
                for particle in target:
                    distance = math.sqrt((rope_end.position[0] - particle.position[0])**2 +
                                       (rope_end.position[1] - particle.position[1])**2)
                    
                    if distance < rope_end.radius + particle.radius:
                        # Collision detected - remove target and add score
                        self.score += 10
                        self.remove_target(i)
                        break
    
    def remove_target(self, target_index):
        """Remove a target from the game"""
        if 0 <= target_index < len(self.targets):
            target_particles = self.targets[target_index]
            
            # Remove particles from physics engine
            for particle in target_particles:
                if particle in self.physics.particles:
                    self.physics.particles.remove(particle)
            
            # Remove target from list
            self.targets.pop(target_index)
    
    def reset_game(self):
        """Reset the game state"""
        self.score = 0
        self.game_time = 0
        
        # Clear all physics objects
        self.physics.particles.clear()
        self.physics.constraints.clear()
        self.targets.clear()
        
        # Recreate game objects
        self.setup_game()
    
    def draw_ui(self):
        """Draw UI elements"""
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Time
        time_text = font.render(f"Time: {int(self.game_time)}s", True, (255, 255, 255))
        self.screen.blit(time_text, (10, 50))
        
        # Instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Left Click: Swing rope",
            "Space: Reset game",
            "R: Add more targets"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (10, self.height - 80 + i * 25))
        
        # Target count
        target_text = font_small.render(f"Targets: {len(self.targets)}", True, (255, 255, 255))
        self.screen.blit(target_text, (self.width - 150, 10))
    
    def draw_targets(self):
        """Draw targets with special rendering"""
        for target in self.targets:
            if target and target[0] in self.physics.particles:
                # Draw target as a filled square
                center_x = sum(p.position[0] for p in target) / len(target)
                center_y = sum(p.position[1] for p in target) / len(target)
                size = 25  # Made slightly larger
                
                # Convert to integers for pygame drawing
                rect_x = int(center_x - size//2)
                rect_y = int(center_y - size//2)
                
                # Draw filled square
                pygame.draw.rect(self.screen, (255, 100, 100), 
                               (rect_x, rect_y, size, size))
                # Draw border
                pygame.draw.rect(self.screen, (255, 255, 255), 
                               (rect_x, rect_y, size, size), 3)
                
                # Draw a small cross in the center
                cross_size = 5
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (rect_x + size//2 - cross_size, rect_y + size//2),
                               (rect_x + size//2 + cross_size, rect_y + size//2), 2)
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (rect_x + size//2, rect_y + size//2 - cross_size),
                               (rect_x + size//2, rect_y + size//2 + cross_size), 2)
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.game_time += dt
            
            self.handle_events()
            
            # Update physics
            self.physics.update(dt)
            
            # Check collisions
            self.check_collisions()
            
            # Render
            self.screen.fill((30, 30, 50))
            
            # Draw physics objects
            self.physics.render(self.screen)
            
            # Draw targets with special rendering
            self.draw_targets()
            
            # Draw UI
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SimplePhysicsGame()
    game.run() 