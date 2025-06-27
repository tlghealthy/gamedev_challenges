import pygame

class PieGame:
    def __init__(self, width=800, height=600, title="2P Fighting Platformer Demo"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.players = []
        self.platforms = []
        self.gravity = 0.5
        self.bg_color = (30, 30, 40)

    def add_player(self, player):
        self.players.append(player)

    def add_platform(self, platform):
        self.platforms.append(platform)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        for player in self.players:
            player.apply_gravity(self.gravity)
            player.move(self.platforms)

    def draw(self):
        self.screen.fill(self.bg_color)
        for platform in self.platforms:
            platform.draw(self.screen)
        for player in self.players:
            player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

# Example Player and Platform classes for demonstration
class Player:
    def __init__(self, x, y, color=(200, 50, 50)):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = color
        self.vel_y = 0
        self.on_ground = False
        self.speed = 5
        self.jump_power = 12

    def apply_gravity(self, gravity):
        if not self.on_ground:
            self.vel_y += gravity
        else:
            self.vel_y = 0

    def move(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        if self.color == (200, 50, 50):  # Player 1 controls
            if keys[pygame.K_a]:
                dx = -self.speed
            if keys[pygame.K_d]:
                dx = self.speed
            if keys[pygame.K_w] and self.on_ground:
                self.vel_y = -self.jump_power
        else:  # Player 2 controls
            if keys[pygame.K_LEFT]:
                dx = -self.speed
            if keys[pygame.K_RIGHT]:
                dx = self.speed
            if keys[pygame.K_UP] and self.on_ground:
                self.vel_y = -self.jump_power
        self.rect.x += dx
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                self.vel_y = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Platform:
    def __init__(self, x, y, w, h, color=(100, 200, 100)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Example usage (uncomment to run as a script):
# if __name__ == "__main__":
#     game = PieGame()
#     game.add_platform(Platform(100, 500, 600, 30))
#     game.add_player(Player(150, 400, (200, 50, 50)))
#     game.add_player(Player(600, 400, (50, 50, 200)))
#     game.run() 