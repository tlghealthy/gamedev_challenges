import sys, json, os, time, pygame
import pymunk
import pymunk.pygame_util as pm_draw

pygame.init()
W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
clock  = pygame.time.Clock()

# --- Physics -------------------------------------------------
space = pymunk.Space()
space.gravity = 0, 900         # +y is down in pygame coords

def make_box(pos, size=(50, 50), mass=1):
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
    body.position = pos
    shape = pymunk.Poly.create_box(body, size)
    shape.friction = 0.6
    space.add(body, shape)

# static floor
segment = pymunk.Segment(space.static_body, (0, H-40), (W, H-40), 5)
segment.friction = 1.0
space.add(segment)

make_box((W/2, 100))

draw_opts = pm_draw.DrawOptions(screen)
phys_dt   = 1/60     # fixed step

# --- Main loop ----------------------------------------------
accum = 0
while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if ev.type == pygame.MOUSEBUTTONDOWN:
            make_box(ev.pos)          # quick spawn test

    # physics: fixed-timestep for determinism
    accum += clock.get_time() / 1000
    while accum >= phys_dt:
        space.step(phys_dt)
        accum -= phys_dt

    screen.fill((30, 30, 30))
    space.debug_draw(draw_opts)       # ≈ zero effort rendering
    pygame.display.flip()
    clock.tick(120)                   # render uncapped; physics fixed
