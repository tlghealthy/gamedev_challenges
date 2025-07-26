# server.py
from netbox import GameSyncNet
import pygame

WIDTH, HEIGHT = 400, 400
BOX_COLORS = [(255,0,0), (0,0,255), (0,200,0), (200,0,200), (255,128,0), (0,255,255)]
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

net = GameSyncNet('server', host='0.0.0.0', port=9999)

run = True
while run:
    screen.fill((30,30,30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    positions = net.get_positions()
    for idx, (pid, pos) in enumerate(sorted(positions.items())):
        color = BOX_COLORS[(pid-1)%len(BOX_COLORS)]
        pygame.draw.rect(screen, color, (pos['x'], pos['y'], 40, 40))
        screen.blit(font.render(f"Player {pid}", 1, (255,255,255)), (pos['x'], pos['y']-22))

    pygame.display.flip()
    clock.tick(30)
pygame.quit()
