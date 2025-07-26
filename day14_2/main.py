import pygame
import random
import sys

# --- Game Constants ---
WIDTH, HEIGHT = 600, 800
FPS = 60
SHAPES = ['circle', 'square', 'triangle']
COLORS = [(255, 0, 0), (0, 255, 0), (0, 128, 255)]  # Red, Green, Blue
BG_COLOR = (30, 30, 30)
OBSTACLE_SPEED = 4
POWERUP_SPEED = 4
MORPH_KEY = pygame.K_SPACE

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('ShapeShift Showdown')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- Helper Functions ---
def draw_shape(surface, shape, color, pos, size):
    x, y = pos
    if shape == 'circle':
        pygame.draw.circle(surface, color, (x, y), size)
    elif shape == 'square':
        pygame.draw.rect(surface, color, (x - size, y - size, size * 2, size * 2))
    elif shape == 'triangle':
        points = [
            (x, y - size),
            (x - size, y + size),
            (x + size, y + size)
        ]
        pygame.draw.polygon(surface, color, points)

def random_shape_color():
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    return shape, color

# --- Classes ---
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.size = 32
        self.shape_idx = 0
        self.color_idx = 0
        self.speed = 8
        self.invincible = 0  # frames

    @property
    def shape(self):
        return SHAPES[self.shape_idx]

    @property
    def color(self):
        return COLORS[self.color_idx]

    def morph(self):
        self.shape_idx = (self.shape_idx + 1) % len(SHAPES)
        self.color_idx = (self.color_idx + 1) % len(COLORS)

    def move(self, dx, dy):
        self.x = max(self.size, min(WIDTH - self.size, self.x + dx))
        self.y = max(self.size, min(HEIGHT - self.size, self.y + dy))

    def draw(self, surface):
        if self.invincible > 0 and (self.invincible // 5) % 2 == 0:
            return  # Flicker effect
        draw_shape(surface, self.shape, self.color, (self.x, self.y), self.size)

class Obstacle:
    def __init__(self, y):
        self.shape, self.color = random_shape_color()
        self.size = random.randint(24, 40)
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = y
        self.passed = False

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        draw_shape(surface, self.shape, self.color, (self.x, self.y), self.size)

    def collide(self, player):
        if abs(self.x - player.x) < self.size + player.size and abs(self.y - player.y) < self.size + player.size:
            return self.shape == player.shape and self.color == player.color
        return None

class PowerUp:
    def __init__(self, y):
        self.kind = random.choice(['score', 'invincible', 'speed'])
        self.color = (255, 255, 0) if self.kind == 'score' else (255, 0, 255) if self.kind == 'invincible' else (0, 255, 255)
        self.size = 20
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = y
        self.active = True

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x - self.size, self.y - self.size, self.size * 2, self.size * 2), 3)

    def collide(self, player):
        if abs(self.x - player.x) < self.size + player.size and abs(self.y - player.y) < self.size + player.size:
            return True
        return False

# --- Game Loop ---
def main():
    player = Player()
    obstacles = []
    powerups = []
    score = 0
    speed = OBSTACLE_SPEED
    spawn_timer = 0
    powerup_timer = 0
    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if not game_over and event.key == MORPH_KEY:
                    player.morph()
                if game_over and event.key == pygame.K_RETURN:
                    return main()

        keys = pygame.key.get_pressed()
        if not game_over:
            dx = dy = 0
            if keys[pygame.K_LEFT]: dx -= player.speed
            if keys[pygame.K_RIGHT]: dx += player.speed
            if keys[pygame.K_UP]: dy -= player.speed
            if keys[pygame.K_DOWN]: dy += player.speed
            player.move(dx, dy)

        # Spawn obstacles
        if not game_over:
            spawn_timer += 1
            if spawn_timer > max(20, 60 - score // 10):
                obstacles.append(Obstacle(-40))
                spawn_timer = 0
            # Spawn powerups
            powerup_timer += 1
            if powerup_timer > 180:
                powerups.append(PowerUp(-40))
                powerup_timer = 0

        # Update obstacles
        for obs in obstacles:
            obs.update(speed)
        obstacles = [o for o in obstacles if o.y < HEIGHT + 50]

        # Update powerups
        for pu in powerups:
            pu.update(POWERUP_SPEED)
        powerups = [p for p in powerups if p.y < HEIGHT + 50 and p.active]

        # Collision detection
        if not game_over:
            for obs in obstacles:
                result = obs.collide(player)
                if result is not None and not obs.passed:
                    if result or player.invincible > 0:
                        score += 10
                        obs.passed = True
                    else:
                        game_over = True
            for pu in powerups:
                if pu.collide(player) and pu.active:
                    if pu.kind == 'score':
                        score += 50
                    elif pu.kind == 'invincible':
                        player.invincible = FPS * 2
                    elif pu.kind == 'speed':
                        player.speed = 14
                    pu.active = False

        # Invincibility timer
        if player.invincible > 0:
            player.invincible -= 1
        else:
            player.speed = 8

        # Increase speed over time
        if not game_over and score > 0 and score % 100 == 0:
            speed = min(12, OBSTACLE_SPEED + score // 100)

        # --- Drawing ---
        screen.fill(BG_COLOR)
        for obs in obstacles:
            obs.draw(screen)
        for pu in powerups:
            pu.draw(screen)
        player.draw(screen)
        score_surf = font.render(f'Score: {score}', True, (255,255,255))
        screen.blit(score_surf, (10, 10))
        if player.invincible > 0:
            inv_surf = font.render('INVINCIBLE!', True, (255,255,0))
            screen.blit(inv_surf, (WIDTH//2-80, 10))
        if game_over:
            over_surf = font.render('GAME OVER! Press Enter to Restart', True, (255,80,80))
            screen.blit(over_surf, (WIDTH//2-180, HEIGHT//2-20))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 