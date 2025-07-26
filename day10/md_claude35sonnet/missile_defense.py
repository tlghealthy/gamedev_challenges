import pygame
import math
import random
from typing import List, Tuple, Optional
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
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
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
LIGHT_BLUE = (173, 216, 230)

class City:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.destroyed = False
        self.health = 100
        self.max_health = 100
        self.damage_animation = 0
        
    def take_damage(self, damage: int):
        if not self.destroyed:
            self.health -= damage
            self.damage_animation = 10
            if self.health <= 0:
                self.destroyed = True
                self.health = 0
        
    def draw(self, screen):
        if not self.destroyed:
            # Health bar
            health_ratio = self.health / self.max_health
            health_width = int(self.width * health_ratio)
            pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_width, 5))
            
            # City building with damage animation
            color = GRAY
            if self.damage_animation > 0:
                color = RED
                self.damage_animation -= 1
                
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            
            # Windows
            for i in range(4):
                for j in range(3):
                    window_x = self.x + 5 + i * 10
                    window_y = self.y + 5 + j * 10
                    window_color = YELLOW if random.random() > 0.3 else BLACK  # Some windows dark
                    pygame.draw.rect(screen, window_color, (window_x, window_y, 6, 6))
            
            # Roof
            pygame.draw.rect(screen, DARK_GREEN, (self.x - 3, self.y, self.width + 6, 8))
            
            # Chimney
            pygame.draw.rect(screen, BROWN, (self.x + self.width - 8, self.y - 15, 6, 15))
        else:
            # Destroyed city (rubble)
            pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
            # Rubble pieces
            for _ in range(8):
                rubble_x = self.x + random.randint(0, self.width - 5)
                rubble_y = self.y + random.randint(0, self.height - 5)
                rubble_size = random.randint(2, 5)
                pygame.draw.rect(screen, GRAY, (rubble_x, rubble_y, rubble_size, rubble_size))

class MissileLauncher:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 35
        self.missiles: List[PlayerMissile] = []
        self.reload_time = 0
        self.reload_delay = 15  # frames between shots
        self.ammo = 10
        self.max_ammo = 10
        self.reload_cooldown = 0
        self.reload_duration = 120  # frames to reload
        
    def draw(self, screen):
        # Base
        pygame.draw.rect(screen, DARK_GREEN, (self.x - 8, self.y + self.height, 41, 12))
        
        # Launcher body
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        
        # Barrel
        pygame.draw.rect(screen, BLACK, (self.x + 8, self.y - 15, 9, 20))
        
        # Ammo indicator
        ammo_ratio = self.ammo / self.max_ammo
        ammo_width = int(30 * ammo_ratio)
        pygame.draw.rect(screen, RED, (self.x - 5, self.y + self.height + 15, 35, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.y + self.height + 15, ammo_width, 5))
        
        # Reload indicator
        if self.reload_cooldown > 0:
            reload_ratio = 1 - (self.reload_cooldown / self.reload_duration)
            reload_width = int(35 * reload_ratio)
            pygame.draw.rect(screen, CYAN, (self.x - 5, self.y + self.height + 22, reload_width, 3))
        
    def fire(self):
        if self.reload_time <= 0 and self.ammo > 0 and self.reload_cooldown <= 0:
            missile = PlayerMissile(self.x + 12, self.y - 10)
            self.missiles.append(missile)
            self.reload_time = self.reload_delay
            self.ammo -= 1
            
            # Start reload if out of ammo
            if self.ammo <= 0:
                self.reload_cooldown = self.reload_duration
            
    def update(self):
        if self.reload_time > 0:
            self.reload_time -= 1
            
        if self.reload_cooldown > 0:
            self.reload_cooldown -= 1
            if self.reload_cooldown <= 0:
                self.ammo = self.max_ammo
            
        # Update missiles
        for missile in self.missiles[:]:
            missile.update()
            if missile.y < -10:
                self.missiles.remove(missile)

class PlayerMissile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.speed = 10
        self.width = 6
        self.height = 15
        self.trail_particles = []
        
    def update(self):
        self.y -= self.speed
        
        # Add trail particles
        if random.random() > 0.3:
            self.trail_particles.append({
                'x': self.x + random.randint(-2, 2),
                'y': self.y + self.height + random.randint(0, 5),
                'life': 10
            })
        
        # Update trail particles
        for particle in self.trail_particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)
        
    def draw(self, screen):
        # Trail particles
        for particle in self.trail_particles:
            alpha = int((particle['life'] / 10) * 255)
            color = (255, 165, 0, alpha)
            trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, color, (2, 2), 2)
            screen.blit(trail_surface, (particle['x'], particle['y']))
        
        # Missile body
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        
        # Missile tip
        pygame.draw.polygon(screen, RED, [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width // 2, self.y - 10)
        ])
        
        # Exhaust trail
        pygame.draw.rect(screen, ORANGE, (self.x + 1, self.y + self.height, 4, 8))

