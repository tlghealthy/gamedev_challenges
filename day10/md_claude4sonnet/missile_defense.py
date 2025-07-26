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
            pygame.draw.rect(screen, DARK_GREEN, (self.x, self.y, self.width, self.height))
            # Windows
            for i in range(3):
                for j in range(2):
                    window_x = self.x + 5 + i * 10
                    window_y = self.y + 5 + j * 10
                    pygame.draw.rect(screen, YELLOW, (window_x, window_y, 6, 6))
        else:
            # Destroyed city (rubble)
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
            # Rubble details
            for i in range(4):
                rubble_x = self.x + random.randint(0, self.width - 8)
                rubble_y = self.y + random.randint(0, self.height - 8)
                pygame.draw.rect(screen, BLACK, (rubble_x, rubble_y, 8, 8))

class Missile:
    def __init__(self, start_x: int, target_x: int, target_y: int):
        self.x = start_x
        self.y = 0
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 2
        self.destroyed = False
        self.explosion_radius = 20
        
        # Calculate trajectory
        dx = target_x - start_x
        dy = target_y - 0
        distance = math.sqrt(dx**2 + dy**2)
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed
        
    def update(self):
        if not self.destroyed:
            self.x += self.vx
            self.y += self.vy
            
    def draw(self, screen):
        if not self.destroyed:
            # Missile body
            pygame.draw.line(screen, RED, (self.x, self.y), (self.x, self.y - 15), 3)
            # Missile tip
            pygame.draw.polygon(screen, RED, [
                (self.x, self.y - 15),
                (self.x - 3, self.y - 20),
                (self.x + 3, self.y - 20)
            ])
            # Trail
            for i in range(3):
                trail_y = self.y + 5 + i * 5
                trail_x = self.x + random.randint(-2, 2)
                pygame.draw.circle(screen, ORANGE, (trail_x, trail_y), 2)

class Interceptor:
    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 4
        self.destroyed = False
        self.explosion_radius = 15
        
        # Calculate trajectory
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = -self.speed
            
    def update(self):
        if not self.destroyed:
            self.x += self.vx
            self.y += self.vy
            
    def draw(self, screen):
        if not self.destroyed:
            # Interceptor body
            pygame.draw.line(screen, BLUE, (self.x, self.y), (self.x, self.y - 12), 2)
            # Interceptor tip
            pygame.draw.polygon(screen, BLUE, [
                (self.x, self.y - 12),
                (self.x - 2, self.y - 16),
                (self.x + 2, self.y - 16)
            ])
            # Trail
            for i in range(2):
                trail_y = self.y + 3 + i * 4
                trail_x = self.x + random.randint(-1, 1)
                pygame.draw.circle(screen, WHITE, (trail_x, trail_y), 1)

