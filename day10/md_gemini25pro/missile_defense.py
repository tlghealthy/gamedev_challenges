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
LIGHT_BLUE = (173, 216, 230)

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
            # Destroyed city (rubble)
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
            # Smoke effect
            for i in range(3):
                smoke_x = self.x + random.randint(0, self.width)
                smoke_y = self.y - random.randint(5, 15)
                pygame.draw.circle(screen, (100, 100, 100), (smoke_x, smoke_y), 3)

class Missile:
    def __init__(self, start_x: int, target_x: int, target_y: int):
        self.x = start_x
        self.y = 0
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 2
        self.destroyed = False
        self.trail = []
        
        # Calculate trajectory
        dx = target_x - start_x
        dy = target_y - 0
        distance = math.sqrt(dx*dx + dy*dy)
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed
        
    def update(self):
        if not self.destroyed:
            self.x += self.vx
            self.y += self.vy
            
            # Add to trail
            self.trail.append((self.x, self.y))
            if len(self.trail) > 10:
                self.trail.pop(0)
                
    def draw(self, screen):
        if not self.destroyed:
            # Draw trail
            for i, (trail_x, trail_y) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                color = (255, 0, 0, alpha)
                pygame.draw.circle(screen, color, (int(trail_x), int(trail_y)), 2)
            
            # Draw missile
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 4)
            # Missile tip
            pygame.draw.polygon(screen, ORANGE, [
                (self.x, self.y - 6),
                (self.x - 3, self.y),
                (self.x + 3, self.y)
            ])
            
    def check_collision(self, city: City) -> bool:
        if self.destroyed or city.destroyed:
            return False
        return (self.x >= city.x and self.x <= city.x + city.width and
                self.y >= city.y and self.y <= city.y + city.height)

class Interceptor:
    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 4
        self.destroyed = False
        self.exploded = False
        self.explosion_radius = 30
        self.explosion_timer = 0
        self.trail = []
        
        # Calculate trajectory
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = -self.speed
            
    def update(self):
        if not self.destroyed and not self.exploded:
            self.x += self.vx
            self.y += self.vy
            
            # Add to trail
            self.trail.append((self.x, self.y))
            if len(self.trail) > 8:
                self.trail.pop(0)
                
            # Check if reached target area
            distance_to_target = math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2)
            if distance_to_target < 20:
                self.explode()
                
        elif self.exploded:
            self.explosion_timer += 1
            if self.explosion_timer > 10:
                self.destroyed = True
                
    def explode(self):
        self.exploded = True
        self.explosion_timer = 0
        
    def draw(self, screen):
        if not self.destroyed:
            if not self.exploded:
                # Draw trail
                for i, (trail_x, trail_y) in enumerate(self.trail):
                    alpha = int(255 * (i / len(self.trail)))
                    color = (0, 255, 0, alpha)
                    pygame.draw.circle(screen, color, (int(trail_x), int(trail_y)), 2)
                
                # Draw interceptor
                pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 3)
                # Interceptor tip
                pygame.draw.polygon(screen, WHITE, [
                    (self.x, self.y - 5),
                    (self.x - 2, self.y),
                    (self.x + 2, self.y)
                ])
            else:
                # Draw explosion
                radius = self.explosion_radius * (1 - self.explosion_timer / 10)
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), int(radius))
                pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), int(radius * 0.7))
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), int(radius * 0.4))
                
    def check_collision(self, missile: Missile) -> bool:
        if self.destroyed or missile.destroyed:
            return False
        if self.exploded:
            # Check explosion radius
            distance = math.sqrt((self.x - missile.x)**2 + (self.y - missile.y)**2)
            return distance < self.explosion_radius
        else:
            # Check direct collision
            distance = math.sqrt((self.x - missile.x)**2 + (self.y - missile.y)**2)
            return distance < 8

