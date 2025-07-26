import pygame
import random
import math

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_RADIUS = 30
ORB_RADIUS = 15
ENEMY_RADIUS = 25
ORB_SPAWN_TIME = 1200  # ms
ENEMY_SPAWN_TIME = 2000  # ms

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 200, 255)
ORB_COLOR = (255, 220, 0)
ENEMY_COLOR = (255, 50, 80)
BG_COLOR = (30, 30, 40)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abstract Arcade: Orb Collector")
clock = pygame.time.Clock()

# Player mechanics: Move with mouse, dash with space, collect orbs, avoid enemies
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = PLAYER_RADIUS
        self.color = PLAYER_COLOR
        self.dash_cooldown = 0
        self.dashing = False
        self.dash_timer = 0
        self.dash_dir = (0, 0)

    def update(self, mouse_pos, keys):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.dashing:
            self.x += self.dash_dir[0] * 20
            self.y += self.dash_dir[1] * 20
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
        else:
            self.x, self.y = mouse_pos
            if keys[pygame.K_SPACE] and self.dash_cooldown == 0:
                mx, my = pygame.mouse.get_pos()
                dx, dy = mx - self.x, my - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.dash_dir = (dx / dist, dy / dist)
                    self.dashing = True
                    self.dash_timer = 8
                    self.dash_cooldown = FPS * 2

        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        if self.dash_cooldown > 0:
            pygame.draw.arc(surface, WHITE, (self.x-35, self.y-35, 70, 70), 0, 2*math.pi*(self.dash_cooldown/(FPS*2)), 4)

    def get_rect(self):
        return pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)

class Orb:
    def __init__(self):
        self.x = random.randint(ORB_RADIUS, WIDTH-ORB_RADIUS)
        self.y = random.randint(ORB_RADIUS, HEIGHT-ORB_RADIUS)
        self.radius = ORB_RADIUS
        self.color = ORB_COLOR
        self.angle = random.uniform(0, 2*math.pi)
        self.speed = random.uniform(1, 2)

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        if self.x < self.radius or self.x > WIDTH - self.radius:
            self.angle = math.pi - self.angle
        if self.y < self.radius or self.y > HEIGHT - self.radius:
            self.angle = -self.angle
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)

    def get_rect(self):
        return pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)

class Enemy:
    def __init__(self):
        self.radius = ENEMY_RADIUS
        self.color = ENEMY_COLOR
        # Spawn at random edge
        edge = random.choice(['top','bottom','left','right'])
        if edge == 'top':
            self.x = random.randint(self.radius, WIDTH-self.radius)
            self.y = -self.radius
        elif edge == 'bottom':
            self.x = random.randint(self.radius, WIDTH-self.radius)
            self.y = HEIGHT + self.radius
        elif edge == 'left':
            self.x = -self.radius
            self.y = random.randint(self.radius, HEIGHT-self.radius)
        else:
            self.x = WIDTH + self.radius
            self.y = random.randint(self.radius, HEIGHT-self.radius)
        # Move toward center
        dx, dy = WIDTH//2 - self.x, HEIGHT//2 - self.y
        dist = math.hypot(dx, dy)
        self.vx = dx / dist * random.uniform(2, 3.5)
        self.vy = dy / dist * random.uniform(2, 3.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)

    def get_rect(self):
        return pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)

def main():
    running = True
    player = Player()
    orbs = []
    enemies = []
    score = 0
    last_orb = pygame.time.get_ticks()
    last_enemy = pygame.time.get_ticks()
    font = pygame.font.SysFont(None, 36)
    game_over = False

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return main()

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if not game_over:
            player.update(mouse_pos, keys)

        # Spawn orbs
        if not game_over and pygame.time.get_ticks() - last_orb > ORB_SPAWN_TIME:
            orbs.append(Orb())
            last_orb = pygame.time.get_ticks()
        # Spawn enemies
        if not game_over and pygame.time.get_ticks() - last_enemy > ENEMY_SPAWN_TIME:
            enemies.append(Enemy())
            last_enemy = pygame.time.get_ticks()

        # Update orbs and enemies
        for orb in orbs:
            orb.update()
        for enemy in enemies:
            enemy.update()

        # Collision: player and orbs
        if not game_over:
            for orb in orbs[:]:
                if player.get_rect().colliderect(orb.get_rect()):
                    orbs.remove(orb)
                    score += 1
        # Collision: player and enemies
        if not game_over:
            for enemy in enemies:
                if player.get_rect().colliderect(enemy.get_rect()):
                    game_over = True

        # Draw everything
        screen.fill(BG_COLOR)
        for orb in orbs:
            orb.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        if game_over:
            over_text = font.render("Game Over! Press R to Restart", True, ENEMY_COLOR)
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 30))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main() 