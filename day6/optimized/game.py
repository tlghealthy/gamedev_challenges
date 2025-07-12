import os
import json
import pygame
import math
import sys
from pygame.locals import *

class Settings:
    """Loads and stores all tunable game constants from settings.json."""
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.defaults = {
            "WIDTH": 1280,
            "HEIGHT": 720,
            "BG_COLOR": [0, 0, 0],
            "STAGE_COLOR": [200, 200, 200],
            "P1_COLOR": [255, 0, 0],
            "P2_COLOR": [0, 128, 255],
            "ATTACK_COLOR": [255, 255, 0],
            "GRAVITY": 1.0,
            "MOVE_SPEED": 6.0,
            "JUMP_VELOCITY": -18.0,
            "ATTACK_COOLDOWN": 0.4,
            "DAMAGE_PER_HIT": 10,
            "BASE_KB": 5,
            "KB_SCALAR": 0.25
        }
        self._ensure_file()
        self._load()

    def _ensure_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump(self.defaults, f, indent=2)

    def _load(self):
        with open(self.filename, "r") as f:
            data = json.load(f)
        for k, v in self.defaults.items():
            setattr(self, k, data.get(k, v))

class Stage:
    """Represents the main fighting platform."""
    def __init__(self, settings):
        self.width = 800
        self.height = 40
        self.x = (settings.WIDTH - self.width) // 2
        self.y = 500
        self.color = tuple(settings.STAGE_COLOR)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

