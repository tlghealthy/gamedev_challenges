import pygame
import random
import math

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_RADIUS = 25
ORB_RADIUS = 15
ENEMY_RADIUS = 20
PLAYER_COLOR = (50, 200, 255)
ORB_COLOR = (255, 220, 50)
ENEMY_COLOR = (255, 60, 80)
BG_COLOR = (30, 30, 40)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abstract Arcade: Orbital Dodge")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Mechanics: Player orbits a center, collects orbs, avoids enemies
CENTER = (WIDTH // 2, HEIGHT // 2)
ORBIT_RADIUS = 180
player_angle = 0
player_speed = 0.04
score = 0
lives = 3

def random_orb_pos():
    angle = random.uniform(0, 2 * math.pi)
    r = ORBIT_RADIUS + random.choice([-60, 60])
    x = CENTER[0] + r * math.cos(angle)
    y = CENTER[1] + r * math.sin(angle)
    return (x, y)

def random_enemy():
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(1.5, 2.5)
    return {'angle': angle, 'speed': speed, 'r': ORBIT_RADIUS + 120}

orb_pos = random_orb_pos()
enemies = [random_enemy() for _ in range(2)]

game_over = False

def draw():
    screen.fill(BG_COLOR)
    # Draw orbit path
    pygame.draw.circle(screen, (80, 80, 120), CENTER, ORBIT_RADIUS, 2)
    # Draw player
    px = CENTER[0] + ORBIT_RADIUS * math.cos(player_angle)
    py = CENTER[1] + ORBIT_RADIUS * math.sin(player_angle)
    pygame.draw.circle(screen, PLAYER_COLOR, (int(px), int(py)), PLAYER_RADIUS)
    # Draw orb
    pygame.draw.circle(screen, ORB_COLOR, (int(orb_pos[0]), int(orb_pos[1])), ORB_RADIUS)
    # Draw enemies
    for enemy in enemies:
        ex = CENTER[0] + enemy['r'] * math.cos(enemy['angle'])
        ey = CENTER[1] + enemy['r'] * math.sin(enemy['angle'])
        pygame.draw.circle(screen, ENEMY_COLOR, (int(ex), int(ey)), ENEMY_RADIUS)
    # Draw score/lives
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    lives_text = font.render(f"Lives: {lives}", True, (255,255,255))
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (20, 60))
    if game_over:
        over_text = font.render("GAME OVER! Press R to restart", True, (255, 100, 100))
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 30))
    pygame.display.flip()

def check_collision(a, b, r1, r2):
    return math.hypot(a[0]-b[0], a[1]-b[1]) < (r1 + r2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # Reset game
            player_angle = 0
            score = 0
            lives = 3
            orb_pos = random_orb_pos()
            enemies = [random_enemy() for _ in range(2)]
            game_over = False
    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT]:
            player_angle -= player_speed
        if keys[pygame.K_RIGHT]:
            player_angle += player_speed
        # Player position
        px = CENTER[0] + ORBIT_RADIUS * math.cos(player_angle)
        py = CENTER[1] + ORBIT_RADIUS * math.sin(player_angle)
        # Check orb collision
        if check_collision((px, py), orb_pos, PLAYER_RADIUS, ORB_RADIUS):
            score += 1
            orb_pos = random_orb_pos()
            # Add new enemy every 3 points
            if score % 3 == 0:
                enemies.append(random_enemy())
        # Move enemies
        for enemy in enemies:
            enemy['angle'] += enemy['speed'] * 0.01
            # Enemy position
            ex = CENTER[0] + enemy['r'] * math.cos(enemy['angle'])
            ey = CENTER[1] + enemy['r'] * math.sin(enemy['angle'])
            if check_collision((px, py), (ex, ey), PLAYER_RADIUS, ENEMY_RADIUS):
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    # Reset player and orb
                    player_angle = 0
                    orb_pos = random_orb_pos()
                    break
    draw()
    clock.tick(FPS)

pygame.quit() 