class Explosion:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.timer = 0
        self.max_timer = 15
        self.radius = 40
        
    def update(self):
        self.timer += 1
        
    def draw(self, screen):
        if self.timer < self.max_timer:
            progress = self.timer / self.max_timer
            radius = int(self.radius * (1 - progress * 0.5))
            alpha = int(255 * (1 - progress))
            
            # Explosion effect
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), radius)
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), int(radius * 0.7))
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), int(radius * 0.4))
            
    def is_finished(self) -> bool:
        return self.timer >= self.max_timer

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game objects
        self.cities = []
        self.missiles = []
        self.interceptors = []
        self.explosions = []
        
        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.missiles_launched = 0
        self.missiles_destroyed = 0
        
        # Timing
        self.missile_spawn_timer = 0
        self.missile_spawn_delay = 120  # Frames between missile spawns
        
        # Initialize cities
        self.init_cities()
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def init_cities(self):
        city_width = 40
        spacing = 60
        start_x = 100
        y = SCREEN_HEIGHT - 50
        
        for i in range(8):
            x = start_x + i * spacing
            self.cities.append(City(x, y))
            
    def spawn_missile(self):
        if random.random() < 0.3:  # 30% chance each frame when timer is ready
            start_x = random.randint(50, SCREEN_WIDTH - 50)
            target_city = random.choice([city for city in self.cities if not city.destroyed])
            if target_city:
                self.missiles.append(Missile(start_x, target_city.x + target_city.width//2, target_city.y))
                self.missiles_launched += 1
                
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.launch_interceptor(event.pos[0], event.pos[1])
                    
    def launch_interceptor(self, target_x: int, target_y: int):
        # Launch from bottom center of screen
        launcher_x = SCREEN_WIDTH // 2
        launcher_y = SCREEN_HEIGHT - 20
        
        self.interceptors.append(Interceptor(launcher_x, launcher_y, target_x, target_y))
        
    def update(self):
        # Spawn missiles
        self.missile_spawn_timer += 1
        if self.missile_spawn_timer >= self.missile_spawn_delay:
            self.spawn_missile()
            self.missile_spawn_timer = 0
            
        # Update missiles
        for missile in self.missiles[:]:
            missile.update()
            
            # Check collision with cities
            for city in self.cities:
                if missile.check_collision(city):
                    city.destroyed = True
                    missile.destroyed = True
                    self.explosions.append(Explosion(missile.x, missile.y))
                    self.lives -= 1
                    break
                    
            # Remove missiles that are off screen or destroyed
            if missile.y > SCREEN_HEIGHT + 50 or missile.destroyed:
                if missile in self.missiles:
                    self.missiles.remove(missile)
                    
        # Update interceptors
        for interceptor in self.interceptors[:]:
            interceptor.update()
            
            # Check collision with missiles
            for missile in self.missiles[:]:
                if interceptor.check_collision(missile):
                    missile.destroyed = True
                    interceptor.destroyed = True
                    self.explosions.append(Explosion(missile.x, missile.y))
                    self.score += 100
                    self.missiles_destroyed += 1
                    break
                    
            # Remove destroyed interceptors
            if interceptor.destroyed:
                if interceptor in self.interceptors:
                    self.interceptors.remove(interceptor)
                    
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
                
        # Check game over
        if self.lives <= 0:
            self.game_over()
            
        # Level progression
        if self.missiles_destroyed >= self.level * 10:
            self.level += 1
            self.missile_spawn_delay = max(30, self.missile_spawn_delay - 10)
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw ground
        pygame.draw.rect(self.screen, DARK_GREEN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        
        # Draw launcher
        launcher_x = SCREEN_WIDTH // 2
        launcher_y = SCREEN_HEIGHT - 20
        pygame.draw.rect(self.screen, GRAY, (launcher_x - 10, launcher_y - 15, 20, 15))
        pygame.draw.rect(self.screen, DARK_GREEN, (launcher_x - 8, launcher_y - 13, 16, 11))
        
        # Draw game objects
        for city in self.cities:
            city.draw(self.screen)
            
        for missile in self.missiles:
            missile.draw(self.screen)
            
        for interceptor in self.interceptors:
            interceptor.draw(self.screen)
            
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
        instructions = [
            "Click to launch interceptors",
            "Defend your cities!",
            f"Missiles destroyed: {self.missiles_destroyed}"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 250, 10 + i * 25))
            
    def game_over(self):
        game_over_text = self.font.render("GAME OVER", True, RED)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.small_font.render("Press R to restart or Q to quit", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(final_score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart game
                        waiting = False
                    elif event.key == pygame.K_q:
                        self.running = False
                        waiting = False
                        
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run() 