import pygame
import math
import random
import sys
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
BROWN = (139, 69, 19)

class Missile:
    def __init__(self, x: float, y: float, target_x: float, target_y: float, speed: float):
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
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else speed
    
    def update(self):
        if self.active:
            self.x += self.dx
            self.y += self.dy
    
    def draw(self, screen):
        if self.active:
            # Draw missile trail
            for i in range(5):
                trail_x = self.x - self.dx * i * 0.2
                trail_y = self.y - self.dy * i * 0.2
                pygame.draw.circle(screen, ORANGE, (int(trail_x), int(trail_y)), 2 - i)
            
            # Draw missile
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 4)
    
    def check_collision(self, x: float, y: float, radius: float) -> bool:
        if not self.active:
            return False
        distance = math.sqrt((self.x - x)**2 + (self.y - y)**2)
        return distance < radius

class Interceptor:
    def __init__(self, x: float, y: float, target_x: float, target_y: float, speed: float):
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
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else speed
    
    def update(self):
        if self.active:
            self.x += self.dx
            self.y += self.dy
    
    def draw(self, screen):
        if self.active:
            # Draw interceptor trail
            for i in range(3):
                trail_x = self.x - self.dx * i * 0.3
                trail_y = self.y - self.dy * i * 0.3
                pygame.draw.circle(screen, YELLOW, (int(trail_x), int(trail_y)), 3 - i)
            
            # Draw interceptor
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 5)
    
    def check_collision(self, x: float, y: float, radius: float) -> bool:
        if not self.active:
            return False
        distance = math.sqrt((self.x - x)**2 + (self.y - y)**2)
        return distance < radius

class City:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.destroyed = False
        self.size = 20
    
    def draw(self, screen):
        if not self.destroyed:
            # Draw city building
            pygame.draw.rect(screen, GRAY, (self.x - 10, self.y - 15, 20, 15))
            # Draw windows
            pygame.draw.rect(screen, YELLOW, (self.x - 8, self.y - 12, 4, 4))
            pygame.draw.rect(screen, YELLOW, (self.x + 4, self.y - 12, 4, 4))
            pygame.draw.rect(screen, YELLOW, (self.x - 8, self.y - 6, 4, 4))
            pygame.draw.rect(screen, YELLOW, (self.x + 4, self.y - 6, 4, 4))
        else:
            # Draw destroyed city
            pygame.draw.rect(screen, RED, (self.x - 10, self.y - 15, 20, 15))
            pygame.draw.line(screen, BLACK, (self.x - 10, self.y - 7), (self.x + 10, self.y - 7), 3)

class Launcher:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.cooldown = 0
        self.cooldown_time = 30  # frames between shots
    
    def can_fire(self) -> bool:
        return self.cooldown <= 0
    
    def fire(self, target_x: float, target_y: float, speed: float) -> Interceptor:
        if self.can_fire():
            self.cooldown = self.cooldown_time
            return Interceptor(self.x, self.y, target_x, target_y, speed)
        return None
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def draw(self, screen):
        # Draw launcher base
        pygame.draw.rect(screen, DARK_GREEN, (self.x - 15, self.y - 10, 30, 20))
        # Draw launcher barrel
        pygame.draw.rect(screen, BROWN, (self.x - 3, self.y - 20, 6, 20))

