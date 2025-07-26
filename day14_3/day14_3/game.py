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

# Mechanics: Collect orbs for points, avoid enemies, dash to phase through enemies (cooldown), orbs and enemies move in patterns

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abstract Dash Collector")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

def draw_text(text, x, y, color=(255,255,255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = PLAYER_RADIUS
        self.color = PLAYER_COLOR
        self.speed = 5
        self.dash_cooldown = 0
        self.dashing = False
        self.dash_time = 0

    def move(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        if dx or dy:
            length = math.hypot(dx, dy)
            dx, dy = dx/length, dy/length
            mult = self.speed * (2 if self.dashing else 1)
            self.x += dx * mult
            self.y += dy * mult
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
            self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def dash(self):
        if self.dash_cooldown <= 0:
            self.dashing = True
            self.dash_time = 12  # frames
            self.dash_cooldown = 90  # frames

    def update(self):
        if self.dashing:
            self.dash_time -= 1
            if self.dash_time <= 0:
                self.dashing = False
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

    def draw(self):
        color = (180,255,255) if self.dashing else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        if self.dash_cooldown > 0:
            pygame.draw.arc(screen, (100,255,255), (self.x-30, self.y-30, 60, 60), 0, 2*math.pi*(1-self.dash_cooldown/90), 3)

class Orb:
    def __init__(self):
        self.radius = ORB_RADIUS
        self.color = ORB_COLOR
        self.angle = random.uniform(0, 2*math.pi)
        self.orbit_radius = random.randint(80, 250)
        self.center_x = random.randint(200, WIDTH-200)
        self.center_y = random.randint(150, HEIGHT-150)
        self.speed = random.uniform(0.01, 0.03)
        self.update_pos()

    def update(self):
        self.angle += self.speed
        self.update_pos()

    def update_pos(self):
        self.x = self.center_x + math.cos(self.angle) * self.orbit_radius
        self.y = self.center_y + math.sin(self.angle) * self.orbit_radius

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Enemy:
    def __init__(self):
        self.radius = ENEMY_RADIUS
        self.color = ENEMY_COLOR
        self.angle = random.uniform(0, 2*math.pi)
        self.orbit_radius = random.randint(100, 300)
        self.center_x = random.randint(150, WIDTH-150)
        self.center_y = random.randint(100, HEIGHT-100)
        self.speed = random.uniform(0.012, 0.025)
        self.update_pos()

    def update(self):
        self.angle -= self.speed
        self.update_pos()

    def update_pos(self):
        self.x = self.center_x + math.cos(self.angle) * self.orbit_radius
        self.y = self.center_y + math.sin(self.angle) * self.orbit_radius

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


def collide(a, b):
    return math.hypot(a.x - b.x, a.y - b.y) < a.radius + b.radius

def main():
    player = Player()
    orbs = [Orb() for _ in range(3)]
    enemies = [Enemy() for _ in range(2)]
    score = 0
    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.dash()
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return main()

        keys = pygame.key.get_pressed()
        if not game_over:
            player.move(keys)
            player.update()
            for orb in orbs:
                orb.update()
            for enemy in enemies:
                enemy.update()

            # Collisions
            for orb in orbs:
                if collide(player, orb):
                    score += 1
                    orbs.remove(orb)
                    orbs.append(Orb())
                    break
            for enemy in enemies:
                if collide(player, enemy):
                    if not player.dashing:
                        game_over = True

        # Draw
        screen.fill(BG_COLOR)
        for orb in orbs:
            orb.draw()
        for enemy in enemies:
            enemy.draw()
        player.draw()
        draw_text(f"Score: {score}", 10, 10)
        if player.dash_cooldown > 0:
            draw_text(f"Dash CD: {player.dash_cooldown//FPS+1}s", 10, 50, (100,255,255))
        if game_over:
            draw_text("GAME OVER! Press R to restart", WIDTH//2-180, HEIGHT//2-20, (255,255,255))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main() 