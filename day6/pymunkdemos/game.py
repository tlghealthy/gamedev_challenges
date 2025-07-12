import os
import json
import sys
import pygame
from physics import Physics

class Settings:
    """Loads and stores all tunable game constants from settings.json."""
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.defaults = {
            "WIDTH": 1280,
            "HEIGHT": 720,
            "BG_COLOR": [0, 0, 0],
            "STAGE_COLOR": [200, 200, 200],
            "P1_COLOR": [255, 0, 0],
            "P2_COLOR": [0, 128, 255],
            "ATTACK_COLOR": [255, 255, 0],
            "GRAVITY": 1.0,
            "MOVE_SPEED": 6.0,
            "JUMP_VELOCITY": -18.0,
            "ATTACK_COOLDOWN": 0.4,
            "DAMAGE_PER_HIT": 10,
            "BASE_KB": 5,
            "KB_SCALAR": 0.25
        }
        self._ensure_file()
        self._load()

    def _ensure_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump(self.defaults, f, indent=2)

    def _load(self):
        with open(self.filename, "r") as f:
            data = json.load(f)
        for k, v in self.defaults.items():
            setattr(self, k, data.get(k, v))

class Stage:
    """Represents the main platform in the game."""
    def __init__(self, physics, settings):
        self.settings = settings
        w = settings.WIDTH
        y = 500
        width = 800
        height = 40
        self.rect = pygame.Rect((w - width) // 2, y, width, height)
        # Use Physics.add_platform for the main stage
        start_px = (self.rect.left, y + height // 2)
        end_px = (self.rect.right, y + height // 2)
        self.body, self.shape = physics.add_platform(start_px, end_px, thickness=height)

    def draw(self, surf):
        pygame.draw.rect(surf, self.settings.STAGE_COLOR, self.rect)

class Player:
    """Encapsulates player state, movement, drawing, attack, and knockback logic."""
    WIDTH = 50
    HEIGHT = 90

    def __init__(self, physics, settings, pos, color, controls, face_left):
        self.settings = settings
        self.color = color
        self.controls = controls
        self.face_left = face_left
        self.facing = -1 if face_left else 1
        self.on_ground = False
        self.damage = 0
        self.attack_cooldown = 0
        self.attacking = False
        self.last_attack_time = 0
        self.spawn_pos = pos

        # Use Physics.add_player
        self.body, self.shape, self.foot_sensor = physics.add_player(pos, size_px=(self.WIDTH, self.HEIGHT), mass=2, friction=0.8)
        self.shape.player_ref = self
        self.physics = physics

    def reset(self):
        self.body.position = self.spawn_pos
        self.body.velocity = (0, 0)
        self.damage = 0
        self.attack_cooldown = 0
        self.attacking = False
        self.facing = -1 if self.face_left else 1

    def handle_input(self, keys, dt):
        move = 0
        if keys[self.controls["left"]]:
            move -= 1
        if keys[self.controls["right"]]:
            move += 1
        if move != 0:
            self.facing = move
        vx, vy = self.body.velocity
        self.body.velocity = (move * self.settings.MOVE_SPEED * 60, vy)
        if keys[self.controls["jump"]] and self.on_ground:
            self.body.velocity = (self.body.velocity[0], self.settings.JUMP_VELOCITY * 60)
            self.on_ground = False

    def try_attack(self, keys, now):
        if self.attack_cooldown > 0:
            return None
        if keys[self.controls["attack"]]:
            self.attacking = True
            self.attack_cooldown = self.settings.ATTACK_COOLDOWN
            self.last_attack_time = now
            return self._make_attack_hitbox()
        return None

    def _make_attack_hitbox(self):
        # Rectangle 40px in front of player, 40x30
        offset = (self.WIDTH // 2 + 20) * self.facing
        x = self.body.position.x + offset
        y = self.body.position.y
        rect = pygame.Rect(0, 0, 40, 30)
        rect.center = (x, y)
        return rect

    def update(self, dt, stage_rect):
        # Cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - dt)
        if self.attack_cooldown == 0:
            self.attacking = False

    def apply_knockback(self, vec):
        self.body.velocity = (vec[0] * 60, vec[1] * 60)

    def draw(self, surf):
        # Draw body
        x, y = self.body.position
        rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        rect.center = (int(x), int(y))
        pygame.draw.rect(surf, self.color, rect)
        # Draw face triangle
        face_color = (0, 255, 0) if not self.attacking and self.attack_cooldown == 0 else (255, 255, 0)
        tri = self._face_triangle(rect, self.facing)
        pygame.draw.polygon(surf, face_color, tri)
        # Draw damage
        font = pygame.font.SysFont(None, 28)
        dmg_surf = font.render(str(self.damage), True, (255, 255, 255))
        surf.blit(dmg_surf, (rect.centerx - 12, rect.top - 28))

    def _face_triangle(self, rect, facing):
        # Small triangle on front edge
        cx, cy = rect.center
        if facing == 1:
            tip = (rect.right + 10, cy)
            base1 = (rect.right, cy - 10)
            base2 = (rect.right, cy + 10)
        else:
            tip = (rect.left - 10, cy)
            base1 = (rect.left, cy - 10)
            base2 = (rect.left, cy + 10)
        return [tip, base1, base2]

    def get_bottom(self):
        return self.body.position.y + self.HEIGHT // 2

    def set_on_ground(self, value):
        self.on_ground = value

class Game:
    """Owns the main loop and all game state."""
    def __init__(self):
        self.settings = Settings()
        pygame.init()
        self.screen = pygame.display.set_mode((self.settings.WIDTH, self.settings.HEIGHT))
        pygame.display.set_caption("Fighting Platformer Prototype")
        self.clock = pygame.time.Clock()
        gravity = (0, self.settings.GRAVITY * 60 * 60)
        self.physics = Physics(gravity=gravity)
        self.stage = Stage(self.physics, self.settings)
        self.players = self._make_players()
        self._setup_ground_sensor()
        self.running = True
        self.winner = None

    def _setup_ground_sensor(self):
        def begin_sensor(arbiter, space, data):
            for p in self.players:
                if arbiter.shapes[0] == p.foot_sensor or arbiter.shapes[1] == p.foot_sensor:
                    p.set_on_ground(True)
            return True

        def separate_sensor(arbiter, space, data):
            for p in self.players:
                if arbiter.shapes[0] == p.foot_sensor or arbiter.shapes[1] == p.foot_sensor:
                    p.set_on_ground(False)
            return True

        self.physics.on("SENSOR", "FLOOR", begin=begin_sensor, separate=separate_sensor)

    def _make_players(self):
        w = self.settings.WIDTH
        # Align player bottom with platform collision line
        platform_y = self.stage.rect.top + self.stage.rect.height // 2
        y = platform_y - Player.HEIGHT // 2
        p1x = w // 2 - 150
        p2x = w // 2 + 150
        p1_controls = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "attack": pygame.K_LCTRL
        }
        p2_controls = {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "attack": pygame.K_RCTRL
        }
        p1 = Player(self.physics, self.settings, (p1x, y), self.settings.P1_COLOR, p1_controls, face_left=False)
        p2 = Player(self.physics, self.settings, (p2x, y), self.settings.P2_COLOR, p2_controls, face_left=True)
        return [p1, p2]

    def reset(self):
        for p in self.players:
            p.reset()
        self.winner = None

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            if not self.winner:
                self._update(dt)
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.winner and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    def _update(self, dt):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks() / 1000.0
        # Player input and attack
        attacks = []
        for p in self.players:
            p.handle_input(keys, dt)
            atk = p.try_attack(keys, now)
            if atk:
                attacks.append((p, atk))
        # Physics step
        for p in self.players:
            p.update(dt, self.stage.rect)
        self.physics.step(dt)
        # Attack collision
        if attacks:
            for idx, (attacker, hitbox) in enumerate(attacks):
                defender = self.players[1 - idx]
                def_rect = pygame.Rect(0, 0, defender.WIDTH, defender.HEIGHT)
                def_rect.center = (int(defender.body.position.x), int(defender.body.position.y))
                if hitbox.colliderect(def_rect):
                    defender.damage += self.settings.DAMAGE_PER_HIT
                    kb = self.settings.BASE_KB + defender.damage * self.settings.KB_SCALAR
                    vec = (kb * attacker.facing, -kb * 0.2)
                    defender.apply_knockback(vec)
        # Win check
        for i, p in enumerate(self.players):
            if p.get_bottom() > self.settings.HEIGHT:
                self.winner = 2 if i == 0 else 1

    def _draw(self):
        self.screen.fill(self.settings.BG_COLOR)
        self.stage.draw(self.screen)
        for p in self.players:
            p.draw(self.screen)
        # Draw attack hitboxes (for one frame)
        for p in self.players:
            if p.attacking and p.attack_cooldown > self.settings.ATTACK_COOLDOWN - 0.05:
                hitbox = p._make_attack_hitbox()
                pygame.draw.rect(self.screen, self.settings.ATTACK_COLOR, hitbox)
        if self.winner:
            self._draw_winner()
        pygame.display.flip()

    def _draw_winner(self):
        font = pygame.font.SysFont(None, 72)
        text = f"PLAYER {self.winner} WINS – press R to restart"
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT // 2))
        self.screen.blit(surf, rect)

if __name__ == "__main__":
    Game().run()