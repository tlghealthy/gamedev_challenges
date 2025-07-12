import os
import json
import pygame
from typing import Tuple, Dict, Any

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULTS = {
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


def load_settings(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(DEFAULTS, f, indent=2)
    with open(path, "r") as f:
        data = json.load(f)
    for key in DEFAULTS:
        if key not in data:
            raise KeyError(f"Missing setting: {key}")
    return data


class Player:
    WIDTH = 48
    HEIGHT = 96
    ATTACK_W = 40
    ATTACK_H = 32

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        controls: Dict[str, int],
        facing: int,
        settings: Dict[str, Any]
    ):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.color = color
        self.controls = controls
        self.facing = facing
        self.damage = 0
        self.attack_cooldown = 0.0
        self.attacking = False
        self.settings = settings

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def feet(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y + self.HEIGHT), self.WIDTH, 4)

    def attack_rect(self) -> pygame.Rect:
        if self.facing >= 0:
            ax = self.x + self.WIDTH
        else:
            ax = self.x - self.ATTACK_W
        ay = self.y + (self.HEIGHT - self.ATTACK_H) // 2
        return pygame.Rect(int(ax), int(ay), self.ATTACK_W, self.ATTACK_H)

    def update(self, keys: pygame.key.ScancodeWrapper, dt: float):
        move_speed = self.settings["MOVE_SPEED"]
        jump_v = self.settings["JUMP_VELOCITY"]
        gravity = self.settings["GRAVITY"]

        left = keys[self.controls["left"]]
        right = keys[self.controls["right"]]
        jump = keys[self.controls["jump"]]
        attack = keys[self.controls["attack"]]

        # Horizontal movement
        self.vx = 0.0
        if left:
            self.vx -= move_speed
            self.facing = -1
        if right:
            self.vx += move_speed
            self.facing = 1

        # Jump
        if jump and self.on_ground:
            self.vy = jump_v
            self.on_ground = False

        # Gravity
        self.vy += gravity

        # Attack
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if attack and self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_cooldown = self.settings["ATTACK_COOLDOWN"]
        else:
            self.attacking = False

    def move_and_collide(self, stage_rect: pygame.Rect):
        # Horizontal
        self.x += self.vx
        # Clamp to screen
        self.x = max(0, min(self.x, self.settings["WIDTH"] - self.WIDTH))

        # Vertical
        self.y += self.vy

        # Platform collision
        player_rect = self.rect()
        if player_rect.colliderect(stage_rect):
            # Only land if falling and feet are above platform
            if self.vy >= 0 and player_rect.bottom - self.vy <= stage_rect.top:
                self.y = stage_rect.top - self.HEIGHT
                self.vy = 0
                self.on_ground = True
            else:
                # Hit from below or side, simple push out
                if player_rect.top < stage_rect.bottom < player_rect.bottom:
                    self.y = stage_rect.bottom
                    self.vy = 0
        else:
            self.on_ground = False

    def apply_knockback(self, direction: int, damage: int):
        base_kb = self.settings["BASE_KB"]
        kb_scalar = self.settings["KB_SCALAR"]
        kb = base_kb + kb_scalar * damage
        self.vx = kb * direction
        self.vy = -0.2 * kb

    def reset(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.damage = 0
        self.attack_cooldown = 0.0
        self.attacking = False
        self.facing = 1


def main():
    settings = load_settings(SETTINGS_PATH)
    pygame.init()
    screen = pygame.display.set_mode((settings["WIDTH"], settings["HEIGHT"]))
    pygame.display.set_caption("2-Player Fighting Platformer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 56)

    # Stage
    stage_w = 800
    stage_h = 40
    stage_x = (settings["WIDTH"] - stage_w) // 2
    stage_y = 500
    stage_rect = pygame.Rect(stage_x, stage_y, stage_w, stage_h)

    # Players
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
    p1_start = (stage_x + 120, stage_y - Player.HEIGHT)
    p2_start = (stage_x + stage_w - 120 - Player.WIDTH, stage_y - Player.HEIGHT)
    p1 = Player(*p1_start, tuple(settings["P1_COLOR"]), p1_controls, 1, settings)
    p2 = Player(*p2_start, tuple(settings["P2_COLOR"]), p2_controls, -1, settings)

    running = True
    winner = None

    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if winner is None:
            # Update players
            p1.update(keys, dt)
            p2.update(keys, dt)
            p1.move_and_collide(stage_rect)
            p2.move_and_collide(stage_rect)

            # Attacks
            for attacker, defender in [(p1, p2), (p2, p1)]:
                if attacker.attacking:
                    if attacker.attack_rect().colliderect(defender.rect()):
                        attacker.attacking = False  # Only one hit per punch
                        defender.damage += settings["DAMAGE_PER_HIT"]
                        defender.apply_knockback(attacker.facing, defender.damage)

            # Out of bounds check
            if p1.y > settings["HEIGHT"]:
                winner = 2
            elif p2.y > settings["HEIGHT"]:
                winner = 1

        else:
            # Freeze, wait for R to restart
            if keys[pygame.K_r]:
                p1.reset(*p1_start)
                p2.reset(*p2_start)
                winner = None

        # Draw
        screen.fill(tuple(settings["BG_COLOR"]))
        pygame.draw.rect(screen, tuple(settings["STAGE_COLOR"]), stage_rect)

        # Draw players (capsule: rect + ellipse ends)
        for player in [p1, p2]:
            body = player.rect()
            pygame.draw.rect(screen, player.color, (body.x, body.y + 16, body.width, body.height - 32))
            pygame.draw.ellipse(screen, player.color, (body.x, body.y, body.width, 32))
            pygame.draw.ellipse(screen, player.color, (body.x, body.y + body.height - 32, body.width, 32))

        # Draw attacks
        for player in [p1, p2]:
            if player.attacking:
                pygame.draw.rect(screen, tuple(settings["ATTACK_COLOR"]), player.attack_rect())

        # Draw damage
        p1_dmg = font.render(f"{p1.damage}", True, (255, 255, 255))
        p2_dmg = font.render(f"{p2.damage}", True, (255, 255, 255))
        screen.blit(p1_dmg, (p1.x + Player.WIDTH // 2 - p1_dmg.get_width() // 2, p1.y - 40))
        screen.blit(p2_dmg, (p2.x + Player.WIDTH // 2 - p2_dmg.get_width() // 2, p2.y - 40))

        # Win message
        if winner:
            msg = f"PLAYER {winner} WINS – press R to restart."
            text = font.render(msg, True, (255, 255, 0))
            screen.blit(
                text,
                (
                    (settings["WIDTH"] - text.get_width()) // 2,
                    settings["HEIGHT"] // 2 - text.get_height() // 2,
                ),
            )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
