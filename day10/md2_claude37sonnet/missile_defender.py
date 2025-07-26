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

class City:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.destroyed = False
        self.health = 100
        
    def draw(self, screen):
        if not self.destroyed:
            # City building
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
            # Windows
            for i in range(3):
                for j in range(2):
                    window_x = self.x + 5 + i * 7
                    window_y = self.y + 5 + j * 7
                    pygame.draw.rect(screen, YELLOW, (window_x, window_y, 4, 4))
        else:
            # Destroyed city (rubble)
            pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
            # Rubble details
            for i in range(5):
                rubble_x = self.x + random.randint(0, self.width - 5)
                rubble_y = self.y + random.randint(0, self.height - 5)
                pygame.draw.circle(screen, DARK_GREEN, (rubble_x, rubble_y), 2)

class MissileLauncher:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 30
        self.reload_time = 0
        self.reload_delay = 30  # frames between shots
        
    def draw(self, screen):
        # Launcher base
        pygame.draw.rect(screen, DARK_GREEN, (self.x, self.y, self.width, self.height))
        # Launcher barrel
        pygame.draw.rect(screen, GRAY, (self.x + 5, self.y - 10, 10, 15))
        # Radar dish
        pygame.draw.circle(screen, BLUE, (self.x + self.width // 2, self.y + 5), 8)
        
    def can_fire(self) -> bool:
        return self.reload_time <= 0
        
    def fire(self):
        if self.can_fire():
            self.reload_time = self.reload_delay
            return True
        return False
        
    def update(self):
        if self.reload_time > 0:
            self.reload_time -= 1

class Missile:
    def __init__(self, x: int, y: int, target_x: int, target_y: int, speed: float, is_defense: bool = False):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.is_defense = is_defense
        self.exploded = False
        self.explosion_radius = 0
        self.max_explosion_radius = 30
        self.explosion_duration = 0
        self.max_explosion_duration = 20
        
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
        if not self.exploded:
            self.x += self.dx
            self.y += self.dy
        else:
            self.explosion_duration += 1
            if self.explosion_duration < self.max_explosion_duration:
                self.explosion_radius = (self.explosion_duration / self.max_explosion_duration) * self.max_explosion_radius
                
    def draw(self, screen):
        if not self.exploded:
            # Missile body
            color = GREEN if self.is_defense else RED
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)
            # Missile trail
            trail_length = 10
            for i in range(1, trail_length + 1):
                alpha = 255 - (i * 255 // trail_length)
                trail_color = (*color, alpha)
                trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, trail_color, (3, 3), 2)
                trail_x = int(self.x - self.dx * i * 0.5)
                trail_y = int(self.y - self.dy * i * 0.5)
                screen.blit(trail_surface, (trail_x - 3, trail_y - 3))
        else:
            # Explosion
            if self.explosion_duration < self.max_explosion_duration:
                alpha = 255 - (self.explosion_duration * 255 // self.max_explosion_duration)
                explosion_color = (*ORANGE, alpha)
                explosion_surface = pygame.Surface((self.explosion_radius * 2, self.explosion_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(explosion_surface, explosion_color, (self.explosion_radius, self.explosion_radius), self.explosion_radius)
                screen.blit(explosion_surface, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))
                
    def check_collision(self, other_missile) -> bool:
        if self.exploded or other_missile.exploded:
            return False
        distance = math.sqrt((self.x - other_missile.x)**2 + (self.y - other_missile.y)**2)
        return distance < 10
        
    def check_city_hit(self, city) -> bool:
        if self.exploded or city.destroyed:
            return False
        return (self.x >= city.x and self.x <= city.x + city.width and 
                self.y >= city.y and self.y <= city.y + city.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defender")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.level = 1
        self.score = 0
        self.cities = []
        self.launchers = []
        self.attack_missiles = []
        self.defense_missiles = []
        self.game_state = "playing"  # "playing", "game_over", "victory"
        
        self.setup_level()
        
    def setup_level(self):
        # Clear existing objects
        self.cities.clear()
        self.launchers.clear()
        self.attack_missiles.clear()
        self.defense_missiles.clear()
        
        # Setup based on level
        if self.level == 1:
            # Level 1: 1 launcher, 3 cities, slow missiles
            self.setup_cities(3)
            self.setup_launchers(1)
            self.missile_spawn_rate = 120  # frames between missile spawns
            self.missile_speed = 2.0
            self.missiles_per_wave = 5
        elif self.level == 2:
            # Level 2: 1 launcher, 4 cities, slightly faster
            self.setup_cities(4)
            self.setup_launchers(1)
            self.missile_spawn_rate = 100
            self.missile_speed = 2.5
            self.missiles_per_wave = 6
        elif self.level == 3:
            # Level 3: 2 launchers, 5 cities, faster missiles
            self.setup_cities(5)
            self.setup_launchers(2)
            self.missile_spawn_rate = 80
            self.missile_speed = 3.0
            self.missiles_per_wave = 7
        elif self.level == 4:
            # Level 4: 2 launchers, 6 cities, even faster
            self.setup_cities(6)
            self.setup_launchers(2)
            self.missile_spawn_rate = 60
            self.missile_speed = 3.5
            self.missiles_per_wave = 8
        elif self.level == 5:
            # Level 5: 3 launchers, 7 cities, very fast
            self.setup_cities(7)
            self.setup_launchers(3)
            self.missile_spawn_rate = 50
            self.missile_speed = 4.0
            self.missiles_per_wave = 10
        else:
            # Victory!
            self.game_state = "victory"
            return
            
        self.missile_spawn_timer = 0
        self.missiles_spawned = 0
        self.wave_complete = False
        
    def setup_cities(self, num_cities: int):
        city_width = 30
        spacing = (SCREEN_WIDTH - 100) // (num_cities + 1)
        start_x = 50
        
        for i in range(num_cities):
            x = start_x + i * spacing
            y = SCREEN_HEIGHT - 50
            self.cities.append(City(x, y))
            
    def setup_launchers(self, num_launchers: int):
        launcher_width = 20
        spacing = (SCREEN_WIDTH - 100) // (num_launchers + 1)
        start_x = 50
        
        for i in range(num_launchers):
            x = start_x + i * spacing
            y = SCREEN_HEIGHT - 100
            self.launchers.append(MissileLauncher(x, y))
            
    def spawn_attack_missile(self):
        if self.missiles_spawned >= self.missiles_per_wave:
            return
            
        # Choose random city as target
        alive_cities = [city for city in self.cities if not city.destroyed]
        if not alive_cities:
            return
            
        target_city = random.choice(alive_cities)
        target_x = target_city.x + target_city.width // 2
        target_y = target_city.y + target_city.height // 2
        
        # Spawn from top of screen
        spawn_x = random.randint(50, SCREEN_WIDTH - 50)
        spawn_y = -20
        
        missile = Missile(spawn_x, spawn_y, target_x, target_y, self.missile_speed, False)
        self.attack_missiles.append(missile)
        self.missiles_spawned += 1
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.game_state in ["game_over", "victory"]:
                    self.__init__()  # Restart game
                    
        # Mouse input for firing missiles
        if self.game_state == "playing":
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:  # Left click
                for launcher in self.launchers:
                    if launcher.can_fire():
                        defense_missile = Missile(
                            launcher.x + launcher.width // 2,
                            launcher.y,
                            mouse_pos[0],
                            mouse_pos[1],
                            5.0,  # Defense missiles are faster
                            True
                        )
                        self.defense_missiles.append(defense_missile)
                        launcher.fire()
                        
        return True
        
    def update(self):
        if self.game_state != "playing":
            return
            
        # Update launchers
        for launcher in self.launchers:
            launcher.update()
            
        # Spawn attack missiles
        self.missile_spawn_timer += 1
        if self.missile_spawn_timer >= self.missile_spawn_rate:
            self.spawn_attack_missile()
            self.missile_spawn_timer = 0
            
        # Update missiles
        for missile in self.attack_missiles[:]:
            missile.update()
            if missile.exploded and missile.explosion_duration >= missile.max_explosion_duration:
                self.attack_missiles.remove(missile)
            elif missile.y > SCREEN_HEIGHT + 50:
                self.attack_missiles.remove(missile)
                
        for missile in self.defense_missiles[:]:
            missile.update()
            if missile.exploded and missile.explosion_duration >= missile.max_explosion_duration:
                self.defense_missiles.remove(missile)
            elif missile.y < -50:
                self.defense_missiles.remove(missile)
                
        # Check missile collisions
        for defense_missile in self.defense_missiles[:]:
            for attack_missile in self.attack_missiles[:]:
                if defense_missile.check_collision(attack_missile):
                    defense_missile.exploded = True
                    attack_missile.exploded = True
                    self.score += 100
                    
        # Check city hits
        for missile in self.attack_missiles[:]:
            for city in self.cities:
                if missile.check_city_hit(city):
                    city.destroyed = True
                    missile.exploded = True
                    self.score -= 200
                    
        # Check level completion
        if self.missiles_spawned >= self.missiles_per_wave and len(self.attack_missiles) == 0:
            alive_cities = [city for city in self.cities if not city.destroyed]
            if alive_cities:
                self.level += 1
                self.setup_level()
            else:
                self.game_state = "game_over"
                
        # Check game over
        alive_cities = [city for city in self.cities if not city.destroyed]
        if not alive_cities:
            self.game_state = "game_over"
            
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
            
        # Draw missiles
        for missile in self.attack_missiles:
            missile.draw(self.screen)
        for missile in self.defense_missiles:
            missile.draw(self.screen)
            
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
        
    def draw_ui(self):
        # Level and score
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(level_text, (10, 10))
        self.screen.blit(score_text, (10, 50))
        
        # Cities remaining
        alive_cities = len([city for city in self.cities if not city.destroyed])
        cities_text = self.small_font.render(f"Cities: {alive_cities}/{len(self.cities)}", True, WHITE)
        self.screen.blit(cities_text, (10, 90))
        
        # Instructions
        if self.game_state == "playing":
            instructions = self.small_font.render("Click to fire missiles at incoming threats!", True, WHITE)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 10))
            
        # Game over screen
        elif self.game_state == "game_over":
            game_over_text = self.font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            
        # Victory screen
        elif self.game_state == "victory":
            victory_text = self.font.render("VICTORY!", True, GREEN)
            congrats_text = self.font.render("Congratulations! You've defended all cities!", True, WHITE)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press SPACE to play again", True, WHITE)
            
            self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            self.screen.blit(congrats_text, (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
            
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