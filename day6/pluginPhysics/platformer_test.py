import pygame
import sys
import json
from simple_physics import SimplePhysicsEngine  # Assumes your physics core is in physics.py

# --- Load settings ---
with open('game_settings.json', 'r') as f:
    settings = json.load(f)

WIN_W = settings["WIN_W"]
WIN_H = settings["WIN_H"]
PLAYER_SIZE = tuple(settings["PLAYER_SIZE"])
GROUND_SIZE = tuple(settings["GROUND_SIZE"])
FPS = settings["FPS"]
GRAVITY = settings["GRAVITY"]
MOVE_FORCE = settings["MOVE_FORCE"]
JUMP_FORCE = settings["JUMP_FORCE"]
PLAYER_DAMPENING = settings["PLAYER_DAMPENING"]
GROUND_DAMPENING = settings["GROUND_DAMPENING"]

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
clock = pygame.time.Clock()

# --- Physics setup ---
eng = SimplePhysicsEngine()
player = eng.create_body(80, 0, *PLAYER_SIZE, dampening=PLAYER_DAMPENING)
ground = eng.create_body(60, 300, *GROUND_SIZE, static=True, dampening=GROUND_DAMPENING)  # x, y, w, h

# --- Helper for checking if player is on ground ---
def on_ground(player_body, ground_body):
    p = player_body
    g = ground_body
    return (abs(p.y + p.h - g.y) < 1.0 and
            p.x + p.w > g.x and p.x < g.x + g.w)

# --- Main loop ---
running = True
prev_jump_pressed = False  # Track previous jump key state
while running:
    dt = clock.tick(FPS) / 1000  # seconds per frame

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Input ---
    keys = pygame.key.get_pressed()
    P = eng.get_body(player)
    G = eng.get_body(ground)
    if on_ground(P, G):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            eng.apply_force(player, -MOVE_FORCE, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            eng.apply_force(player, MOVE_FORCE, 0)

    eng.apply_force(player, 0, GRAVITY)

    # Jump (W or Space) - only on key down, and only if vy is near zero
    jump_pressed = keys[pygame.K_w] or keys[pygame.K_SPACE]
    if jump_pressed and not prev_jump_pressed and on_ground(P, G) and abs(P.vy) < 100.0:
        eng.apply_force(player, 0, JUMP_FORCE)
    prev_jump_pressed = jump_pressed

    # --- Physics step ---
    eng.update(dt)

    # --- Draw ---
    screen.fill((30, 30, 50))
    # Draw ground
    G = eng.get_body(ground)
    pygame.draw.rect(screen, (120, 90, 50),
                     pygame.Rect(G.x, G.y, G.w, G.h))
    # Draw player
    P = eng.get_body(player)
    pygame.draw.rect(screen, (100, 220, 120),
                     pygame.Rect(P.x, P.y, P.w, P.h))

    pygame.display.flip()

pygame.quit()
sys.exit()