class EnemyMissile:
    def __init__(self, x: int, y: int, target_x: int, target_y: int, speed: float = 3):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.width = 8
        self.height = 20
        self.trail_particles = []
        
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
        
        # Add trail particles
        if random.random() > 0.4:
            self.trail_particles.append({
                'x': self.x + random.randint(-3, 3),
                'y': self.y + self.height + random.randint(0, 8),
                'life': 15
            })
        
        # Update trail particles
        for particle in self.trail_particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)
        
    def draw(self, screen):
        # Trail particles
        for particle in self.trail_particles:
            alpha = int((particle['life'] / 15) * 255)
            color = (255, 0, 0, alpha)
            trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, color, (3, 3), 3)
            screen.blit(trail_surface, (particle['x'], particle['y']))
        
        # Missile body
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        
        # Missile tip
        pygame.draw.polygon(screen, WHITE, [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width // 2, self.y - 12)
        ])
        
        # Fins
        pygame.draw.rect(screen, DARK_RED, (self.x - 2, self.y + self.height - 8, 4, 6))
        pygame.draw.rect(screen, DARK_RED, (self.x + self.width - 2, self.y + self.height - 8, 4, 6))

class Explosion:
    def __init__(self, x: int, y: int, size: int = 30):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = size
        self.life = 25
        self.particles = []
        
        # Create explosion particles
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(15, 25),
                'color': random.choice([YELLOW, ORANGE, RED, WHITE])
            })
        
    def update(self):
        self.radius += 1
        self.life -= 1
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
    def draw(self, screen):
        if self.life > 0:
            # Main explosion
            alpha = int((self.life / 25) * 255)
            color = (255, 255, 0, alpha)
            explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, color, (self.radius, self.radius), self.radius)
            screen.blit(explosion_surface, (self.x - self.radius, self.y - self.radius))
            
            # Particles
            for particle in self.particles:
                if particle['life'] > 0:
                    alpha = int((particle['life'] / 25) * 255)
                    color = (*particle['color'][:3], alpha)
                    particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, color, (2, 2), 2)
                    screen.blit(particle_surface, (particle['x'] - 2, particle['y'] - 2))

