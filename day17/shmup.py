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
        self.max_hp = 5
        
        # Powerup states
        self.rapid_fire = 0
        self.triple_shot = 0
        self.shield = 0
        self.damage_boost = 0
        self.speed_boost = 0
        
    def update(self, dt):
        keys = pygame.key.get_pressed()
        speed = 300 * dt * (1.5 if self.speed_boost > 0 else 1.0)
        if keys[pygame.K_LEFT]: self.x = max(self.radius, self.x - speed)
        if keys[pygame.K_RIGHT]: self.x = min(WIDTH - self.radius, self.x + speed)
        if keys[pygame.K_UP]: self.y = max(self.radius, self.y - speed)
        if keys[pygame.K_DOWN]: self.y = min(HEIGHT - self.radius, self.y + speed)
        
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        
        # Update powerup timers
        self.rapid_fire = max(0, self.rapid_fire - dt)
        self.triple_shot = max(0, self.triple_shot - dt)
        self.shield = max(0, self.shield - dt)
        self.damage_boost = max(0, self.damage_boost - dt)
        self.speed_boost = max(0, self.speed_boost - dt)
        
    def shoot(self, bullets):
        cooldown = 0.05 if self.rapid_fire > 0 else 0.1
        if self.shoot_cooldown <= 0:
            damage = 2 if self.damage_boost > 0 else 1
            bullet_color = (100, 255, 100) if self.damage_boost > 0 else GREEN
            
            if self.triple_shot > 0:
                # Triple shot pattern
                for angle_offset in [-0.2, 0, 0.2]:
                    dx = math.sin(angle_offset) * 300
                    dy = -500
                    bullets.append(Bullet(self.x, self.y - self.radius, dx, dy, 
                                        self.radius//2, bullet_color, damage, True))
            else:
                # Single shot
                bullets.append(Bullet(self.x, self.y - self.radius, 0, -500, 
                                    self.radius//2, bullet_color, damage, True))
            self.shoot_cooldown = cooldown

class Enemy(Entity):
    def __init__(self, x, y, enemy_type="basic"):
        self.type = enemy_type
        self.time = 0
        self.shoot_timer = random.uniform(0.5, 2.0)
        self.pattern_phase = random.uniform(0, math.pi * 2)
        
        # Shape properties
        self.shape = None
        self.stretch_x = 1.0
        self.stretch_y = 1.0
        self.rotation = 0
        self.rotation_speed = 0
        
        # Powerup drop properties
        self.drop_chance = 0
        self.possible_drops = []
        
        # Randomize attributes based on type
        if enemy_type == "basic":
            super().__init__(x, y, 0, random.uniform(50, 150), 
                           radius=random.randint(8, 15),
                           color=self._random_color(),
                           hp=1)
            self.shape = random.choice(["triangle", "square", "diamond"])
            self.stretch_x = random.uniform(0.8, 1.2)
            self.stretch_y = random.uniform(0.8, 1.2)
            self.drop_chance = 0.15
            self.possible_drops = ["health", "rapid_fire", "damage"]
            
        elif enemy_type == "heavy":
            super().__init__(x, y, 0, random.uniform(30, 80),
                           radius=random.randint(20, 30),
                           color=self._random_color(),
                           hp=random.randint(3, 5))
            self.shape = random.choice(["hexagon", "octagon", "square"])
            self.stretch_x = random.uniform(1.0, 1.4)
            self.stretch_y = random.uniform(0.7, 1.0)
            self.rotation_speed = random.uniform(-1, 1)
            self.drop_chance = 0.25
            self.possible_drops = ["shield", "health", "damage", "triple_shot"]
            
        elif enemy_type == "sine":
            super().__init__(x, y, random.uniform(50, 150), random.uniform(40, 100),
                           radius=random.randint(10, 18),
                           color=self._random_color(),
                           hp=2)
            self.base_x = x
            self.amplitude = random.uniform(50, 150)
            self.frequency = random.uniform(1, 3)
            self.shape = random.choice(["diamond", "star", "triangle"])
            self.stretch_x = random.uniform(0.7, 1.0)
            self.stretch_y = random.uniform(1.0, 1.3)
            self.rotation_speed = random.uniform(2, 4)
            self.drop_chance = 0.20
            self.possible_drops = ["speed", "rapid_fire", "triple_shot"]
            
        elif enemy_type == "spiral":
            super().__init__(x, y, 0, 0,
                           radius=random.randint(12, 20),
                           color=self._random_color(),
                           hp=random.randint(2, 4))
            self.angle = random.uniform(0, math.pi * 2)
            self.spiral_speed = random.uniform(100, 200)
            self.angle_speed = random.uniform(2, 4)
            self.shape = random.choice(["star", "cross", "hexagon"])
            self.stretch_x = random.uniform(0.9, 1.1)
            self.stretch_y = random.uniform(0.9, 1.1)
            self.rotation = random.uniform(0, math.pi * 2)
            self.rotation_speed = random.uniform(-3, -1) if random.random() > 0.5 else random.uniform(1, 3)
            self.drop_chance = 0.30
            self.possible_drops = ["shield", "speed", "damage", "health"]
            
    def _random_color(self):
        # Use a wider range of vibrant colors
        color_schemes = [
            # Pure hues with variations
            lambda: colorsys.hsv_to_rgb(random.uniform(0, 1), random.uniform(0.7, 1.0), random.uniform(0.8, 1.0)),
            # Pastel colors
            lambda: colorsys.hsv_to_rgb(random.uniform(0, 1), random.uniform(0.3, 0.5), random.uniform(0.9, 1.0)),
            # Neon colors
            lambda: colorsys.hsv_to_rgb(random.uniform(0, 1), 1.0, 1.0),
            # Deep colors
            lambda: colorsys.hsv_to_rgb(random.uniform(0, 1), random.uniform(0.8, 1.0), random.uniform(0.5, 0.7)),
        ]
        
        scheme = random.choice(color_schemes)
        rgb = scheme()
        return tuple(int(c * 255) for c in rgb)
        
    def update(self, dt, player, bullets):
        self.time += dt
        self.shoot_timer -= dt
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
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
    
    def draw(self, screen):
        # Save the current position
        cx, cy = int(self.x), int(self.y)
        
        # Calculate stretched radius
        rx = self.radius * self.stretch_x
        ry = self.radius * self.stretch_y
        
        # Create points based on shape
        points = []
        
        if self.shape == "triangle":
            # Equilateral triangle
            for i in range(3):
                angle = self.rotation + (i * 2 * math.pi / 3) - math.pi / 2
                px = cx + rx * math.cos(angle)
                py = cy + ry * math.sin(angle)
                points.append((px, py))
                
        elif self.shape == "square":
            # Square
            for i in range(4):
                angle = self.rotation + (i * math.pi / 2) + math.pi / 4
                px = cx + rx * math.cos(angle)
                py = cy + ry * math.sin(angle)
                points.append((px, py))
                
        elif self.shape == "diamond":
            # Diamond (rotated square)
            for i in range(4):
                angle = self.rotation + (i * math.pi / 2)
                px = cx + rx * math.cos(angle) * (1.2 if i % 2 == 0 else 0.8)
                py = cy + ry * math.sin(angle) * (0.8 if i % 2 == 0 else 1.2)
                points.append((px, py))
                
        elif self.shape == "hexagon":
            # Hexagon
            for i in range(6):
                angle = self.rotation + (i * math.pi / 3)
                px = cx + rx * math.cos(angle)
                py = cy + ry * math.sin(angle)
                points.append((px, py))
                
        elif self.shape == "octagon":
            # Octagon
            for i in range(8):
                angle = self.rotation + (i * math.pi / 4)
                px = cx + rx * math.cos(angle)
                py = cy + ry * math.sin(angle)
                points.append((px, py))
                
        elif self.shape == "star":
            # 5-pointed star
            for i in range(10):
                angle = self.rotation + (i * math.pi / 5) - math.pi / 2
                if i % 2 == 0:
                    r = rx
                else:
                    r = rx * 0.5
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle) * (ry / rx)
                points.append((px, py))
                
        elif self.shape == "cross":
            # Plus/cross shape
            w = rx * 0.3
            h = ry
            # Calculate rotated cross points
            cross_points = [
                (-w, -h), (w, -h), (w, -w), (h, -w),
                (h, w), (w, w), (w, h), (-w, h),
                (-w, w), (-h, w), (-h, -w), (-w, -w)
            ]
            for px, py in cross_points:
                # Rotate points
                rpx = px * math.cos(self.rotation) - py * math.sin(self.rotation)
                rpy = px * math.sin(self.rotation) + py * math.cos(self.rotation)
                points.append((cx + rpx, cy + rpy))
        
        # Draw the shape
        if points:
            pygame.draw.polygon(screen, self.color, points)
            if self.hp > 1:
                pygame.draw.polygon(screen, WHITE, points, 2)

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

class Powerup:
    def __init__(self, x, y, powerup_type):
        self.x, self.y = x, y
        self.type = powerup_type
        self.radius = 15
        self.dy = 100  # Fall speed
        self.time = 0
        self.collected = False
        
        # Set colors and properties based on type
        self.colors = {
            "health": (255, 100, 200),      # Pink
            "rapid_fire": (255, 255, 100),  # Yellow
            "triple_shot": (100, 255, 255), # Cyan
            "shield": (150, 150, 255),      # Light blue
            "damage": (255, 150, 100),      # Orange
            "speed": (200, 100, 255)        # Purple
        }
        self.color = self.colors.get(powerup_type, WHITE)
        
    def update(self, dt):
        self.y += self.dy * dt
        self.time += dt
        
    def draw(self, screen):
        # Pulsing effect
        pulse = math.sin(self.time * 5) * 0.2 + 1.0
        radius = int(self.radius * pulse)
        
        # Draw outer glow
        for i in range(3):
            glow_radius = radius + (3-i) * 5
            glow_alpha = 50 - i * 15
            glow_color = tuple(min(255, c + glow_alpha) for c in self.color)
            pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), glow_radius, 2)
        
        # Draw based on type with unique shapes
        if self.type == "health":
            # Draw plus sign
            pygame.draw.rect(screen, self.color, 
                           (self.x - 3, self.y - radius, 6, radius * 2))
            pygame.draw.rect(screen, self.color, 
                           (self.x - radius, self.y - 3, radius * 2, 6))
        elif self.type == "rapid_fire":
            # Draw lightning bolt
            points = [
                (self.x - 5, self.y - radius),
                (self.x + 3, self.y - 3),
                (self.x - 3, self.y + 3),
                (self.x + 5, self.y + radius)
            ]
            pygame.draw.lines(screen, self.color, False, points, 3)
        elif self.type == "triple_shot":
            # Draw three small circles
            for dx in [-8, 0, 8]:
                pygame.draw.circle(screen, self.color, 
                                 (int(self.x + dx), int(self.y)), 5)
        elif self.type == "shield":
            # Draw hexagon
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                px = self.x + radius * math.cos(angle)
                py = self.y + radius * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points, 2)
        elif self.type == "damage":
            # Draw star
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                if i % 2 == 0:
                    r = radius
                else:
                    r = radius * 0.5
                px = self.x + r * math.cos(angle - math.pi/2)
                py = self.y + r * math.sin(angle - math.pi/2)
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)
        elif self.type == "speed":
            # Draw arrow
            points = [
                (self.x, self.y - radius),
                (self.x - 7, self.y + 5),
                (self.x, self.y),
                (self.x + 7, self.y + 5)
            ]
            pygame.draw.polygon(screen, self.color, points)
        
        # Draw inner circle for all types
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)

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
        self.powerups = []
        self.wave_gen = WaveGenerator()
        self.powerup_timer = random.uniform(5, 10)
        
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
                
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if powerup.y > HEIGHT + 50:
                self.powerups.remove(powerup)
                
        # Spawn powerups
        self.powerup_timer -= dt
        if self.powerup_timer <= 0:
            self._spawn_powerup()
            self.powerup_timer = random.uniform(8, 15)
            
        # Handle collisions
        self._handle_collisions()
        
        # Check game over
        if self.player.hp <= 0 or self.game_time >= GAME_DURATION:
            self.running = False
            
    def _spawn_powerup(self):
        powerup_types = ["health", "rapid_fire", "triple_shot", "shield", "damage", "speed"]
        weights = [20, 20, 15, 15, 15, 15]  # Health is slightly more common
        powerup_type = random.choices(powerup_types, weights=weights)[0]
        x = random.uniform(50, WIDTH - 50)
        self.powerups.append(Powerup(x, -30, powerup_type))
        
    def _handle_collisions(self):
        # Player vs powerups
        for powerup in self.powerups[:]:
            dx = powerup.x - self.player.x
            dy = powerup.y - self.player.y
            if math.sqrt(dx*dx + dy*dy) < powerup.radius + self.player.radius:
                self._apply_powerup(powerup.type)
                self.powerups.remove(powerup)
                self.score += 50
                
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
                            # Check for powerup drop
                            if random.random() < enemy.drop_chance and enemy.possible_drops:
                                drop_type = random.choice(enemy.possible_drops)
                                self.powerups.append(Powerup(enemy.x, enemy.y, drop_type))
                        self.bullets.remove(bullet)
                        break
                        
        # Enemy bullets vs player
        if self.player.invulnerable <= 0:
            for bullet in self.bullets[:]:
                if not bullet.friendly:
                    if self._check_collision(bullet, self.player):
                        if self.player.shield > 0:
                            self.player.shield = 0  # Shield breaks
                            self._create_explosion(self.player.x, self.player.y, 30)
                        else:
                            self.player.hp -= bullet.damage
                            self.player.invulnerable = 1.5
                            self._create_explosion(self.player.x, self.player.y, 20)
                        self.bullets.remove(bullet)
                        
        # Enemies vs player
        if self.player.invulnerable <= 0:
            for enemy in self.enemies[:]:
                if self._check_collision(enemy, self.player):
                    if self.player.shield > 0:
                        self.player.shield = 0  # Shield breaks
                        self._create_explosion(enemy.x, enemy.y, enemy.radius * 1.5)
                    else:
                        self.player.hp -= 1
                        self.player.invulnerable = 2.0
                        self._create_explosion(enemy.x, enemy.y, enemy.radius)
                    self.enemies.remove(enemy)
                    
    def _check_collision(self, a, b):
        dx = a.x - b.x
        dy = a.y - b.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < a.radius + b.radius
        
    def _apply_powerup(self, powerup_type):
        if powerup_type == "health":
            self.player.hp = min(self.player.hp + 1, self.player.max_hp)
            self._create_explosion(self.player.x, self.player.y, 25)
        elif powerup_type == "rapid_fire":
            self.player.rapid_fire = 5.0  # 5 seconds
        elif powerup_type == "triple_shot":
            self.player.triple_shot = 7.0  # 7 seconds
        elif powerup_type == "shield":
            self.player.shield = 10.0  # 10 seconds
        elif powerup_type == "damage":
            self.player.damage_boost = 8.0  # 8 seconds
        elif powerup_type == "speed":
            self.player.speed_boost = 6.0  # 6 seconds
        
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
            enemy.draw(self.screen)
                
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, bullet.color, (int(bullet.x), int(bullet.y)), bullet.radius)
            
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        # Draw player
        if self.player.invulnerable <= 0 or int(self.player.invulnerable * 10) % 2:
            pygame.draw.circle(self.screen, self.player.color, (int(self.player.x), int(self.player.y)), self.player.radius)
            pygame.draw.circle(self.screen, WHITE, (int(self.player.x), int(self.player.y)), self.player.radius, 2)
            
            # Draw shield effect
            if self.player.shield > 0:
                shield_alpha = min(255, int(255 * (self.player.shield / 10)))
                for i in range(3):
                    pygame.draw.circle(self.screen, (150, 150, 255), 
                                     (int(self.player.x), int(self.player.y)), 
                                     self.player.radius + 5 + i * 3, 1)
            
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
        
        # Active powerups display
        powerup_y = 80
        if self.player.rapid_fire > 0:
            rf_text = self.small_font.render(f"Rapid Fire: {int(self.player.rapid_fire)}s", True, YELLOW)
            self.screen.blit(rf_text, (10, powerup_y))
            powerup_y += 25
        if self.player.triple_shot > 0:
            ts_text = self.small_font.render(f"Triple Shot: {int(self.player.triple_shot)}s", True, CYAN)
            self.screen.blit(ts_text, (10, powerup_y))
            powerup_y += 25
        if self.player.shield > 0:
            sh_text = self.small_font.render(f"Shield: {int(self.player.shield)}s", True, (150, 150, 255))
            self.screen.blit(sh_text, (10, powerup_y))
            powerup_y += 25
        if self.player.damage_boost > 0:
            db_text = self.small_font.render(f"Damage Boost: {int(self.player.damage_boost)}s", True, (255, 150, 100))
            self.screen.blit(db_text, (10, powerup_y))
            powerup_y += 25
        if self.player.speed_boost > 0:
            sb_text = self.small_font.render(f"Speed Boost: {int(self.player.speed_boost)}s", True, (200, 100, 255))
            self.screen.blit(sb_text, (10, powerup_y))
        
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