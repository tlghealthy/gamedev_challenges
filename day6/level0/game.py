import pygame
import sys
import math
from pygame.locals import *

# --- Constants ---
WIDTH, HEIGHT = 1280, 720
PLATFORM_W, PLATFORM_H = 800, 40
PLATFORM_Y = 500
PLATFORM_X = (WIDTH - PLATFORM_W) // 2
BG_COLOR = (0, 0, 0)
PLATFORM_COLOR = (200, 200, 200)
FPS = 60
GRAVITY = 1.2
JUMP_VEL = -22
MOVE_SPEED = 9
CAPSULE_W, CAPSULE_H = 60, 120
PUNCH_W, PUNCH_H = 40, 30
PUNCH_COOLDOWN = 0.4
DAMAGE_PER_HIT = 10

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2-Player Fighting Platformer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 64)

# --- Helper Functions ---
def draw_capsule(surf, color, rect, facing):
    x, y, w, h = rect
    radius = w // 2
    pygame.draw.rect(surf, color, (x, y + radius, w, h - 2 * radius))
    pygame.draw.circle(surf, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surf, color, (x + radius, y + h - radius), radius)
    # Eyes for facing
    eye_y = y + radius + 10
    if facing == 1:
        pygame.draw.circle(surf, (255,255,255), (x + w - 18, eye_y), 7)
        pygame.draw.circle(surf, (0,0,0), (x + w - 18, eye_y), 3)
    else:
        pygame.draw.circle(surf, (255,255,255), (x + 18, eye_y), 7)
        pygame.draw.circle(surf, (0,0,0), (x + 18, eye_y), 3)

def rects_collide(a, b):
    return pygame.Rect(a).colliderect(pygame.Rect(b))

# --- Classes ---
class Player:
    def __init__(self, x, y, color, controls, punch_key):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.color = color
        self.facing = 1
        self.on_ground = False
        self.damage = 0
        self.punch_cooldown = 0
        self.punching = False
        self.controls = controls
        self.punch_key = punch_key
        self.rect = pygame.Rect(self.x, self.y, CAPSULE_W, CAPSULE_H)
        self.last_punch_time = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, CAPSULE_W, CAPSULE_H)

    def get_feet(self):
        return pygame.Rect(self.x + 10, self.y + CAPSULE_H - 10, CAPSULE_W - 20, 12)

    def get_punch_rect(self):
        if self.facing == 1:
            px = self.x + CAPSULE_W
        else:
            px = self.x - PUNCH_W
        py = self.y + CAPSULE_H // 2 - PUNCH_H // 2
        return pygame.Rect(px, py, PUNCH_W, PUNCH_H)

    def update(self, keys, dt):
        # Movement
        self.vx = 0
        if keys[self.controls['left']]:
            self.vx -= MOVE_SPEED
            self.facing = -1
        if keys[self.controls['right']]:
            self.vx += MOVE_SPEED
            self.facing = 1
        # Jump
        if keys[self.controls['jump']] and self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False
        # Punch
        if keys[self.punch_key] and self.punch_cooldown <= 0:
            self.punching = True
            self.punch_cooldown = PUNCH_COOLDOWN
        else:
            self.punching = False
        # Cooldown
        if self.punch_cooldown > 0:
            self.punch_cooldown -= dt
        # Gravity
        self.vy += GRAVITY
        # Apply velocity
        self.x += self.vx
        self.y += self.vy
        # Clamp to screen
        self.x = max(0, min(WIDTH - CAPSULE_W, self.x))
        # Update rect
        self.rect = pygame.Rect(self.x, self.y, CAPSULE_W, CAPSULE_H)

    def land_on(self, plat_rect):
        self.y = plat_rect.top - CAPSULE_H
        self.vy = 0
        self.on_ground = True

    def knockback(self, direction):
        mag = 5 + 0.25 * self.damage
        self.vx = mag * direction
        self.vy = -mag * 0.2

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.facing = 1
        self.on_ground = False
        self.damage = 0
        self.punch_cooldown = 0
        self.punching = False

# --- Game Setup ---
platform_rect = pygame.Rect(PLATFORM_X, PLATFORM_Y, PLATFORM_W, PLATFORM_H)
p1_controls = {'left': K_a, 'right': K_d, 'jump': K_w}
p2_controls = {'left': K_LEFT, 'right': K_RIGHT, 'jump': K_UP}
p1 = Player(PLATFORM_X + 100, PLATFORM_Y - CAPSULE_H, (220, 40, 40), p1_controls, K_LCTRL)
p2 = Player(PLATFORM_X + PLATFORM_W - 160, PLATFORM_Y - CAPSULE_H, (40, 80, 220), p2_controls, K_RCTRL)

def reset_game():
    p1.reset(PLATFORM_X + 100, PLATFORM_Y - CAPSULE_H)
    p2.reset(PLATFORM_X + PLATFORM_W - 160, PLATFORM_Y - CAPSULE_H)
    return False, 0

game_over, winner = reset_game()

# --- Main Loop ---
while True:
    dt = clock.tick(FPS) / 1000.0
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == KEYDOWN and event.key == K_r:
            game_over, winner = reset_game()

    if not game_over:
        # Update players
        p1.update(keys, dt)
        p2.update(keys, dt)

        # Platform collision
        for p in [p1, p2]:
            if p.vy >= 0:
                feet = p.get_feet()
                if feet.colliderect(platform_rect) and p.y + CAPSULE_H - 8 < platform_rect.top + 10:
                    p.land_on(platform_rect)
            if p.y + CAPSULE_H >= HEIGHT:
                game_over = True
                winner = 2 if p is p1 else 1

        # Punch logic
        for attacker, defender in [(p1, p2), (p2, p1)]:
            if attacker.punching and attacker.punch_cooldown > PUNCH_COOLDOWN - 0.05:
                punch_rect = attacker.get_punch_rect()
                if rects_collide(punch_rect, defender.get_rect()):
                    defender.damage += DAMAGE_PER_HIT
                    direction = attacker.facing
                    defender.knockback(direction)

    # --- Drawing ---
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, PLATFORM_COLOR, platform_rect)
    # Draw players
    draw_capsule(screen, p1.color, (p1.x, p1.y, CAPSULE_W, CAPSULE_H), p1.facing)
    draw_capsule(screen, p2.color, (p2.x, p2.y, CAPSULE_W, CAPSULE_H), p2.facing)
    # Draw punch
    for p in [p1, p2]:
        if p.punching and p.punch_cooldown > PUNCH_COOLDOWN - 0.05:
            pygame.draw.rect(screen, (255,255,180), p.get_punch_rect())
    # Draw damage
    dmg1 = font.render(f"{p1.damage}", True, (255,255,255))
    dmg2 = font.render(f"{p2.damage}", True, (255,255,255))
    screen.blit(dmg1, (p1.x + CAPSULE_W//2 - dmg1.get_width()//2, p1.y - 40))
    screen.blit(dmg2, (p2.x + CAPSULE_W//2 - dmg2.get_width()//2, p2.y - 40))
    # Game over
    if game_over:
        msg = font.render(f"PLAYER {winner} WINS – press R to restart", True, (255,255,0))
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
    pygame.display.flip()
