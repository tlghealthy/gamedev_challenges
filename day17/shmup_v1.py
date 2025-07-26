import pygame
import random
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import colorsys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GAME_DURATION = 600  # 10 minutes in seconds

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
PURPLE = (255, 50, 255)
CYAN = (50, 255, 255)

@dataclass
class Entity:
    x: float
    y: float
    dx: float = 0
    dy: float = 0
    radius: float = 10
    color: Tuple[int, int, int] = WHITE
    hp: int = 1
    
class Player(Entity):
    def __init__(self):
        super().__init__(WIDTH//2, HEIGHT-50, radius=12, color=CYAN, hp=5)
        self.shoot_cooldown = 0
        self.invulnerable = 0
        
    def update(self, dt):
        keys = pygame.key.get_pressed()
        speed = 300 * dt
        if keys[pygame.K_LEFT]: self.x = max(self.radius, self.x - speed)
        if keys[pygame.K_RIGHT]: self.x = min(WIDTH - self.radius, self.x + speed)
        if keys[pygame.K_UP]: self.y = max(self.radius, self.y - speed)
        if keys[pygame.K_DOWN]: self.y = min(HEIGHT - self.radius, self.y + speed)
        
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        
    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            bullets.append(Bullet(self.x, self.y - self.radius, 0, -500, self.radius//2, GREEN, 1, True))
            self.shoot_cooldown = 0.1

class Enemy(Entity):
    def __init__(self, x, y, enemy_type="basic"):
        self.type = enemy_type
        self.time = 0
        self.shoot_timer = random.uniform(0.5, 2.0)
        self.pattern_phase = random.uniform(0, math.pi * 2)
        
        # Randomize attributes based on type
        if enemy_type == "basic":
            super().__init__(x, y, 0, random.uniform(50, 150), 
                           radius=random.randint(8, 15),
                           color=self._random_color(0.0, 0.3),  # Red hues
                           hp=1)
        elif enemy_type == "heavy":
            super().__init__(x, y, 0, random.uniform(30, 80),
                           radius=random.randint(20, 30),
                           color=self._random_color(0.6, 0.8),  # Blue hues
                           hp=random.randint(3, 5))
        elif enemy_type == "sine":
            super().__init__(x, y, random.uniform(50, 150), random.uniform(40, 100),
                           radius=random.randint(10, 18),
                           color=self._random_color(0.1, 0.2),  # Orange hues
                           hp=2)
            self.base_x = x
            self.amplitude = random.uniform(50, 150)
            self.frequency = random.uniform(1, 3)
        elif enemy_type == "spiral":
            super().__init__(x, y, 0, 0,
                           radius=random.randint(12, 20),
                           color=self._random_color(0.8, 0.95),  # Purple hues
                           hp=random.randint(2, 4))
            self.angle = random.uniform(0, math.pi * 2)
            self.spiral_speed = random.uniform(100, 200)
            self.angle_speed = random.uniform(2, 4)
            
    def _random_color(self, hue_min, hue_max):
        h = random.uniform(hue_min, hue_max)
        s = random.uniform(0.6, 1.0)
        v = random.uniform(0.7, 1.0)
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return tuple(int(c * 255) for c in rgb)
        
    def update(self, dt, player, bullets):
        self.time += dt
        self.shoot_timer -= dt
        
        if self.type == "basic":
            self.y += self.dy * dt
        elif self.type == "heavy":
            self.y += self.dy * dt
            # Track player slowly
            if player.x > self.x + 5:
                self.x += 30 * dt
            elif player.x < self.x - 5:
                self.x -= 30 * dt
        elif self.type == "sine":
            self.y += self.dy * dt
            self.x = self.base_x + math.sin(self.time * self.frequency + self.pattern_phase) * self.amplitude
        elif self.type == "spiral":
            self.angle += self.angle_speed * dt
            self.x += math.cos(self.angle) * self.spiral_speed * dt
            self.y += math.sin(self.angle) * self.spiral_speed * dt + 50 * dt
            
        # Shoot patterns
        if self.shoot_timer <= 0 and self.y < HEIGHT - 100:
            self._shoot_pattern(bullets, player)
            self.shoot_timer = random.uniform(0.8, 2.5)
            
    def _shoot_pattern(self, bullets, player):
        if self.type == "basic":
            # Single aimed shot
            angle = math.atan2(player.y - self.y, player.x - self.x)
            speed = random.uniform(200, 300)
            bullets.append(Bullet(self.x, self.y, 
                                math.cos(angle) * speed, 
                                math.sin(angle) * speed,
                                4, RED, 1, False))
        elif self.type == "heavy":
            # Spread shot
            for i in range(5):
                angle = math.pi/2 + (i - 2) * 0.3
                speed = random.uniform(150, 250)
                bullets.append(Bullet(self.x, self.y,
                                    math.cos(angle) * speed,
                                    math.sin(angle) * speed,
                                    5, YELLOW, 1, False))
        elif self.type == "sine":
            # Circular burst
            num_bullets = random.randint(6, 10)
            for i in range(num_bullets):
                angle = (i / num_bullets) * math.pi * 2
                speed = random.uniform(100, 200)
                bullets.append(Bullet(self.x, self.y,
                                    math.cos(angle) * speed,
                                    math.sin(angle) * speed,
                                    3, PURPLE, 1, False))
        elif self.type == "spiral":
            # Spiral pattern
            for i in range(3):
                angle = self.angle + i * (math.pi * 2 / 3)
                speed = random.uniform(150, 250)
                bullets.append(Bullet(self.x, self.y,
                                    math.cos(angle) * speed,
                                    math.sin(angle) * speed,
                                    4, (255, 128, 0), 1, False))

class Bullet(Entity):
    def __init__(self, x, y, dx, dy, radius, color, damage, friendly):
        super().__init__(x, y, dx, dy, radius, color)
        self.damage = damage
        self.friendly = friendly
        
    def update(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt

class Particle:
    def __init__(self, x, y, dx, dy, color, lifetime):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.color = color
        self.lifetime = lifetime
        self.initial_lifetime = lifetime
        self.radius = random.uniform(1, 4)
        
    def update(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.lifetime -= dt
        self.dy += 200 * dt  # Gravity
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = self.lifetime / self.initial_lifetime
            radius = self.radius * alpha
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(radius))

class WaveGenerator:
    def __init__(self):
        self.wave_timer = 0
        self.wave_number = 0
        self.difficulty = 1.0
        
    def update(self, dt, game_time, enemies):
        self.wave_timer -= dt
        self.difficulty = 1.0 + (game_time / 60)  # Increase difficulty every minute
        
        if self.wave_timer <= 0:
            self._generate_wave(enemies)
            self.wave_timer = random.uniform(3, 6) / self.difficulty
            self.wave_number += 1
            
    def _generate_wave(self, enemies):
        wave_types = ["basic", "mixed", "heavy", "sine", "spiral", "combined"]
        weights = [30, 20, 15, 15, 10, 10]
        wave_type = random.choices(wave_types, weights=weights)[0]
        
        if wave_type == "basic":
            # Line of basic enemies
            num = random.randint(3, 6 + int(self.difficulty))
            spacing = WIDTH / (num + 1)
            for i in range(num):
                enemies.append(Enemy(spacing * (i + 1), -30, "basic"))
                
        elif wave_type == "mixed":
            # Mix of enemy types
            for _ in range(random.randint(2, 4 + int(self.difficulty))):
                enemy_type = random.choice(["basic", "sine", "heavy"])
                x = random.uniform(50, WIDTH - 50)
                enemies.append(Enemy(x, -30, enemy_type))
                
        elif wave_type == "heavy":
            # Few heavy enemies
            for _ in range(random.randint(1, 2 + int(self.difficulty/2))):
                x = random.uniform(100, WIDTH - 100)
                enemies.append(Enemy(x, -50, "heavy"))
                
        elif wave_type == "sine":
            # Wave of sine enemies
            num = random.randint(2, 4 + int(self.difficulty/2))
            for i in range(num):
                x = WIDTH / 2 + (i - num/2) * 100
                enemies.append(Enemy(x, -30 - i * 30, "sine"))
                
        elif wave_type == "spiral":
            # Spiral enemies from sides
            for side in [-1, 1]:
                x = WIDTH/2 + side * WIDTH/3
                enemies.append(Enemy(x, -30, "spiral"))
                
        elif wave_type == "combined":
            # Boss-like formation
            # Center heavy
            enemies.append(Enemy(WIDTH/2, -50, "heavy"))
            # Supporting basics
            for dx in [-100, 100]:
                enemies.append(Enemy(WIDTH/2 + dx, -30, "basic"))
            # Side spirals
            if self.difficulty > 2:
                for side in [-200, 200]:
                    enemies.append(Enemy(WIDTH/2 + side, -80, "spiral"))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Procedural Shmup")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_time = 0
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game entities
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.wave_gen = WaveGenerator()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.player.shoot(self.bullets)
            
    def update(self, dt):
        self.game_time += dt
        
        # Update player
        self.player.update(dt)
        
        # Update wave generator
        self.wave_gen.update(dt, self.game_time, self.enemies)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.player, self.bullets)
            if enemy.y > HEIGHT + 50 or enemy.x < -50 or enemy.x > WIDTH + 50:
                self.enemies.remove(enemy)
                
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if (bullet.y < -20 or bullet.y > HEIGHT + 20 or 
                bullet.x < -20 or bullet.x > WIDTH + 20):
                self.bullets.remove(bullet)
                
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
                
        # Handle collisions
        self._handle_collisions()
        
        # Check game over
        if self.player.hp <= 0 or self.game_time >= GAME_DURATION:
            self.running = False
            
    def _handle_collisions(self):
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            if bullet.friendly:
                for enemy in self.enemies[:]:
                    if self._check_collision(bullet, enemy):
                        enemy.hp -= bullet.damage
                        if enemy.hp <= 0:
                            self._create_explosion(enemy.x, enemy.y, enemy.radius)
                            self.enemies.remove(enemy)
                            self.score += 100 * int(self.wave_gen.difficulty)
                        self.bullets.remove(bullet)
                        break
                        
        # Enemy bullets vs player
        if self.player.invulnerable <= 0:
            for bullet in self.bullets[:]:
                if not bullet.friendly:
                    if self._check_collision(bullet, self.player):
                        self.player.hp -= bullet.damage
                        self.player.invulnerable = 1.5
                        self._create_explosion(self.player.x, self.player.y, 20)
                        self.bullets.remove(bullet)
                        
        # Enemies vs player
        if self.player.invulnerable <= 0:
            for enemy in self.enemies[:]:
                if self._check_collision(enemy, self.player):
                    self.player.hp -= 1
                    self.player.invulnerable = 2.0
                    self._create_explosion(enemy.x, enemy.y, enemy.radius)
                    self.enemies.remove(enemy)
                    
    def _check_collision(self, a, b):
        dx = a.x - b.x
        dy = a.y - b.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < a.radius + b.radius
        
    def _create_explosion(self, x, y, size):
        num_particles = int(size * 2)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            color = random.choice([RED, YELLOW, (255, 128, 0)])
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color,
                random.uniform(0.3, 0.8)
            ))
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars background
        for i in range(50):
            x = (i * 73) % WIDTH
            y = (self.game_time * 20 + i * 137) % HEIGHT
            pygame.draw.circle(self.screen, (100, 100, 100), (int(x), int(y)), 1)
        
        # Draw entities
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, enemy.color, (int(enemy.x), int(enemy.y)), enemy.radius)
            if enemy.hp > 1:
                pygame.draw.circle(self.screen, WHITE, (int(enemy.x), int(enemy.y)), enemy.radius, 2)
                
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, bullet.color, (int(bullet.x), int(bullet.y)), bullet.radius)
            
        # Draw player
        if self.player.invulnerable <= 0 or int(self.player.invulnerable * 10) % 2:
            pygame.draw.circle(self.screen, self.player.color, (int(self.player.x), int(self.player.y)), self.player.radius)
            pygame.draw.circle(self.screen, WHITE, (int(self.player.x), int(self.player.y)), self.player.radius, 2)
            
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
            
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH - bar_width - 10
        bar_y = 10
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, bar_width * self.player.hp / 5, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Time remaining
        time_left = max(0, GAME_DURATION - self.game_time)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        time_text = self.small_font.render(f"Time: {minutes}:{seconds:02d}", True, WHITE)
        self.screen.blit(time_text, (WIDTH - 100, 40))
        
        # Wave info
        wave_text = self.small_font.render(f"Wave: {self.wave_gen.wave_number}", True, WHITE)
        self.screen.blit(wave_text, (10, 50))
        
        pygame.display.flip()
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            
        # Game over screen
        self.screen.fill(BLACK)
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.small_font.render("Press ESC to exit", True, WHITE)
        
        self.screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2 - 50))
        self.screen.blit(final_score_text, (WIDTH//2 - 120, HEIGHT//2))
        self.screen.blit(restart_text, (WIDTH//2 - 80, HEIGHT//2 + 50))
        
        pygame.display.flip()
        
        # Wait for exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
                    
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run() 