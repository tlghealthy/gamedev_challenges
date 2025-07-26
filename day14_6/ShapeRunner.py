import pygame
import random
import sys

# --- Game Constants ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
FPS = 60
PLAYER_SIZE = 40
OBSTACLE_SIZE = 40
COIN_SIZE = 20
PLAYER_COLOR = (50, 200, 255)
OBSTACLE_COLOR = (255, 60, 60)
COIN_COLOR = (255, 215, 0)
BG_COLOR = (30, 30, 40)
FONT_COLOR = (255, 255, 255)

LEVEL_INTROS = [
    "Level 1: Dodge the falling blocks and collect coins! Survive to the end to advance.",
    "Level 2: Enemy shapes move across your path! Avoid them while still dodging and collecting.",
    "Level 3: Power-ups appear! Grab them for special effects. The chamber scrolls faster—stay sharp!"
]

# --- Game Classes ---
class Player:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH//2 - PLAYER_SIZE//2, SCREEN_HEIGHT-PLAYER_SIZE-10, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = 6
        self.lives = 3
        self.score = 0

    def move(self, dx):
        self.rect.x += dx * self.speed
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_SIZE))

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)

class Obstacle:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH-OBSTACLE_SIZE), -OBSTACLE_SIZE, OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.speed = random.randint(4, 7)

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, OBSTACLE_COLOR, self.rect)

class Coin:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH-COIN_SIZE), -COIN_SIZE, COIN_SIZE, COIN_SIZE)
        self.speed = random.randint(3, 6)

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.ellipse(surface, COIN_COLOR, self.rect)

class Enemy:
    def __init__(self):
        self.size = 36
        self.y = random.randint(80, SCREEN_HEIGHT - 200)
        self.speed = random.choice([-5, -4, 4, 5])
        if self.speed > 0:
            self.x = -self.size
        else:
            self.x = SCREEN_WIDTH
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.color = (180, 80, 255)

    def update(self):
        self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