class Player:
    """Encapsulates player state, movement, drawing, attack, and knockback logic."""
    WIDTH = 50
    HEIGHT = 90

    def __init__(self, settings, x, y, color, controls, face_left):
        self.settings = settings
        self.color = color
        self.controls = controls
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing = -1 if face_left else 1
        self.attack_cooldown = 0
        self.damage = 0
        self.knockback = pygame.Vector2(0, 0)
        self.is_attacking = False
        self.face_color_idle = (0, 255, 0)
        self.face_color_cooldown = (255, 255, 0)

    def handle_input(self, keys, dt):
        move = 0
        if keys[self.controls['left']]:
            move -= 1
        if keys[self.controls['right']]:
            move += 1
        if move != 0:
            self.facing = move
        self.vel.x = move * self.settings.MOVE_SPEED

        if keys[self.controls['jump']] and self.on_ground:
            self.vel.y = self.settings.JUMP_VELOCITY
            self.on_ground = False

    def update(self, dt, stage_rect):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown < 0:
                self.attack_cooldown = 0

        # Apply knockback if any
        if self.knockback.length_squared() > 0.01:
            self.vel += self.knockback
            self.knockback *= 0.7  # Dampen knockback
            if self.knockback.length() < 0.5:
                self.knockback = pygame.Vector2(0, 0)

        # Gravity
        self.vel.y += self.settings.GRAVITY

        # Move and collide with stage
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        # Stage collision (only from above)
        if self.rect.colliderect(stage_rect):
            if self.vel.y >= 0 and self.rect.bottom - self.vel.y <= stage_rect.top:
                self.rect.bottom = stage_rect.top
                self.vel.y = 0
                self.on_ground = True
            else:
                # Prevent sticking to sides/bottom
                if self.rect.right > stage_rect.right:
                    self.rect.right = stage_rect.right
                if self.rect.left < stage_rect.left:
                    self.rect.left = stage_rect.left
        else:
            self.on_ground = False

    def can_attack(self):
        return self.attack_cooldown == 0

    def attack(self):
        self.attack_cooldown = self.settings.ATTACK_COOLDOWN
        self.is_attacking = True

    def get_attack_hitbox(self):
        # 40 px in front, same height as player, 30 px tall, 30 px wide
        offset = self.facing * (self.WIDTH // 2 + 20)
        hitbox_x = self.rect.centerx + offset - 20
        hitbox_y = self.rect.centery - 20
        return pygame.Rect(hitbox_x, hitbox_y, 40, 40)

    def apply_hit(self):
        self.damage += self.settings.DAMAGE_PER_HIT

    def apply_knockback(self):
        kb = self.settings.BASE_KB + self.damage * self.settings.KB_SCALAR
        angle = math.radians(20)  # 20% vertical
        dx = kb * self.facing
        dy = -abs(kb * 0.2)
        self.knockback = pygame.Vector2(dx, dy)

    def draw(self, surf):
        pygame.draw.ellipse(surf, self.color, self.rect)
        # Draw face triangle
        face_color = self.face_color_idle if self.can_attack() else self.face_color_cooldown
        cx = self.rect.centerx + self.facing * (self.WIDTH // 2)
        cy = self.rect.centery - 20
        points = [
            (cx + self.facing * 10, cy),
            (cx, cy - 10),
            (cx, cy + 10)
        ]
        pygame.draw.polygon(surf, face_color, points)

    def reset(self, x, y, face_left):
        self.rect.x = x
        self.rect.y = y
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing = -1 if face_left else 1
        self.attack_cooldown = 0
        self.damage = 0
        self.knockback = pygame.Vector2(0, 0)
        self.is_attacking = False

class Game:
    """Owns the main loop and game state."""
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.WIDTH, self.settings.HEIGHT))
        pygame.display.set_caption("2-Player Fighting Platformer Demo")
        self.clock = pygame.time.Clock()
        self.stage = Stage(self.settings)
        self.running = True
        self.winner = None
        self.font = pygame.font.SysFont(None, 60)
        self.small_font = pygame.font.SysFont(None, 32)
        self._init_players()

    def _init_players(self):
        stage = self.stage
        y = stage.y - Player.HEIGHT
        p1_x = stage.x + stage.width // 2 - 150 - Player.WIDTH // 2
        p2_x = stage.x + stage.width // 2 + 150 - Player.WIDTH // 2
        self.p1 = Player(
            self.settings, p1_x, y,
            tuple(self.settings.P1_COLOR),
            {
                'left': pygame.K_a,
                'right': pygame.K_d,
                'jump': pygame.K_w,
                'attack': pygame.K_LCTRL
            },
            face_left=False
        )
        self.p2 = Player(
            self.settings, p2_x, y,
            tuple(self.settings.P2_COLOR),
            {
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'jump': pygame.K_UP,
                'attack': pygame.K_RCTRL
            },
            face_left=True
        )

    def reset(self):
        self._init_players()
        self.winner = None

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            if not self.winner:
                self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if self.winner and event.key == pygame.K_r:
                    self.reset()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.p1.handle_input(keys, dt)
        self.p2.handle_input(keys, dt)

        self.p1.update(dt, self.stage.rect)
        self.p2.update(dt, self.stage.rect)

        # Attacks
        for player, opponent in [(self.p1, self.p2), (self.p2, self.p1)]:
            if keys[player.controls['attack']] and player.can_attack():
                player.attack()
                hitbox = player.get_attack_hitbox()
                if hitbox.colliderect(opponent.rect):
                    opponent.apply_hit()
                    opponent.apply_knockback()
            else:
                player.is_attacking = False

        # Win condition
        if self.p1.rect.top > self.settings.HEIGHT:
            self.winner = 2
        elif self.p2.rect.top > self.settings.HEIGHT:
            self.winner = 1

    def draw(self):
        self.screen.fill(tuple(self.settings.BG_COLOR))
        self.stage.draw(self.screen)
        self.p1.draw(self.screen)
        self.p2.draw(self.screen)

        # Draw attack hitboxes (for one frame)
        for player in [self.p1, self.p2]:
            if player.is_attacking:
                pygame.draw.rect(
                    self.screen,
                    tuple(self.settings.ATTACK_COLOR),
                    player.get_attack_hitbox()
                )

        # Draw damage
        dmg1 = self.small_font.render(f"P1: {self.p1.damage}", True, (255, 255, 255))
        dmg2 = self.small_font.render(f"P2: {self.p2.damage}", True, (255, 255, 255))
        self.screen.blit(dmg1, (30, 30))
        self.screen.blit(dmg2, (self.settings.WIDTH - 120, 30))

        if self.winner:
            text = self.font.render(
                f"PLAYER {self.winner} WINS – press R to restart", True, (255, 255, 255)
            )
            rect = text.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT // 2))
            self.screen.blit(text, rect)

        pygame.display.flip()

if __name__ == "__main__":
    Game().run()