class Explosion:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.active = True
    
    def update(self):
        self.radius += 2
        if self.radius >= self.max_radius:
            self.active = False
    
    def draw(self, screen):
        if self.active:
            alpha = 255 - (self.radius / self.max_radius) * 255
            color = (255, 255, 0, int(alpha))
            # Create a surface for the explosion
            explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, color, (self.radius, self.radius), self.radius)
            screen.blit(explosion_surface, (self.x - self.radius, self.y - self.radius))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defender")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
    
    def reset_game(self):
        self.level = 1
        self.score = 0
        self.missiles: List[Missile] = []
        self.interceptors: List[Interceptor] = []
        self.explosions: List[Explosion] = []
        self.missile_spawn_timer = 0
        self.level_complete = False
        self.game_over = False
        self.game_won = False
        
        # Level configuration
        self.level_config = {
            1: {"cities": 3, "launchers": 1, "missile_speed": 2, "spawn_rate": 120, "missiles_per_level": 5},
            2: {"cities": 4, "launchers": 1, "missile_speed": 2.5, "spawn_rate": 100, "missiles_per_level": 6},
            3: {"cities": 4, "launchers": 2, "missile_speed": 3, "spawn_rate": 90, "missiles_per_level": 7},
            4: {"cities": 5, "launchers": 2, "missile_speed": 3.5, "spawn_rate": 80, "missiles_per_level": 8},
            5: {"cities": 5, "launchers": 3, "missile_speed": 4, "spawn_rate": 70, "missiles_per_level": 10}
        }
        
        self.setup_level()
    
    def setup_level(self):
        config = self.level_config.get(self.level, self.level_config[5])
        
        # Setup cities
        self.cities: List[City] = []
        city_spacing = SCREEN_WIDTH // (config["cities"] + 1)
        for i in range(config["cities"]):
            x = city_spacing * (i + 1)
            y = SCREEN_HEIGHT - 50
            self.cities.append(City(x, y))
        
        # Setup launchers
        self.launchers: List[Launcher] = []
        launcher_spacing = SCREEN_WIDTH // (config["launchers"] + 1)
        for i in range(config["launchers"]):
            x = launcher_spacing * (i + 1)
            y = SCREEN_HEIGHT - 100
            self.launchers.append(Launcher(x, y))
        
        # Reset level variables
        self.missiles_remaining = config["missiles_per_level"]
        self.missiles_destroyed = 0
        self.missile_speed = config["missile_speed"]
        self.spawn_rate = config["spawn_rate"]
        self.interceptor_speed = 6
        
        # Clear existing objects
        self.missiles.clear()
        self.interceptors.clear()
        self.explosions.clear()
        self.missile_spawn_timer = 0
    
    def spawn_missile(self):
        if self.missiles_remaining > 0:
            # Choose a random city as target
            target_city = random.choice([city for city in self.cities if not city.destroyed])
            if target_city:
                # Spawn from top of screen
                x = random.randint(50, SCREEN_WIDTH - 50)
                missile = Missile(x, 0, target_city.x, target_city.y, self.missile_speed)
                self.missiles.append(missile)
                self.missiles_remaining -= 1
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.game_over and not self.game_won:
                    # Fire interceptor at mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for launcher in self.launchers:
                        interceptor = launcher.fire(mouse_x, mouse_y, self.interceptor_speed)
                        if interceptor:
                            self.interceptors.append(interceptor)
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if self.game_over or self.game_won:
                        self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def update(self):
        if self.game_over or self.game_won:
            return
        
        # Update launchers
        for launcher in self.launchers:
            launcher.update()
        
        # Spawn missiles
        self.missile_spawn_timer += 1
        if self.missile_spawn_timer >= self.spawn_rate and self.missiles_remaining > 0:
            self.spawn_missile()
            self.missile_spawn_timer = 0
        
        # Update missiles
        for missile in self.missiles[:]:
            missile.update()
            
            # Check if missile hit ground
            if missile.y >= SCREEN_HEIGHT:
                missile.active = False
                # Find closest city and destroy it
                closest_city = None
                min_distance = float('inf')
                for city in self.cities:
                    if not city.destroyed:
                        distance = abs(missile.x - city.x)
                        if distance < min_distance:
                            min_distance = distance
                            closest_city = city
                
                if closest_city:
                    closest_city.destroyed = True
                    self.score -= 100
        
        # Update interceptors
        for interceptor in self.interceptors[:]:
            interceptor.update()
            
            # Check collision with missiles
            for missile in self.missiles[:]:
                if missile.active and interceptor.active:
                    if interceptor.check_collision(missile.x, missile.y, 8):
                        # Create explosion
                        explosion = Explosion(missile.x, missile.y)
                        self.explosions.append(explosion)
                        
                        # Destroy both objects
                        missile.active = False
                        interceptor.active = False
                        self.missiles_destroyed += 1
                        self.score += 50
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)
        
        # Remove inactive objects
        self.missiles = [m for m in self.missiles if m.active]
        self.interceptors = [i for i in self.interceptors if i.active]
        
        # Check level completion
        if self.missiles_remaining == 0 and len(self.missiles) == 0:
            self.level_complete = True
            self.score += 200 * len([city for city in self.cities if not city.destroyed])
            
            if self.level >= 5:
                self.game_won = True
            else:
                self.level += 1
                self.setup_level()
        
        # Check game over
        if all(city.destroyed for city in self.cities):
            self.game_over = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw ground
        pygame.draw.rect(self.screen, DARK_GREEN, (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))
        
        # Draw cities
        for city in self.cities:
            city.draw(self.screen)
        
        # Draw launchers
        for launcher in self.launchers:
            launcher.draw(self.screen)
        
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
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Draw missiles remaining
        missiles_text = self.small_font.render(f"Missiles: {self.missiles_remaining}", True, WHITE)
        self.screen.blit(missiles_text, (10, 90))
        
        # Draw cities remaining
        cities_remaining = len([city for city in self.cities if not city.destroyed])
        cities_text = self.small_font.render(f"Cities: {cities_remaining}", True, WHITE)
        self.screen.blit(cities_text, (10, 110))
        
        # Draw instructions
        if not self.game_over and not self.game_won:
            instructions = self.small_font.render("Click to fire interceptors!", True, WHITE)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - 100, 10))
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over_screen()
        
        # Draw win screen
        if self.game_won:
            self.draw_win_screen()
        
        # Draw level complete screen
        if self.level_complete and not self.game_won:
            self.draw_level_complete_screen()
    
    def draw_game_over_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_win_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Congratulations text
        congrats_text = self.font.render("CONGRATULATIONS!", True, GREEN)
        text_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(congrats_text, text_rect)
        
        # Win message
        win_text = self.font.render("You've defended all cities!", True, WHITE)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(win_text, win_rect)
        
        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(score_text, score_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to play again or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_level_complete_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Level complete text
        complete_text = self.font.render(f"Level {self.level - 1} Complete!", True, GREEN)
        text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(complete_text, text_rect)
        
        # Continue instruction
        continue_text = self.small_font.render("Press any key to continue...", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 