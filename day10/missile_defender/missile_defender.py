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
BROWN = (139, 69, 19)

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
            pygame.draw.rect(screen, DARK_GREEN, (self.x - 2, self.y, self.width + 4, 5))
        else:
            # Destroyed city (rubble)
            pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
            # Rubble pieces
            for _ in range(5):
                rubble_x = self.x + random.randint(0, self.width - 5)
                rubble_y = self.y + random.randint(0, self.height - 5)
                pygame.draw.rect(screen, GRAY, (rubble_x, rubble_y, 3, 3))

class MissileLauncher:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 30
        self.missiles: List[PlayerMissile] = []
        self.reload_time = 0
        self.reload_delay = 10  # frames between shots
        
    def draw(self, screen):
        # Base
        pygame.draw.rect(screen, DARK_GREEN, (self.x - 5, self.y + self.height, 30, 10))
        # Launcher body
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        # Barrel
        pygame.draw.rect(screen, BLACK, (self.x + 7, self.y - 10, 6, 15))
        
    def fire(self):
        if self.reload_time <= 0:
            missile = PlayerMissile(self.x + 10, self.y - 5)
            self.missiles.append(missile)
            self.reload_time = self.reload_delay
            
    def update(self):
        if self.reload_time > 0:
            self.reload_time -= 1
            
        # Update missiles
        for missile in self.missiles[:]:
            missile.update()
            if missile.y < -10:
                self.missiles.remove(missile)

class PlayerMissile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.speed = 8
        self.width = 4
        self.height = 12
        
    def update(self):
        self.y -= self.speed
        
    def draw(self, screen):
        # Missile body
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        # Missile tip
        pygame.draw.polygon(screen, RED, [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width // 2, self.y - 8)
        ])
        # Exhaust trail
        pygame.draw.rect(screen, ORANGE, (self.x + 1, self.y + self.height, 2, 6))

class EnemyMissile:
    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 3
        self.width = 6
        self.height = 15
        
        # Calculate trajectory
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = self.speed
            
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
    def draw(self, screen):
        # Missile body
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        # Missile tip
        pygame.draw.polygon(screen, WHITE, [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width // 2, self.y - 10)
        ])

class Explosion:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.life = 20
        
    def update(self):
        self.radius += 1
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int((self.life / 20) * 255)
            color = (255, 255, 0, alpha)
            # Create a surface for the explosion with alpha
            explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, color, (self.radius, self.radius), self.radius)
            screen.blit(explosion_surface, (self.x - self.radius, self.y - self.radius))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defender")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game objects
        self.cities = self.create_cities()
        self.launchers = self.create_launchers()
        self.enemy_missiles: List[EnemyMissile] = []
        self.explosions: List[Explosion] = []
        
        # Game state
        self.score = 0
        self.level = 1
        self.missiles_per_wave = 5
        self.wave_timer = 0
        self.wave_delay = 120  # frames between waves
        self.game_over = False
        
        # Input
        self.mouse_pos = (0, 0)
        
    def create_cities(self) -> List[City]:
        cities = []
        city_spacing = SCREEN_WIDTH // 6
        for i in range(5):
            x = city_spacing * (i + 1) - 20
            y = SCREEN_HEIGHT - 50
            cities.append(City(x, y))
        return cities
    
    def create_launchers(self) -> List[MissileLauncher]:
        launchers = []
        launcher_spacing = SCREEN_WIDTH // 4
        for i in range(3):
            x = launcher_spacing * (i + 1) - 10
            y = SCREEN_HEIGHT - 100
            launchers.append(MissileLauncher(x, y))
        return launchers
    
    def spawn_enemy_missile(self):
        if len(self.enemy_missiles) < self.missiles_per_wave:
            # Choose a random city as target
            target_city = random.choice([city for city in self.cities if not city.destroyed])
            if target_city:
                x = random.randint(0, SCREEN_WIDTH)
                y = -20
                missile = EnemyMissile(x, y, target_city.x + target_city.width // 2, target_city.y)
                self.enemy_missiles.append(missile)
    
    def check_collisions(self):
        # Check player missiles vs enemy missiles
        for launcher in self.launchers:
            for player_missile in launcher.missiles[:]:
                for enemy_missile in self.enemy_missiles[:]:
                    if (player_missile.x < enemy_missile.x + enemy_missile.width and
                        player_missile.x + player_missile.width > enemy_missile.x and
                        player_missile.y < enemy_missile.y + enemy_missile.height and
                        player_missile.y + player_missile.height > enemy_missile.y):
                        
                        # Create explosion
                        explosion = Explosion(enemy_missile.x + enemy_missile.width // 2, 
                                            enemy_missile.y + enemy_missile.height // 2)
                        self.explosions.append(explosion)
                        
                        # Remove missiles
                        launcher.missiles.remove(player_missile)
                        self.enemy_missiles.remove(enemy_missile)
                        self.score += 100
                        break
        
        # Check enemy missiles vs cities
        for enemy_missile in self.enemy_missiles[:]:
            for city in self.cities:
                if not city.destroyed:
                    if (enemy_missile.x < city.x + city.width and
                        enemy_missile.x + enemy_missile.width > city.x and
                        enemy_missile.y < city.y + city.height and
                        enemy_missile.y + enemy_missile.height > city.y):
                        
                        # Create explosion
                        explosion = Explosion(enemy_missile.x + enemy_missile.width // 2, 
                                            enemy_missile.y + enemy_missile.height // 2)
                        self.explosions.append(explosion)
                        
                        # Destroy city
                        city.destroyed = True
                        self.enemy_missiles.remove(enemy_missile)
                        break
        
        # Check if all cities are destroyed
        if all(city.destroyed for city in self.cities):
            self.game_over = True
    
    def update(self):
        if self.game_over:
            return
            
        # Update launchers
        for launcher in self.launchers:
            launcher.update()
        
        # Update enemy missiles
        for missile in self.enemy_missiles[:]:
            missile.update()
            if missile.y > SCREEN_HEIGHT + 20:
                self.enemy_missiles.remove(missile)
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.life <= 0:
                self.explosions.remove(explosion)
        
        # Spawn enemy missiles
        self.wave_timer += 1
        if self.wave_timer >= self.wave_delay:
            self.spawn_enemy_missile()
            if len(self.enemy_missiles) >= self.missiles_per_wave:
                self.wave_timer = 0
                self.level += 1
                self.missiles_per_wave = min(5 + self.level, 15)
                self.wave_delay = max(60, 120 - self.level * 10)
        
        # Check collisions
        self.check_collisions()
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw ground
        pygame.draw.rect(self.screen, DARK_GREEN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        
        # Draw cities
        for city in self.cities:
            city.draw(self.screen)
        
        # Draw launchers
        for launcher in self.launchers:
            launcher.draw(self.screen)
            for missile in launcher.missiles:
                missile.draw(self.screen)
        
        # Draw enemy missiles
        for missile in self.enemy_missiles:
            missile.draw(self.screen)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        cities_text = font.render(f"Cities: {sum(1 for city in self.cities if not city.destroyed)}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        self.screen.blit(cities_text, (10, 90))
        
        if self.game_over:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Left click
                    # Find closest launcher to mouse
                    mouse_x, mouse_y = event.pos
                    closest_launcher = min(self.launchers, 
                                         key=lambda l: abs(l.x - mouse_x))
                    closest_launcher.fire()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Restart game
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run() 