class PowerUp:
    def __init__(self, x: int, y: int, power_type: str):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.power_type = power_type  # 'rapid_fire', 'shield', 'multi_shot'
        self.life = 300  # frames
        self.bob_offset = 0
        
    def update(self):
        self.life -= 1
        self.bob_offset = math.sin(time.time() * 3) * 3
        
    def draw(self, screen):
        if self.power_type == 'rapid_fire':
            color = YELLOW
        elif self.power_type == 'shield':
            color = CYAN
        else:  # multi_shot
            color = PURPLE
            
        pygame.draw.rect(screen, color, (self.x, self.y + self.bob_offset, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y + self.bob_offset, self.width, self.height), 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defense - Arcade Classic")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game objects
        self.cities = self.create_cities()
        self.launchers = self.create_launchers()
        self.enemy_missiles: List[EnemyMissile] = []
        self.explosions: List[Explosion] = []
        self.power_ups: List[PowerUp] = []
        
        # Game state
        self.score = 0
        self.level = 1
        self.missiles_per_wave = 3
        self.wave_timer = 0
        self.wave_delay = 180  # frames between waves
        self.game_over = False
        self.paused = False
        
        # Power-up effects
        self.rapid_fire_timer = 0
        self.shield_timer = 0
        self.multi_shot_timer = 0
        
        # Input
        self.mouse_pos = (0, 0)
        self.keys_pressed = set()
        
        # Background stars
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) 
                     for _ in range(100)]
        
    def create_cities(self) -> List[City]:
        cities = []
        city_spacing = SCREEN_WIDTH // 7
        for i in range(6):
            x = city_spacing * (i + 1) - 25
            y = SCREEN_HEIGHT - 60
            cities.append(City(x, y))
        return cities
    
    def create_launchers(self) -> List[MissileLauncher]:
        launchers = []
        launcher_spacing = SCREEN_WIDTH // 5
        for i in range(4):
            x = launcher_spacing * (i + 1) - 12
            y = SCREEN_HEIGHT - 120
            launchers.append(MissileLauncher(x, y))
        return launchers
    
    def spawn_enemy_missile(self):
        if len(self.enemy_missiles) < self.missiles_per_wave:
            # Choose a random city as target
            alive_cities = [city for city in self.cities if not city.destroyed]
            if alive_cities:
                target_city = random.choice(alive_cities)
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = -30
                speed = 2 + (self.level * 0.5)  # Speed increases with level
                missile = EnemyMissile(x, y, target_city.x + target_city.width // 2, target_city.y, speed)
                self.enemy_missiles.append(missile)
    
    def spawn_power_up(self):
        if random.random() < 0.01:  # 1% chance per frame
            power_types = ['rapid_fire', 'shield', 'multi_shot']
            power_type = random.choice(power_types)
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = -30
            power_up = PowerUp(x, y, power_type)
            self.power_ups.append(power_up)
    
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
                        
                        # Check if shield is active
                        if self.shield_timer > 0:
                            # Create explosion
                            explosion = Explosion(enemy_missile.x + enemy_missile.width // 2, 
                                                enemy_missile.y + enemy_missile.height // 2)
                            self.explosions.append(explosion)
                            self.enemy_missiles.remove(enemy_missile)
                            self.score += 50
                        else:
                            # Create explosion
                            explosion = Explosion(enemy_missile.x + enemy_missile.width // 2, 
                                                enemy_missile.y + enemy_missile.height // 2, 50)
                            self.explosions.append(explosion)
                            
                            # Damage city
                            city.take_damage(25)
                            self.enemy_missiles.remove(enemy_missile)
                        break
        
        # Check power-ups vs launchers
        for power_up in self.power_ups[:]:
            for launcher in self.launchers:
                if (power_up.x < launcher.x + launcher.width and
                    power_up.x + power_up.width > launcher.x and
                    power_up.y < launcher.y + launcher.height and
                    power_up.y + power_up.height > launcher.y):
                    
                    # Apply power-up effect
                    if power_up.power_type == 'rapid_fire':
                        self.rapid_fire_timer = 300  # 5 seconds
                    elif power_up.power_type == 'shield':
                        self.shield_timer = 600  # 10 seconds
                    else:  # multi_shot
                        self.multi_shot_timer = 450  # 7.5 seconds
                    
                    self.power_ups.remove(power_up)
                    break
        
        # Check if all cities are destroyed
        if all(city.destroyed for city in self.cities):
            self.game_over = True
    
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Update launchers
        for launcher in self.launchers:
            launcher.update()
        
        # Update enemy missiles
        for missile in self.enemy_missiles[:]:
            missile.update()
            if missile.y > SCREEN_HEIGHT + 30:
                self.enemy_missiles.remove(missile)
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.life <= 0:
                self.explosions.remove(explosion)
        
        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.life <= 0:
                self.power_ups.remove(power_up)
        
        # Update power-up timers
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.multi_shot_timer > 0:
            self.multi_shot_timer -= 1
        
        # Spawn enemy missiles
        self.wave_timer += 1
        if self.wave_timer >= self.wave_delay:
            self.spawn_enemy_missile()
            if len(self.enemy_missiles) >= self.missiles_per_wave:
                self.wave_timer = 0
                self.level += 1
                self.missiles_per_wave = min(3 + self.level, 12)
                self.wave_delay = max(60, 180 - self.level * 15)
        
        # Spawn power-ups
        self.spawn_power_up()
        
        # Check collisions
        self.check_collisions()
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(self.screen, WHITE, star, 1)
        
        # Draw ground
        pygame.draw.rect(self.screen, DARK_GREEN, (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))
        
        # Draw shield effect
        if self.shield_timer > 0:
            shield_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int((self.shield_timer / 600) * 50)
            pygame.draw.rect(shield_surface, (0, 255, 255, alpha), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(shield_surface, (0, 0))
        
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
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        cities_text = font.render(f"Cities: {sum(1 for city in self.cities if not city.destroyed)}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        self.screen.blit(cities_text, (10, 90))
        
        # Draw power-up indicators
        y_offset = 130
        if self.rapid_fire_timer > 0:
            rapid_text = font.render(f"Rapid Fire: {self.rapid_fire_timer // 60 + 1}s", True, YELLOW)
            self.screen.blit(rapid_text, (10, y_offset))
            y_offset += 30
        
        if self.shield_timer > 0:
            shield_text = font.render(f"Shield: {self.shield_timer // 60 + 1}s", True, CYAN)
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 30
        
        if self.multi_shot_timer > 0:
            multi_text = font.render(f"Multi Shot: {self.multi_shot_timer // 60 + 1}s", True, PURPLE)
            self.screen.blit(multi_text, (10, y_offset))
        
        if self.game_over:
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to restart", True, WHITE)
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        
        if self.paused:
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render("PAUSED", True, WHITE)
            resume_text = font.render("Press P to resume", True, WHITE)
            
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.paused:
                if event.button == 1:  # Left click
                    # Find closest launcher to mouse
                    mouse_x, mouse_y = event.pos
                    closest_launcher = min(self.launchers, 
                                         key=lambda l: abs(l.x - mouse_x))
                    
                    # Apply rapid fire effect
                    if self.rapid_fire_timer > 0:
                        closest_launcher.reload_delay = 5
                    else:
                        closest_launcher.reload_delay = 15
                    
                    closest_launcher.fire()
                    
                    # Multi-shot effect
                    if self.multi_shot_timer > 0:
                        # Fire from adjacent launchers too
                        for launcher in self.launchers:
                            if launcher != closest_launcher:
                                if abs(launcher.x - closest_launcher.x) < 200:  # Within range
                                    launcher.fire()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Restart game
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
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