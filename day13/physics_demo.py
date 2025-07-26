import pygame
import sys
import random
from verlet_physics import *

# -------------------------------------------------------------
#  Physics Engine Demo Game
# -------------------------------------------------------------
#  Features:
#  • Player character with physics-based movement
#  • Interactive platforms and obstacles
#  • Bouncing balls and physics objects
#  • Collision detection and response
#  • Mouse interaction for creating objects
# -------------------------------------------------------------

class PhysicsDemo:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Verlet Physics Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        # Colors
        self.BG_COLOR = (20, 20, 30)
        self.PLATFORM_COLOR = (100, 100, 150)
        self.PLAYER_COLOR = (50, 200, 50)
        self.BALL_COLOR = (200, 100, 100)
        self.ROPE_COLOR = (150, 150, 150)
        self.TEXT_COLOR = (230, 230, 230)
        
        # Physics world
        self.world = PhysicsWorld(
            gravity=Vector2(0, 800),
            bounds=(self.width, self.height)
        )
        
        # Game objects
        self.player = None
        self.player_controller = None
        self.platforms = []
        self.balls = []
        self.ropes = []
        self.selected_body = None
        self.dragging = False
        
        # Game state
        self.score = 0
        self.ball_count = 0
        
        self.setup_level()
        self.setup_ui()
    
    def setup_level(self):
        """Create the initial level layout"""
        # Create ground
        ground = create_platform(self.world, self.width // 2, self.height - 20, self.width, 40)
        self.platforms.append(ground)
        
        # Create platforms
        platform_positions = [
            (200, 600, 150, 20),
            (500, 500, 150, 20),
            (800, 400, 150, 20),
            (300, 300, 150, 20),
            (700, 200, 150, 20),
            (100, 450, 100, 20),
            (900, 550, 100, 20),
        ]
        
        for x, y, w, h in platform_positions:
            platform = create_platform(self.world, x, y, w, h)
            self.platforms.append(platform)
        
        # Create player
        self.player = create_player(self.world, 100, 100, 25)
        self.player_controller = PlayerController(self.player, speed=400, jump_force=500)
        
        # Create some initial balls
        for i in range(5):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, 200)
            ball = create_ball(self.world, x, y, random.randint(10, 20))
            self.balls.append(ball)
        
        # Create a rope
        rope = create_rope(self.world, (1000, 100), 8, 25, 0.9)
        self.ropes.append(rope)
        
        # Add collision callback
        self.world.add_collision_callback(self.on_collision)
    
    def setup_ui(self):
        """Setup UI elements"""
        self.ui_buttons = [
            {"text": "Add Ball", "rect": pygame.Rect(10, 10, 80, 30), "action": self.add_ball},
            {"text": "Add Rope", "rect": pygame.Rect(100, 10, 80, 30), "action": self.add_rope},
            {"text": "Clear", "rect": pygame.Rect(190, 10, 80, 30), "action": self.clear_objects},
        ]
    
    def add_ball(self):
        """Add a new ball at random position"""
        x = random.randint(50, self.width - 50)
        y = random.randint(50, 200)
        ball = create_ball(self.world, x, y, random.randint(10, 20))
        self.balls.append(ball)
        self.ball_count += 1
    
    def add_rope(self):
        """Add a new rope at random position"""
        x = random.randint(100, self.width - 100)
        y = random.randint(50, 200)
        rope = create_rope(self.world, (x, y), random.randint(5, 10), 20, 0.8)
        self.ropes.append(rope)
    
    def clear_objects(self):
        """Clear all dynamic objects except player"""
        for ball in self.balls[:]:
            self.world.remove_body(ball)
            self.balls.remove(ball)
        
        for rope in self.ropes[:]:
            self.world.remove_body(rope)
            self.ropes.remove(rope)
        
        self.ball_count = 0
    
    def on_collision(self, body1, body2):
        """Handle collision events"""
        # Check if player collided with a ball
        if body1 == self.player and body2 in self.balls:
            self.score += 10
        elif body2 == self.player and body1 in self.balls:
            self.score += 10
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check UI buttons
                    for button in self.ui_buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            button["action"]()
                            break
                    else:
                        # Check if clicking on a body
                        self.selected_body = self.get_body_at_pos(mouse_pos)
                        if self.selected_body:
                            self.dragging = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    self.selected_body = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.selected_body:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.selected_body.body_type == BodyType.DYNAMIC:
                        # Apply force to move the body
                        center = self.selected_body.get_center()
                        force = Vector2(mouse_pos[0] - center.x, mouse_pos[1] - center.y) * 10
                        self.selected_body.apply_force_at_point(force, center)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_level()
                elif event.key == pygame.K_SPACE:
                    self.add_ball()
        
        return True
    
    def get_body_at_pos(self, pos):
        """Get the body at a specific position"""
        for body in self.world.bodies:
            if not body.active:
                continue
            
            bounds = self.world.get_body_bounds(body)
            if bounds[0] <= pos[0] <= bounds[2] and bounds[1] <= pos[1] <= bounds[3]:
                return body
        return None
    
    def reset_level(self):
        """Reset the level to initial state"""
        # Remove all dynamic bodies
        for body in self.world.dynamic_bodies[:]:
            self.world.remove_body(body)
        
        # Clear lists
        self.balls.clear()
        self.ropes.clear()
        
        # Reset player
        self.player = create_player(self.world, 100, 100, 25)
        self.player_controller = PlayerController(self.player, speed=400, jump_force=500)
        
        # Recreate initial objects
        for i in range(5):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, 200)
            ball = create_ball(self.world, x, y, random.randint(10, 20))
            self.balls.append(ball)
        
        rope = create_rope(self.world, (1000, 100), 8, 25, 0.9)
        self.ropes.append(rope)
        
        self.score = 0
        self.ball_count = 5
    
    def update(self, dt):
        """Update game logic"""
        # Update physics world
        self.world.update(dt)
        
        # Update player controller
        keys = pygame.key.get_pressed()
        self.player_controller.handle_input(keys, dt)
        self.player_controller.update(dt)
        
        # Update ball count
        self.ball_count = len(self.balls)
    
    def render(self):
        """Render the game"""
        self.screen.fill(self.BG_COLOR)
        
        # Render platforms
        for platform in self.platforms:
            self.render_body(platform, self.PLATFORM_COLOR)
        
        # Render ropes
        for rope in self.ropes:
            self.render_body(rope, self.ROPE_COLOR, draw_nodes=True)
        
        # Render balls
        for ball in self.balls:
            self.render_body(ball, self.BALL_COLOR)
        
        # Render player
        if self.player:
            self.render_body(self.player, self.PLAYER_COLOR)
        
        # Render UI
        self.render_ui()
        
        pygame.display.flip()
    
    def render_body(self, body, color, draw_nodes=False):
        """Render a physics body"""
        if not body.active or not body.nodes:
            return
        
        # Draw edges/constraints
        for constraint in body.constraints:
            if isinstance(constraint, DistanceConstraint):
                start_pos = (int(constraint.a.pos.x), int(constraint.a.pos.y))
                end_pos = (int(constraint.b.pos.x), int(constraint.b.pos.y))
                pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
        
        # Draw nodes
        if draw_nodes:
            for node in body.nodes:
                pos = (int(node.pos.x), int(node.pos.y))
                pygame.draw.circle(self.screen, color, pos, 3)
        
        # Highlight selected body
        if body == self.selected_body:
            center = body.get_center()
            pygame.draw.circle(self.screen, (255, 255, 0), 
                             (int(center.x), int(center.y)), 15, 2)
    
    def render_ui(self):
        """Render UI elements"""
        # Draw buttons
        for button in self.ui_buttons:
            pygame.draw.rect(self.screen, (60, 60, 80), button["rect"])
            pygame.draw.rect(self.screen, (100, 100, 120), button["rect"], 2)
            
            text = self.font.render(button["text"], True, self.TEXT_COLOR)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        # Draw info text
        info_texts = [
            f"Score: {self.score}",
            f"Balls: {self.ball_count}",
            f"Ropes: {len(self.ropes)}",
            "Controls: WASD/Arrows to move, SPACE to jump",
            "Click and drag objects, R to reset",
            "Mouse: Create balls/ropes with buttons"
        ]
        
        y_offset = 50
        for text_str in info_texts:
            text = self.font.render(text_str, True, self.TEXT_COLOR)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            running = self.handle_events()
            self.update(dt)
            self.render()

def main():
    demo = PhysicsDemo()
    demo.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 