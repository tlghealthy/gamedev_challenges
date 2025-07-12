import pygame, sys, time
from physics import Physics

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock  = pygame.time.Clock()

phys = Physics(debug=True)

player_body, player_shape, foot = phys.add_player((200, 300))
phys.add_platform((0, 680), (1280, 680))                     # floor
moving = phys.add_platform((200, 500), (500, 500),
                           kinematic=True, vel_px_s=(60, 0)) # conveyor

# example attackbox ↔ hurtbox callback
def begin_attack(arbiter, space, data):
    print("hit!")
    arbiter.shapes[1].body.apply_impulse_at_local_point((200, -400))
    return False  # prevent physical push-back

phys.on("ATTACKBOX", "HURTBOX", begin=begin_attack)

while True:
    dt = clock.tick(120) / 1000.0
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); sys.exit()

    # cheap input → impulse movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_body.apply_force_at_local_point((-900, 0))
    if keys[pygame.K_RIGHT]:
        player_body.apply_force_at_local_point((+900, 0))
    if keys[pygame.K_SPACE]:
        player_body.apply_impulse_at_local_point((0, -450))

    phys.step(dt)

    screen.fill((30, 32, 40))
    phys.debug_draw(screen)
    pygame.display.flip()
