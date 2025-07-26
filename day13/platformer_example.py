import pygame
import sys
import random
from verlet_physics import *

# -------------------------------------------------------------
#  Simple Platformer Example using Verlet Physics
# -------------------------------------------------------------
#  Features:
#  • Player character with smooth physics-based movement
#  • Enemies with simple AI
#  • Collectible coins
#  • Level design with platforms and obstacles
#  • Score system and game states
# -------------------------------------------------------------

class PlatformerGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Physics Platformer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        
        # Colors
        self.BG_COLOR = (50, 100, 150)
        self.PLATFORM_COLOR = (80, 60, 40)
        self.PLAYER_COLOR = (50, 200, 50)
        self.ENEMY_COLOR = (200, 50, 50)
        self.COIN_COLOR = (255, 215, 0)
        self.TEXT_COLOR = (255, 255, 255)
        
        # Physics world
        self.world = PhysicsWorld(
            gravity=Vector2(0, 1000),
            bounds=(self.width, self.height)
        )
        
        # Game objects
        self.player = None
        self.player_controller = None
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.game_state = "playing"  # "playing", "game_over", "victory"
        
        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        
        self.setup_level()
    
    def setup_level(self):
        """Create the level layout"""
        # Clear existing objects
        for body in self.world.bodies[:]:
            self.world.remove_body(body)
        
        self.platforms.clear()
        self.enemies.clear()
        self.coins.clear()
        
        # Create ground
        ground = create_platform(self.world, self.width // 2, self.height - 10, self.width, 20)
        self.platforms.append(ground)
        
        # Create level-specific platforms
        if self.level == 1:
            self.create_level_1()
        elif self.level == 2:
            self.create_level_2()
        else:
            self.create_level_3()
        
        # Create player
        self.player = create_player(self.world, 50, 100, 20)
        self.player_controller = PlayerController(self.player, speed=350, jump_force=450)
        
        # Create enemies
        self.spawn_enemies()
        
        # Create coins
        self.spawn_coins()
        
        # Add collision callback
        self.world.add_collision_callback(self.on_collision)
    
    def create_level_1(self):
        """Create level 1 layout"""
        platform_data = [
            (200, 500, 120, 15),
            (400, 400, 120, 15),
            (600, 300, 120, 15),
            (800, 200, 120, 15),
            (300, 200, 100, 15),
            (700, 450, 100, 15),
        ]
        
        for x, y, w, h in platform_data:
            platform = create_platform(self.world, x, y, w, h)
            self.platforms.append(platform)
    
    def create_level_2(self):
        """Create level 2 layout"""
        platform_data = [
            (150, 500, 100, 15),
            (350, 450, 100, 15),
            (550, 400, 100, 15),
            (750, 350, 100, 15),
            (200, 300, 100, 15),
            (400, 250, 100, 15),
            (600, 200, 100, 15),
            (800, 150, 100, 15),
        ]
        
        for x, y, w, h in platform_data:
            platform = create_platform(self.world, x, y, w, h)
            self.platforms.append(platform)
    
    def create_level_3(self):
        """Create level 3 layout"""
        platform_data = [
            (100, 500, 80, 15),
            (250, 450, 80, 15),
            (400, 400, 80, 15),
            (550, 350, 80, 15),
            (700, 300, 80, 15),
            (850, 250, 80, 15),
            (150, 200, 80, 15),
            (300, 150, 80, 15),
            (450, 100, 80, 15),
            (600, 50, 80, 15),
        ]
        
        for x, y, w, h in platform_data:
            platform = create_platform(self.world, x, y, w, h)
            self.platforms.append(platform)
    
    def spawn_enemies(self):
        """Spawn enemies for the current level"""
        num_enemies = min(self.level + 2, 6)
        
        for i in range(num_enemies):
            x = random.randint(200, self.width - 200)
            y = random.randint(100, 400)
            enemy = self.create_enemy(x, y)
            self.enemies.append(enemy)
    
    def create_enemy(self, x, y):
        """Create an enemy character"""
        enemy = RectangleBody((x, y), 15, 15, body_type=BodyType.DYNAMIC)
        enemy.material.density = 1.5
        enemy.material.friction = 0.2
        enemy.material.restitution = 0.3
        self.world.add_body(enemy)
        return enemy
    
    def spawn_coins(self):
        """Spawn collectible coins"""
        num_coins = self.level * 5
        
        for i in range(num_coins):
            x = random.randint(100, self.width - 100)
            y = random.randint(50, 450)
            coin = self.create_coin(x, y)
            self.coins.append(coin)
    
    def create_coin(self, x, y):
        """Create a collectible coin"""
        coin = CircleBody((x, y), 8, body_type=BodyType.DYNAMIC)
        coin.material.density = 0.5
        coin.material.restitution = 0.8
        coin.material.friction = 0.1
        self.world.add_body(coin)
        return coin
    
    def on_collision(self, body1, body2):
        """Handle collision events"""
        # Player vs Enemy
        if (body1 == self.player and body2 in self.enemies) or \
           (body2 == self.player and body1 in self.enemies):
            self.player_hit()
        
        # Player vs Coin
        if (body1 == self.player and body2 in self.coins) or \
           (body2 == self.player and body1 in self.coins):
            coin = body2 if body1 == self.player else body1
            self.collect_coin(coin)
    
    def player_hit(self):
        """Handle player being hit by enemy"""
        self.lives -= 1
        if self.lives <= 0:
            self.game_state = "game_over"
        else:
            # Reset player position
            self.player.pos = Vector2(50, 100)
            for node in self.player.nodes:
                node.pos = Vector2(50, 100)
    
    def collect_coin(self, coin):
        """Handle coin collection"""
        if coin in self.coins:
            self.coins.remove(coin)
            self.world.remove_body(coin)
            self.score += 10
            
            # Check if all coins collected
            if len(self.coins) == 0:
                self.next_level()
    
    def next_level(self):
        """Advance to next level"""
        self.level += 1
        if self.level > 3:
            self.game_state = "victory"
        else:
            self.setup_level()
    
    def update_enemies(self, dt):
        """Update enemy AI"""
        for enemy in self.enemies:
            if not enemy.active:
                continue
            
            # Simple enemy AI - move back and forth
            center = enemy.get_center()
            
            # Check if enemy is on a platform
            on_platform = False
            for platform in self.platforms:
                platform_center = platform.get_center()
                if abs(center.y - platform_center.y) < 30 and \
                   abs(center.x - platform_center.x) < platform.shape_data["width"] // 2:
                    on_platform = True
                    break
            
            # Apply movement force
            if on_platform:
                # Move back and forth on platform
                direction = 1 if (pygame.time.get_ticks() // 1000) % 4 < 2 else -1
                force = Vector2(direction * 50, 0)
                enemy.apply_force_at_point(force, center)
            else:
                # Fall down
                enemy.apply_force_at_point(Vector2(0, 100), center)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_state != "playing":
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_state = "playing"
        self.setup_level()
    
    def update(self, dt):
        """Update game logic"""
        if self.game_state != "playing":
            return
        
        # Update physics world
        self.world.update(dt)
        
        # Update player controller
        keys = pygame.key.get_pressed()
        self.player_controller.handle_input(keys, dt)
        self.player_controller.update(dt)
        
        # Update enemies
        self.update_enemies(dt)
        
        # Check if player fell off screen
        if self.player and self.player.get_center().y > self.height + 50:
            self.player_hit()
    
    def render(self):
        """Render the game"""
        self.screen.fill(self.BG_COLOR)
        
        # Render platforms
        for platform in self.platforms:
            self.render_body(platform, self.PLATFORM_COLOR)
        
        # Render coins
        for coin in self.coins:
            self.render_body(coin, self.COIN_COLOR)
        
        # Render enemies
        for enemy in self.enemies:
            self.render_body(enemy, self.ENEMY_COLOR)
        
        # Render player
        if self.player:
            self.render_body(self.player, self.PLAYER_COLOR)
        
        # Render UI
        self.render_ui()
        
        # Render game state screen
        if self.game_state != "playing":
            self.render_game_state()
        
        pygame.display.flip()
    
    def render_body(self, body, color):
        """Render a physics body"""
        if not body.active or not body.nodes:
            return
        
        # Draw edges/constraints
        for constraint in body.constraints:
            if isinstance(constraint, DistanceConstraint):
                start_pos = (int(constraint.a.pos.x), int(constraint.a.pos.y))
                end_pos = (int(constraint.b.pos.x), int(constraint.b.pos.y))
                pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
    
    def render_ui(self):
        """Render UI elements"""
        info_texts = [
            f"Score: {self.score}",
            f"Lives: {self.lives}",
            f"Level: {self.level}",
            f"Coins: {len(self.coins)}",
            "Controls: WASD/Arrows to move, SPACE to jump"
        ]
        
        y_offset = 10
        for text_str in info_texts:
            text = self.font.render(text_str, True, self.TEXT_COLOR)
            self.screen.blit(text, (10, y_offset))
            y_offset += 30
    
    def render_game_state(self):
        """Render game over/victory screen"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.game_state == "game_over":
            title = self.font.render("GAME OVER", True, (255, 100, 100))
            subtitle = self.font.render(f"Final Score: {self.score}", True, self.TEXT_COLOR)
            instruction = self.font.render("Press R to restart", True, self.TEXT_COLOR)
        else:  # victory
            title = self.font.render("VICTORY!", True, (100, 255, 100))
            subtitle = self.font.render(f"Final Score: {self.score}", True, self.TEXT_COLOR)
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
    game = PlatformerGame()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 