class Explosion:
    def __init__(self, x: int, y: int, radius: int):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.life -= 1
        self.radius = int(self.max_radius * (self.life / self.max_life))
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            # Create a surface for the explosion with alpha
            explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (255, 255, 0, alpha), (self.radius, self.radius), self.radius)
            pygame.draw.circle(explosion_surface, (255, 100, 0, alpha), (self.radius, self.radius), self.radius // 2)
            screen.blit(explosion_surface, (self.x - self.radius, self.y - self.radius))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.score = 0
        self.level = 1
        self.missiles_launched = 0
        self.missiles_destroyed = 0
        self.cities_destroyed = 0
        
        # Game objects
        self.cities = []
        self.missiles = []
        self.interceptors = []
        self.explosions = []
        
        # Game settings
        self.missile_spawn_timer = 0
        self.missile_spawn_delay = 120  # Frames between missile spawns
        self.max_missiles = 5
        
        # Initialize cities
        self.init_cities()
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def init_cities(self):
        city_positions = [
            (50, SCREEN_HEIGHT - 50),
            (150, SCREEN_HEIGHT - 50),
            (250, SCREEN_HEIGHT - 50),
            (350, SCREEN_HEIGHT - 50),
            (450, SCREEN_HEIGHT - 50),
            (550, SCREEN_HEIGHT - 50),
            (650, SCREEN_HEIGHT - 50),
            (750, SCREEN_HEIGHT - 50)
        ]
        
        for x, y in city_positions:
            self.cities.append(City(x, y))
    
    def spawn_missile(self):
        if len(self.missiles) < self.max_missiles:
            # Choose a random city as target
            target_city = random.choice([city for city in self.cities if not city.destroyed])
            if target_city:
                start_x = random.randint(50, SCREEN_WIDTH - 50)
                self.missiles.append(Missile(start_x, target_city.x + target_city.width // 2, target_city.y))
                self.missiles_launched += 1
    
    def launch_interceptor(self, mouse_x: int, mouse_y: int):
        # Find the closest missile to the mouse position
        closest_missile = None
        closest_distance = float('inf')
        
        for missile in self.missiles:
            if not missile.destroyed:
                distance = math.sqrt((mouse_x - missile.x)**2 + (mouse_y - missile.y)**2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_missile = missile
        
        if closest_missile and closest_distance < 100:  # Only launch if mouse is near a missile
            # Launch from bottom of screen
            launch_x = random.randint(50, SCREEN_WIDTH - 50)
            self.interceptors.append(Interceptor(launch_x, SCREEN_HEIGHT - 20, closest_missile.x, closest_missile.y))
    
    def check_collisions(self):
        # Check interceptor-missile collisions
        for interceptor in self.interceptors:
            if not interceptor.destroyed:
                for missile in self.missiles:
                    if not missile.destroyed:
                        distance = math.sqrt((interceptor.x - missile.x)**2 + (interceptor.y - missile.y)**2)
                        if distance < 15:
                            # Create explosion
                            self.explosions.append(Explosion(missile.x, missile.y, missile.explosion_radius))
                            missile.destroyed = True
                            interceptor.destroyed = True
                            self.missiles_destroyed += 1
                            self.score += 100
                            break
        
        # Check missile-city collisions
        for missile in self.missiles:
            if not missile.destroyed and missile.y >= SCREEN_HEIGHT - 80:
                for city in self.cities:
                    if not city.destroyed:
                        if (missile.x >= city.x and missile.x <= city.x + city.width and
                            missile.y >= city.y and missile.y <= city.y + city.height):
                            # Create explosion
                            self.explosions.append(Explosion(missile.x, missile.y, missile.explosion_radius))
                            missile.destroyed = True
                            city.destroyed = True
                            self.cities_destroyed += 1
                            self.score -= 200
                            break
    
    def update(self):
        # Spawn missiles
        self.missile_spawn_timer += 1
        if self.missile_spawn_timer >= self.missile_spawn_delay:
            self.spawn_missile()
            self.missile_spawn_timer = 0
            # Increase difficulty
            self.missile_spawn_delay = max(30, self.missile_spawn_delay - 2)
            self.max_missiles = min(10, self.max_missiles + 1)
        
        # Update missiles
        for missile in self.missiles:
            missile.update()
        
        # Update interceptors
        for interceptor in self.interceptors:
            interceptor.update()
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.life <= 0:
                self.explosions.remove(explosion)
        
        # Check collisions
        self.check_collisions()
        
        # Remove destroyed objects
        self.missiles = [m for m in self.missiles if not m.destroyed or m.y < SCREEN_HEIGHT]
        self.interceptors = [i for i in self.interceptors if not i.destroyed or i.y > 0]
        
        # Check game over
        if self.cities_destroyed >= len(self.cities):
            self.running = False
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw ground
        pygame.draw.rect(self.screen, DARK_GREEN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        
        # Draw cities
        for city in self.cities:
            city.draw(self.screen)
        
        # Draw missiles
        for missile in self.missiles:
            missile.draw(self.screen)
        
        # Draw interceptors
        for interceptor in self.interceptors:
            interceptor.draw(self.screen)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Cities remaining
        cities_remaining = len([city for city in self.cities if not city.destroyed])
        cities_text = self.small_font.render(f"Cities: {cities_remaining}/{len(self.cities)}", True, WHITE)
        self.screen.blit(cities_text, (10, 90))
        
        # Missiles destroyed
        missiles_text = self.small_font.render(f"Destroyed: {self.missiles_destroyed}", True, WHITE)
        self.screen.blit(missiles_text, (10, 110))
        
        # Instructions
        instructions = [
            "Click near missiles to launch interceptors",
            "Defend your cities!",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, GRAY)
            self.screen.blit(inst_text, (SCREEN_WIDTH - 300, 10 + i * 25))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.launch_interceptor(event.pos[0], event.pos[1])
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Game over screen
        self.show_game_over()
    
    def show_game_over(self):
        self.screen.fill(BLACK)
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        cities_text = self.small_font.render(f"Cities Destroyed: {self.cities_destroyed}", True, WHITE)
        missiles_text = self.small_font.render(f"Missiles Destroyed: {self.missiles_destroyed}", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 200))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))
        self.screen.blit(cities_text, (SCREEN_WIDTH//2 - cities_text.get_width()//2, 290))
        self.screen.blit(missiles_text, (SCREEN_WIDTH//2 - missiles_text.get_width()//2, 310))
        
        pygame.display.flip()
        
        # Wait for user to close
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit() 