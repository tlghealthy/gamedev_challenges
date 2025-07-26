import pygame
import math
import random
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)

class City:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.destroyed = False
        self.health = 100
        
    def draw(self, screen):
        if not self.destroyed:
            # City building
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
            # Windows
            for i in range(3):
                for j in range(2):
                    window_x = self.x + 5 + i * 10
                    window_y = self.y + 5 + j * 10
                    pygame.draw.rect(screen, YELLOW, (window_x, window_y, 6, 6))
            # Roof
            pygame.draw.polygon(screen, DARK_GREEN, [
                (self.x, self.y),
                (self.x + self.width // 2, self.y - 10),
                (self.x + self.width, self.y)
            ])
        else:
            # Destroyed city (rubble)
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            for i in range(5):
                rubble_x = self.x + random.randint(0, self.width - 5)
                rubble_y = self.y + random.randint(0, self.height - 5)
                pygame.draw.rect(screen, GRAY, (rubble_x, rubble_y, 3, 3))

class Missile:
    def __init__(self, x: int, y: int, target_x: int, target_y: int, speed: float = 2.0):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.active = True
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.dx = (dx / distance) * speed
            self.dy = (dy / distance) * speed
        else:
            self.dx = 0
            self.dy = speed
            
    def update(self):
        if self.active:
            self.x += self.dx
            self.y += self.dy
            
            # Check if missile has reached target
            if self.y >= self.target_y:
                self.active = False
                
    def draw(self, screen):
        if self.active:
            # Missile body
            pygame.draw.line(screen, RED, (self.x, self.y), (self.x, self.y - 10), 3)
            # Missile tip
            pygame.draw.polygon(screen, RED, [
                (self.x, self.y - 10),
                (self.x - 3, self.y - 15),
                (self.x + 3, self.y - 15)
            ])
            # Trail
            for i in range(3):
                trail_y = self.y + 5 + i * 3
                pygame.draw.circle(screen, ORANGE, (int(self.x), int(trail_y)), 1)

class PlayerMissile:
    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 4.0
        self.active = True
        self.explosion_radius = 30
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = -self.speed
            
    def update(self):
        if self.active:
            self.x += self.dx
            self.y += self.dy
            
            # Check if missile has gone off screen
            if self.y < 0:
                self.active = False
                
    def draw(self, screen):
        if self.active:
            # Missile body
            pygame.draw.line(screen, GREEN, (self.x, self.y), (self.x, self.y + 10), 3)
            # Missile tip
            pygame.draw.polygon(screen, GREEN, [
                (self.x, self.y + 10),
                (self.x - 3, self.y + 15),
                (self.x + 3, self.y + 15)
            ])
            # Trail
            for i in range(3):
                trail_y = self.y - 5 - i * 3
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(trail_y)), 1)

class Explosion:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.active = True
        self.growth_rate = 2
        
    def update(self):
        if self.active:
            self.radius += self.growth_rate
            if self.radius >= self.max_radius:
                self.active = False
                
    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), int(self.radius * 0.7))
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), int(self.radius * 0.4))

class MissileDefense:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        
        # Cities
        self.cities = []
        city_spacing = SCREEN_WIDTH // 6
        for i in range(5):
            x = city_spacing * (i + 1) - 20
            y = SCREEN_HEIGHT - 50
            self.cities.append(City(x, y))
            
        # Missiles
        self.enemy_missiles = []
        self.player_missiles = []
        self.explosions = []
        
        # Player launcher
        self.launcher_x = SCREEN_WIDTH // 2
        self.launcher_y = SCREEN_HEIGHT - 20
        
        # Game timing
        self.missile_spawn_timer = 0
        self.missile_spawn_delay = 120  # frames between missile spawns
        
        # Font
        self.font = pygame.font.Font(None, 36)
        
    def spawn_enemy_missile(self):
        """Spawn a new enemy missile targeting a random city"""
        if not self.cities:
            return
            
        # Find a non-destroyed city to target
        available_cities = [city for city in self.cities if not city.destroyed]
        if not available_cities:
            return
            
        target_city = random.choice(available_cities)
        start_x = random.randint(50, SCREEN_WIDTH - 50)
        start_y = 0
        
        # Add some randomness to the target
        target_x = target_city.x + random.randint(-10, target_city.width + 10)
        target_y = target_city.y
        
        speed = 1.5 + (self.level * 0.2)  # Speed increases with level
        self.enemy_missiles.append(Missile(start_x, start_y, target_x, target_y, speed))
        
    def handle_input(self):
        """Handle player input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Left click
                    # Launch missile at mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.player_missiles.append(PlayerMissile(
                        self.launcher_x, self.launcher_y, mouse_x, mouse_y
                    ))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Restart game
                    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
            
        # Spawn enemy missiles
        self.missile_spawn_timer += 1
        if self.missile_spawn_timer >= self.missile_spawn_delay:
            self.spawn_enemy_missile()
            self.missile_spawn_timer = 0
            # Decrease spawn delay as level increases
            self.missile_spawn_delay = max(30, 120 - (self.level * 10))
            
        # Update enemy missiles
        for missile in self.enemy_missiles[:]:
            missile.update()
            if not missile.active:
                self.enemy_missiles.remove(missile)
                # Check if missile hit a city
                for city in self.cities:
                    if (missile.x >= city.x and missile.x <= city.x + city.width and
                        missile.y >= city.y and missile.y <= city.y + city.height and
                        not city.destroyed):
                        city.destroyed = True
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_over = True
                        break
                        
        # Update player missiles
        for missile in self.player_missiles[:]:
            missile.update()
            if not missile.active:
                self.player_missiles.remove(missile)
                
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)
                
        # Check collisions between player missiles and enemy missiles
        for player_missile in self.player_missiles[:]:
            if not player_missile.active:
                continue
            for enemy_missile in self.enemy_missiles[:]:
                if not enemy_missile.active:
                    continue
                    
                distance = math.sqrt((player_missile.x - enemy_missile.x)**2 + 
                                   (player_missile.y - enemy_missile.y)**2)
                                   
                if distance < player_missile.explosion_radius:
                    # Create explosion
                    self.explosions.append(Explosion(enemy_missile.x, enemy_missile.y))
                    # Destroy both missiles
                    player_missile.active = False
                    enemy_missile.active = False
                    # Add score
                    self.score += 100
                    break
                    
        # Check if all cities are destroyed
        if all(city.destroyed for city in self.cities):
            self.game_over = True
            
        # Level progression
        if self.score >= self.level * 1000:
            self.level += 1
            
    def draw(self):
        """Draw the game"""
        self.screen.fill(BLACK)
        
        # Draw cities
        for city in self.cities:
            city.draw(self.screen)
            
        # Draw enemy missiles
        for missile in self.enemy_missiles:
            missile.draw(self.screen)
            
        # Draw player missiles
        for missile in self.player_missiles:
            missile.draw(self.screen)
            
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)
            
        # Draw launcher
        pygame.draw.rect(self.screen, BLUE, (self.launcher_x - 15, self.launcher_y - 10, 30, 20))
        pygame.draw.rect(self.screen, WHITE, (self.launcher_x - 5, self.launcher_y - 15, 10, 10))
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        self.screen.blit(lives_text, (10, 90))
        
        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
            self.screen.blit(final_score_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))
            
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = MissileDefense()
    game.run() 