class PowerUp:
    TYPES = ["shield", "slow"]
    COLORS = {"shield": (60, 255, 120), "slow": (120, 120, 255)}
    def __init__(self):
        self.type = random.choice(self.TYPES)
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH-COIN_SIZE), -COIN_SIZE, COIN_SIZE, COIN_SIZE)
        self.speed = random.randint(4, 7)
        self.color = self.COLORS[self.type]
    def update(self):
        self.rect.y += self.speed
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# --- Game Functions ---
def draw_text(surface, text, size, x, y, center=True):
    font = pygame.font.SysFont("arial", size, bold=True)
    text_surface = font.render(text, True, FONT_COLOR)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def show_intro(surface, level):
    surface.fill(BG_COLOR)
    draw_text(surface, f"{LEVEL_INTROS[level]}", 24, SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    draw_text(surface, "Press any key to start", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+60)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def run_level_1(surface, clock, player):
    obstacles = []
    coins = []
    obstacle_timer = 0
    coin_timer = 0
    level_time = 30 * FPS  # 30 seconds
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        player.move(dx)
        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer > 30:
            obstacles.append(Obstacle())
            obstacle_timer = 0
        # Spawn coins
        coin_timer += 1
        if coin_timer > 60:
            coins.append(Coin())
            coin_timer = 0
        # Update obstacles
        for obs in obstacles[:]:
            obs.update()
            if obs.rect.colliderect(player.rect):
                player.lives -= 1
                obstacles.remove(obs)
                if player.lives <= 0:
                    return False  # Game over
            elif obs.rect.top > SCREEN_HEIGHT:
                obstacles.remove(obs)
        # Update coins
        for coin in coins[:]:
            coin.update()
            if coin.rect.colliderect(player.rect):
                player.score += 10
                coins.remove(coin)
            elif coin.rect.top > SCREEN_HEIGHT:
                coins.remove(coin)
        # Draw everything
        surface.fill(BG_COLOR)
        player.draw(surface)
        for obs in obstacles:
            obs.draw(surface)
        for coin in coins:
            coin.draw(surface)
        draw_text(surface, f"Score: {player.score}", 22, 10, 10, center=False)
        draw_text(surface, f"Lives: {player.lives}", 22, SCREEN_WIDTH-10, 10, center=False)
        pygame.display.flip()
        level_time -= 1
        if level_time <= 0:
            return True  # Level complete

def run_level_2(surface, clock, player):
    obstacles = []
    coins = []
    enemies = []
    obstacle_timer = 0
    coin_timer = 0
    enemy_timer = 0
    level_time = 35 * FPS  # 35 seconds
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        player.move(dx)
        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer > 28:
            obstacles.append(Obstacle())
            obstacle_timer = 0
        # Spawn coins
        coin_timer += 1
        if coin_timer > 55:
            coins.append(Coin())
            coin_timer = 0
        # Spawn enemies
        enemy_timer += 1
        if enemy_timer > 90:
            enemies.append(Enemy())
            enemy_timer = 0
        # Update obstacles
        for obs in obstacles[:]:
            obs.update()
            if obs.rect.colliderect(player.rect):
                player.lives -= 1
                obstacles.remove(obs)
                if player.lives <= 0:
                    return False  # Game over
            elif obs.rect.top > SCREEN_HEIGHT:
                obstacles.remove(obs)
        # Update coins
        for coin in coins[:]:
            coin.update()
            if coin.rect.colliderect(player.rect):
                player.score += 10
                coins.remove(coin)
            elif coin.rect.top > SCREEN_HEIGHT:
                coins.remove(coin)
        # Update enemies
        for enemy in enemies[:]:
            enemy.update()
            if enemy.rect.colliderect(player.rect):
                player.lives -= 1
                enemies.remove(enemy)
                if player.lives <= 0:
                    return False  # Game over
            elif enemy.rect.right < 0 or enemy.rect.left > SCREEN_WIDTH:
                enemies.remove(enemy)
        # Draw everything
        surface.fill(BG_COLOR)
        player.draw(surface)
        for obs in obstacles:
            obs.draw(surface)
        for coin in coins:
            coin.draw(surface)
        for enemy in enemies:
            enemy.draw(surface)
        draw_text(surface, f"Score: {player.score}", 22, 10, 10, center=False)
        draw_text(surface, f"Lives: {player.lives}", 22, SCREEN_WIDTH-10, 10, center=False)
        pygame.display.flip()
        level_time -= 1
        if level_time <= 0:
            return True  # Level complete

def run_level_3(surface, clock, player):
    obstacles = []
    coins = []
    enemies = []
    powerups = []
    obstacle_timer = 0
    coin_timer = 0
    enemy_timer = 0
    powerup_timer = 0
    level_time = 40 * FPS  # 40 seconds
    running = True
    shield_active = False
    shield_timer = 0
    slow_active = False
    slow_timer = 0
    game_speed = 1.3  # Increase speed
    while running:
        clock.tick(int(FPS * (0.7 if slow_active else game_speed)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        player.move(dx)
        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer > 22:
            obstacles.append(Obstacle())
            obstacle_timer = 0
        # Spawn coins
        coin_timer += 1
        if coin_timer > 45:
            coins.append(Coin())
            coin_timer = 0
        # Spawn enemies
        enemy_timer += 1
        if enemy_timer > 70:
            enemies.append(Enemy())
            enemy_timer = 0
        # Spawn powerups
        powerup_timer += 1
        if powerup_timer > 180:
            powerups.append(PowerUp())
            powerup_timer = 0
        # Update obstacles
        for obs in obstacles[:]:
            obs.update()
            if obs.rect.colliderect(player.rect):
                if shield_active:
                    obstacles.remove(obs)
                else:
                    player.lives -= 1
                    obstacles.remove(obs)
                    if player.lives <= 0:
                        return False  # Game over
            elif obs.rect.top > SCREEN_HEIGHT:
                obstacles.remove(obs)
        # Update coins
        for coin in coins[:]:
            coin.update()
            if coin.rect.colliderect(player.rect):
                player.score += 10
                coins.remove(coin)
            elif coin.rect.top > SCREEN_HEIGHT:
                coins.remove(coin)
        # Update enemies
        for enemy in enemies[:]:
            enemy.update()
            if enemy.rect.colliderect(player.rect):
                if shield_active:
                    enemies.remove(enemy)
                else:
                    player.lives -= 1
                    enemies.remove(enemy)
                    if player.lives <= 0:
                        return False  # Game over
            elif enemy.rect.right < 0 or enemy.rect.left > SCREEN_WIDTH:
                enemies.remove(enemy)
        # Update powerups
        for pu in powerups[:]:
            pu.update()
            if pu.rect.colliderect(player.rect):
                if pu.type == "shield":
                    shield_active = True
                    shield_timer = FPS * 4  # 4 seconds
                elif pu.type == "slow":
                    slow_active = True
                    slow_timer = FPS * 4  # 4 seconds
                powerups.remove(pu)
            elif pu.rect.top > SCREEN_HEIGHT:
                powerups.remove(pu)
        # Update timers
        if shield_active:
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False
        if slow_active:
            slow_timer -= 1
            if slow_timer <= 0:
                slow_active = False
        # Draw everything
        surface.fill(BG_COLOR)
        player.draw(surface)
        for obs in obstacles:
            obs.draw(surface)
        for coin in coins:
            coin.draw(surface)
        for enemy in enemies:
            enemy.draw(surface)
        for pu in powerups:
            pu.draw(surface)
        draw_text(surface, f"Score: {player.score}", 22, 10, 10, center=False)
        draw_text(surface, f"Lives: {player.lives}", 22, SCREEN_WIDTH-10, 10, center=False)
        if shield_active:
            draw_text(surface, "SHIELD!", 22, SCREEN_WIDTH//2, 30)
        if slow_active:
            draw_text(surface, "SLOW MOTION!", 22, SCREEN_WIDTH//2, 60)
        pygame.display.flip()
        level_time -= 1
        if level_time <= 0:
            return True  # Level complete

def main():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shape Runner: Chaos Chambers")
    clock = pygame.time.Clock()
    player = Player()
    level = 0
    while True:
        show_intro(surface, level)
        if level == 0:
            level_complete = run_level_1(surface, clock, player)
        elif level == 1:
            level_complete = run_level_2(surface, clock, player)
        elif level == 2:
            level_complete = run_level_3(surface, clock, player)
        else:
            break
        if not level_complete:
            surface.fill(BG_COLOR)
            draw_text(surface, "Game Over! Press any key to exit.", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        pygame.quit()
                        sys.exit()
            break
        level += 1
        if level > 2:
            break  # Only 3 levels
    pygame.quit()

if __name__ == "__main__":
    main() 