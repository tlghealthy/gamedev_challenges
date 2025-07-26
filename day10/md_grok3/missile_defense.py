import pygame
import math
import random
from typing import List, Tuple, Optional

# Initialize pygame
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
            # Roof
            pygame.draw.polygon(screen, GRAY, [
                (self.x, self.y),
                (self.x + self.width // 2, self.y - 10),
                (self.x + self.width, self.y)
            ])
        else:
            # Destroyed city
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            # Rubble
            for _ in range(5):
                rubble_x = self.x + random.randint(0, self.width)
                rubble_y = self.y + random.randint(0, self.height)
                pygame.draw.circle(screen, GRAY, (rubble_x, rubble_y), 2)

class Missile:
    def __init__(self, start_x: int, target_x: int, target_y: int):
        self.x = start_x
        self.y = 0
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 2
        self.destroyed = False
        self.trail = []
        
        # Calculate direction
        dx = target_x - start_x
        dy = target_y - 0
        distance = math.sqrt(dx**2 + dy**2)
        self.dx = (dx / distance) * self.speed
        self.dy = (dy / distance) * self.speed
        
    def update(self):
        if not self.destroyed:
            self.x += self.dx
            self.y += self.dy
            
            # Add to trail
            self.trail.append((self.x, self.y))
            if len(self.trail) > 10:
                self.trail.pop(0)
                
    def draw(self, screen):
        if not self.destroyed:
            # Draw trail
            for i, (trail_x, trail_y) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                color = (255, 255, 0, alpha)
                pygame.draw.circle(screen, color, (int(trail_x), int(trail_y)), 2)
            
            # Draw missile
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 4)
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 2)
            
    def check_collision(self, city: City) -> bool:
        if self.destroyed or city.destroyed:
            return False
        return (self.x > city.x and self.x < city.x + city.width and
                self.y > city.y and self.y < city.y + city.height)

class Interceptor:
    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 4
        self.destroyed = False
        self.trail = []
        
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
        if not self.destroyed:
            self.x += self.dx
            self.y += self.dy
            
            # Add to trail
            self.trail.append((self.x, self.y))
            if len(self.trail) > 8:
                self.trail.pop(0)
                
    def draw(self, screen):
        if not self.destroyed:
            # Draw trail
            for i, (trail_x, trail_y) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                color = (0, 255, 255, alpha)
                pygame.draw.circle(screen, color, (int(trail_x), int(trail_y)), 2)
            
            # Draw interceptor
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 1)
            
    def check_collision(self, missile: Missile) -> bool:
        if self.destroyed or missile.destroyed:
            return False
        distance = math.sqrt((self.x - missile.x)**2 + (self.y - missile.y)**2)
        return distance < 8

class Explosion:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.life -= 1
        self.radius = self.max_radius * (1 - self.life / self.max_life)
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (255, 255, 0, alpha)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.radius))
            
    def is_dead(self) -> bool:
        return self.life <= 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.level = 1
        self.missiles_launched = 0
        self.missiles_destroyed = 0
        
        # Game objects
        self.cities = self.create_cities()
        self.missiles = []
        self.interceptors = []
        self.explosions = []
        
        # Timing
        self.missile_timer = 0
        self.missile_delay = 120  # Frames between missile launches
        
    def create_cities(self) -> List[City]:
        cities = []
        city_width = 40
        spacing = 60
        start_x = 50
        y = SCREEN_HEIGHT - 50
        
        for i in range(8):
            x = start_x + i * (city_width + spacing)
            cities.append(City(x, y))
        return cities
    
    def spawn_missile(self):
        if len(self.missiles) < 5 + self.level:  # Limit missiles based on level
            # Choose a random city as target
            available_cities = [city for city in self.cities if not city.destroyed]
            if available_cities:
                target_city = random.choice(available_cities)
                start_x = random.randint(50, SCREEN_WIDTH - 50)
                missile = Missile(start_x, target_city.x + target_city.width // 2, target_city.y)
                self.missiles.append(missile)
                self.missiles_launched += 1
    
    def launch_interceptor(self, mouse_x: int, mouse_y: int):
        if len(self.interceptors) < 3:  # Limit active interceptors
            interceptor = Interceptor(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, mouse_x, mouse_y)
            self.interceptors.append(interceptor)
    
    def update(self):
        if self.game_over:
            return
            
        # Spawn missiles
        self.missile_timer += 1
        if self.missile_timer >= self.missile_delay:
            self.spawn_missile()
            self.missile_timer = 0
            # Increase difficulty
            self.missile_delay = max(60, self.missile_delay - 2)
        
        # Update missiles
        for missile in self.missiles[:]:
            missile.update()
            
            # Check if missile hit a city
            for city in self.cities:
                if missile.check_collision(city):
                    city.destroyed = True
                    missile.destroyed = True
                    explosion = Explosion(missile.x, missile.y)
                    self.explosions.append(explosion)
                    self.lives -= 1
                    break
            
            # Remove missiles that are off screen or destroyed
            if missile.y > SCREEN_HEIGHT or missile.destroyed:
                self.missiles.remove(missile)
        
        # Update interceptors
        for interceptor in self.interceptors[:]:
            interceptor.update()
            
            # Check collision with missiles
            for missile in self.missiles[:]:
                if interceptor.check_collision(missile):
                    missile.destroyed = True
                    interceptor.destroyed = True
                    explosion = Explosion(missile.x, missile.y)
                    self.explosions.append(explosion)
                    self.score += 100
                    self.missiles_destroyed += 1
                    break
            
            # Remove interceptors that are off screen or destroyed
            if interceptor.y < 0 or interceptor.destroyed:
                if interceptor in self.interceptors:
                    self.interceptors.remove(interceptor)
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_dead():
                self.explosions.remove(explosion)
        
        # Check game over
        if self.lives <= 0:
            self.game_over = True
        
        # Check level progression
        if self.missiles_destroyed >= self.level * 10:
            self.level += 1
            self.missiles_destroyed = 0
    
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
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 90))
        
        # Instructions
        if not self.game_over:
            instructions = self.small_font.render("Click to launch interceptors!", True, WHITE)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - 100, 10))
        
        # Game over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 50))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Left click
                    self.launch_interceptor(event.pos[0], event.pos[1])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Restart game
        return True
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit() 