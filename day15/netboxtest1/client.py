# client.py
from netbox import GameSyncNet
import pygame

WIDTH, HEIGHT = 400, 400
START_POS = [(60, 180), (300, 180), (200, 60), (200, 300), (120,120), (280,280)]
BOX_COLORS = [(255,0,0), (0,0,255), (0,200,0), (200,0,200), (255,128,0), (0,255,255)]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

net = GameSyncNet('client', host='127.0.0.1', port=9999)
my_x, my_y = 0, 0
speed = 4
assigned = False

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Wait for player ID assignment
    if not assigned and net.get_player_id() is not None:
        player_id = net.get_player_id()
        my_x, my_y = START_POS[(player_id-1)%len(START_POS)]
        assigned = True

    screen.fill((20,20,20))
    if not assigned:
        msg = font.render("Connecting to server...", True, (255,255,255))
        screen.blit(msg, (60, HEIGHT//2-20))
        pygame.display.flip()
        clock.tick(30)
        continue

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        my_x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        my_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        my_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        my_y += speed
    my_x = max(0, min(WIDTH-40, my_x))
    my_y = max(0, min(HEIGHT-40, my_y))

    net.send_position(my_x, my_y)
    positions = net.get_positions()

    # Draw all boxes
    for idx, (pid, pos) in enumerate(sorted(positions.items())):
        color = BOX_COLORS[(int(pid)-1)%len(BOX_COLORS)]
        pygame.draw.rect(screen, color, (pos['x'], pos['y'], 40, 40))
        screen.blit(font.render(f"Player {pid}", 1, (255,255,255)), (pos['x'], pos['y']-22))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
