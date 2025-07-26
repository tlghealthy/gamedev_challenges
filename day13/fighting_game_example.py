import pygame
import sys
import random
import math
from verlet_physics import *

# -------------------------------------------------------------
#  Simple Fighting Game Example using Verlet Physics
# -------------------------------------------------------------
#  Features:
#  • Physics-based combat with ragdoll effects
#  • Environmental interactions and destructible objects
#  • Health and damage system
#  • Multiple attack types
#  • Arena with boundaries
# -------------------------------------------------------------

class Fighter:
    """Physics-based fighter character"""
    
    def __init__(self, world, x, y, color, controls, is_player=True):
        self.world = world
        self.color = color
        self.controls = controls
        self.is_player = is_player
        
        # Create fighter body
        self.body = RectangleBody((x, y), 30, 50, body_type=BodyType.DYNAMIC)
        self.body.material.density = 1.2
        self.body.material.friction = 0.3
        world.add_body(self.body)
        
        # Fighter stats
        self.health = 100
        self.max_health = 100
        self.attack_cooldown = 0
        self.attack_range = 40
        self.attack_damage = 20
        self.is_attacking = False
        self.attack_direction = Vector2(1, 0)
        self.last_attack_time = 0
        
        # Movement
        self.speed = 200
        self.jump_force = 400
        self.on_ground = False
        
        # Animation
        self.attack_animation = 0
        self.hit_flash = 0
    
    def update(self, dt, keys=None):
        """Update fighter logic"""
        if self.is_player and keys:
            self.handle_input(keys, dt)
        
        # Update attack cooldown
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        
        # Update attack animation
        if self.is_attacking:
            self.attack_animation += dt * 10
            if self.attack_animation >= 1.0:
                self.is_attacking = False
                self.attack_animation = 0
        
        # Update hit flash
        self.hit_flash = max(0, self.hit_flash - dt * 5)
        
        # Check if on ground
        center = self.body.get_center()
        self.on_ground = center.y > 550
    
    def handle_input(self, keys, dt):
        """Handle player input"""
        if not self.body.active:
            return
        
        # Horizontal movement
        if keys[self.controls["left"]]:
            self.body.set_velocity(Vector2(-self.speed, self.body.velocity.y))
            self.attack_direction = Vector2(-1, 0)
        elif keys[self.controls["right"]]:
            self.body.set_velocity(Vector2(self.speed, self.body.velocity.y))
            self.attack_direction = Vector2(1, 0)
        else:
            # Apply damping
            self.body.set_velocity(Vector2(self.body.velocity.x * 0.8, self.body.velocity.y))
        
        # Jumping
        if keys[self.controls["jump"]] and self.on_ground:
            self.body.apply_force_at_point(Vector2(0, -self.jump_force), self.body.get_center())
        
        # Attacking
        if keys[self.controls["attack"]] and self.attack_cooldown <= 0:
            self.attack()
    
    def attack(self):
        """Perform an attack"""
        if self.attack_cooldown > 0:
            return
        
        self.is_attacking = True
        self.attack_animation = 0
        self.attack_cooldown = 0.5
        self.last_attack_time = pygame.time.get_ticks()
        
        # Apply attack force
        attack_force = self.attack_direction * self.attack_damage * 10
        self.body.apply_force_at_point(attack_force, self.body.get_center())
    
    def take_damage(self, damage, knockback_direction):
        """Take damage and apply knockback"""
        self.health = max(0, self.health - damage)
        self.hit_flash = 1.0
        
        # Apply knockback
        knockback_force = knockback_direction * damage * 5
        self.body.apply_force_at_point(knockback_force, self.body.get_center())
        
        # Check if defeated
        if self.health <= 0:
            self.defeat()
    
    def defeat(self):
        """Handle fighter defeat"""
        # Make body more floppy
        for constraint in self.body.constraints:
            if isinstance(constraint, DistanceConstraint):
                constraint.stiffness *= 0.5
        
        # Apply random forces for ragdoll effect
        for node in self.body.nodes:
            random_force = Vector2(
                random.uniform(-100, 100),
                random.uniform(-50, 50)
            )
            node.apply_force(random_force)
    
    def is_defeated(self):
        """Check if fighter is defeated"""
        return self.health <= 0
    
    def get_attack_hitbox(self):
        """Get the attack hitbox"""
        if not self.is_attacking:
            return None
        
        center = self.body.get_center()
        attack_pos = center + self.attack_direction * self.attack_range
        
        # Create a simple circular hitbox
        return {
            "center": attack_pos,
            "radius": 20
        }
    
    def render(self, screen):
        """Render the fighter"""
        if not self.body.active:
            return
        
        # Determine color (flash when hit)
        render_color = self.color
        if self.hit_flash > 0:
            flash_intensity = int(255 * self.hit_flash)
            render_color = (min(255, render_color[0] + flash_intensity),
                          render_color[1], render_color[2])
        
        # Draw body
        for constraint in self.body.constraints:
            if isinstance(constraint, DistanceConstraint):
                start_pos = (int(constraint.a.pos.x), int(constraint.a.pos.y))
                end_pos = (int(constraint.b.pos.x), int(constraint.b.pos.y))
                pygame.draw.line(screen, render_color, start_pos, end_pos, 3)
        
        # Draw attack indicator
        if self.is_attacking:
            hitbox = self.get_attack_hitbox()
            if hitbox:
                pygame.draw.circle(screen, (255, 255, 0), 
                                 (int(hitbox["center"].x), int(hitbox["center"].y)), 
                                 int(hitbox["radius"]), 2)
        
        # Draw health bar
        center = self.body.get_center()
        bar_width = 40
        bar_height = 5
        bar_x = int(center.x - bar_width // 2)
        bar_y = int(center.y - 40)
        
        # Background
        pygame.draw.rect(screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = (100, 255, 100) if self.health > 50 else (255, 255, 100) if self.health > 25 else (255, 100, 100)
        pygame.draw.rect(screen, health_color, 
                        (bar_x, bar_y, health_width, bar_height))

class DestructibleObject:
    """Destructible environment object"""
    
    def __init__(self, world, x, y, width, height, health=50):
        self.world = world
        self.health = health
        self.max_health = health
        
        # Create object body
        self.body = RectangleBody((x, y), width, height, body_type=BodyType.STATIC)
        self.body.material.density = 2.0
        world.add_body(self.body)
        
        # Visual properties
        self.color = (139, 69, 19)  # Brown
        self.destroyed = False
    
    def take_damage(self, damage):
        """Take damage and potentially break"""
        self.health = max(0, self.health - damage)
        
        if self.health <= 0 and not self.destroyed:
            self.destroy()
    
    def destroy(self):
        """Destroy the object"""
        self.destroyed = True
        
        # Remove from world
        self.world.remove_body(self.body)
        
        # Create debris
        center = self.body.get_center()
        for i in range(3):
            debris = RectangleBody((center.x + random.uniform(-20, 20), 
                                  center.y + random.uniform(-20, 20)), 
                                 10, 10, body_type=BodyType.DYNAMIC)
            debris.material.density = 0.5
            debris.material.restitution = 0.3
            self.world.add_body(debris)
    
    def render(self, screen):
        """Render the object"""
        if self.destroyed:
            return
        
        # Determine color based on health
        health_ratio = self.health / self.max_health
        color = tuple(int(c * health_ratio) for c in self.color)
        
        # Draw object
        for constraint in self.body.constraints:
            if isinstance(constraint, DistanceConstraint):
                start_pos = (int(constraint.a.pos.x), int(constraint.a.pos.y))
                end_pos = (int(constraint.b.pos.x), int(constraint.b.pos.y))
                pygame.draw.line(screen, color, start_pos, end_pos, 3)

class FightingGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Physics Fighting Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        
        # Colors
        self.BG_COLOR = (20, 20, 40)
        self.ARENA_COLOR = (60, 60, 80)
        self.TEXT_COLOR = (255, 255, 255)
        
        # Physics world
        self.world = PhysicsWorld(
            gravity=Vector2(0, 800),
            bounds=(self.width, self.height)
        )
        
        # Game objects
        self.fighters = []
        self.destructibles = []
        self.game_state = "fighting"  # "fighting", "game_over"
        self.winner = None
        
        self.setup_arena()
        self.setup_fighters()
        self.setup_destructibles()
        
        # Add collision callback
        self.world.add_collision_callback(self.on_collision)
    
    def setup_arena(self):
        """Create the fighting arena"""
        # Ground
        ground = create_platform(self.world, self.width // 2, self.height - 10, self.width, 20)
        
        # Walls
        left_wall = create_platform(self.world, 10, self.height // 2, 20, self.height)
        right_wall = create_platform(self.world, self.width - 10, self.height // 2, 20, self.height)
        
        # Platforms
        platforms = [
            (300, 500, 150, 20),
            (900, 500, 150, 20),
            (600, 400, 200, 20),
            (200, 300, 100, 20),
            (1000, 300, 100, 20),
        ]
        
        for x, y, w, h in platforms:
            platform = create_platform(self.world, x, y, w, h)
    
    def setup_fighters(self):
        """Create the fighters"""
        # Player 1 (WASD + F to attack)
        player1 = Fighter(self.world, 200, 200, (50, 200, 50), {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "attack": pygame.K_f
        }, is_player=True)
        
        # Player 2 (Arrow keys + L to attack)
        player2 = Fighter(self.world, 1000, 200, (200, 50, 50), {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "attack": pygame.K_l
        }, is_player=True)
        
        self.fighters = [player1, player2]
    
    def setup_destructibles(self):
        """Create destructible objects"""
        destructible_data = [
            (400, 450, 60, 40, 30),
            (800, 450, 60, 40, 30),
            (600, 350, 80, 30, 40),
            (150, 250, 50, 50, 25),
            (1050, 250, 50, 50, 25),
        ]
        
        for x, y, w, h, health in destructible_data:
            obj = DestructibleObject(self.world, x, y, w, h, health)
            self.destructibles.append(obj)
    
    def on_collision(self, body1, body2):
        """Handle collision events"""
        # Check for attack hits
        for fighter in self.fighters:
            if fighter.is_attacking:
                hitbox = fighter.get_attack_hitbox()
                if hitbox:
                    # Check against other fighters
                    for other_fighter in self.fighters:
                        if other_fighter != fighter and not other_fighter.is_defeated():
                            other_center = other_fighter.body.get_center()
                            distance = (hitbox["center"] - other_center).length()
                            if distance < hitbox["radius"] + 20:
                                # Hit landed!
                                knockback = (other_center - hitbox["center"]).normalize()
                                other_fighter.take_damage(fighter.attack_damage, knockback)
                    
                    # Check against destructibles
                    for destructible in self.destructibles:
                        if not destructible.destroyed:
                            obj_center = destructible.body.get_center()
                            distance = (hitbox["center"] - obj_center).length()
                            if distance < hitbox["radius"] + 30:
                                destructible.take_damage(fighter.attack_damage)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_state != "fighting":
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def reset_game(self):
        """Reset the game"""
        # Clear all bodies
        for body in self.world.bodies[:]:
            self.world.remove_body(body)
        
        # Reset game state
        self.game_state = "fighting"
        self.winner = None
        
        # Recreate arena and objects
        self.setup_arena()
        self.setup_fighters()
        self.setup_destructibles()
    
    def update(self, dt):
        """Update game logic"""
        if self.game_state != "fighting":
            return
        
        # Update physics world
        self.world.update(dt)
        
        # Update fighters
        keys = pygame.key.get_pressed()
        for fighter in self.fighters:
            fighter.update(dt, keys)
        
        # Check for game over
        active_fighters = [f for f in self.fighters if not f.is_defeated()]
        if len(active_fighters) <= 1:
            self.game_state = "game_over"
            if len(active_fighters) == 1:
                self.winner = active_fighters[0]
    
    def render(self):
        """Render the game"""
        self.screen.fill(self.BG_COLOR)
        
        # Render destructibles
        for destructible in self.destructibles:
            destructible.render(self.screen)
        
        # Render fighters
        for fighter in self.fighters:
            fighter.render(self.screen)
        
        # Render UI
        self.render_ui()
        
        # Render game over screen
        if self.game_state == "game_over":
            self.render_game_over()
        
        pygame.display.flip()
    
    def render_ui(self):
        """Render UI elements"""
        # Render controls info
        controls_text = [
            "Player 1: WASD to move, F to attack",
            "Player 2: Arrows to move, L to attack",
            "R: Restart, ESC: Quit"
        ]
        
        y_offset = 10
        for text_str in controls_text:
            text = self.font.render(text_str, True, self.TEXT_COLOR)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        # Render fighter health
        for i, fighter in enumerate(self.fighters):
            if not fighter.is_defeated():
                health_text = f"P{i+1} Health: {fighter.health}"
                color = fighter.color
                text = self.font.render(health_text, True, color)
                self.screen.blit(text, (10, 100 + i * 30))
    
    def render_game_over(self):
        """Render game over screen"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.winner:
            winner_color = self.winner.color
            title = self.font.render("FIGHT!", True, winner_color)
            subtitle = self.font.render(f"Player {self.fighters.index(self.winner) + 1} Wins!", True, self.TEXT_COLOR)
        else:
            title = self.font.render("DRAW!", True, (255, 255, 255))
            subtitle = self.font.render("Both fighters defeated!", True, self.TEXT_COLOR)
        
        instruction = self.font.render("Press R to restart", True, self.TEXT_COLOR)
        
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 2))
        instruction_rect = instruction.get_rect(center=(self.width // 2, self.height // 2 + 50))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(instruction, instruction_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            running = self.handle_events()
            self.update(dt)
            self.render()

def main():
    game = FightingGame()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 