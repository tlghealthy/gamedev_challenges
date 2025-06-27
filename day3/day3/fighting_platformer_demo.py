import pygame
import json
import os
from pie_game import PieGame, Platform

# Load settings
with open(os.path.join(os.path.dirname(__file__), 'settings.json')) as f:
    S = json.load(f)

# Helper for tuple colors
C = lambda k: tuple(S[k])

class Fighter:
    def __init__(self, x, y, color, face_color, attack_flash_color, controls):
        self.x = x
        self.y = y
        self.width = S["player_width"]
        self.height = S["player_height"]
        self.color = color
        self.face_color = face_color
        self.attack_flash_color = attack_flash_color
        self.controls = controls
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing = 1  # 1=right, -1=left
        self.damage = 0
        self.attack_cooldown = 0
        self.attack_timer = 0
        self.attacking = False
        self.last_attack_time = 0
        self.knockback = 0
        self.flash = False
        self.flash_timer = 0

    def apply_gravity(self, gravity):
        if not self.on_ground:
            self.vel_y += gravity
        else:
            self.vel_y = 0

    def move(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[self.controls['left']]:
            dx = -S["player_speed"]
            self.facing = -1
        if keys[self.controls['right']]:
            dx = S["player_speed"]
            self.facing = 1
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = -S["jump_power"]
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
        # Stay in bounds
        self.rect.x = max(0, min(self.rect.x, S["screen_width"]-self.width))
        self.x, self.y = self.rect.x, self.rect.y

    def update_attack(self, now):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1/60
        if self.attacking:
            self.attack_timer -= 1/60
            if self.attack_timer <= 0:
                self.attacking = False
                self.flash = False

    def try_attack(self, now):
        if self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_timer = S["attack_duration"]
            self.attack_cooldown = S["attack_cooldown"]
            self.flash = True
            self.flash_timer = S["attack_duration"]
            self.last_attack_time = now

    def draw(self, surface):
        # Draw capsule body
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=self.width//2)
        # Draw face
        face_center = (int(self.x + self.width//2 + self.facing*(self.width//3)), int(self.y + self.height//4))
        pygame.draw.circle(surface, self.face_color, face_center, S["face_radius"])
        # Draw attack flash
        if self.flash:
            attack_x = self.x + (self.width//2) + self.facing*(S["attack_range"])
            attack_y = self.y + self.height//2
            pygame.draw.circle(surface, self.attack_flash_color, (int(attack_x), int(attack_y)), S["face_radius"]+4)

    def get_attack_rect(self):
        if self.attacking:
            attack_x = self.x + (self.width//2) + self.facing*(S["attack_range"])
            attack_y = self.y + self.height//2
            return pygame.Rect(attack_x-12, attack_y-12, 24, 24)
        return None

    def take_hit(self, from_facing):
        self.damage = min(self.damage + S["attack_damage"], S["max_damage"])
        kb = S["attack_knockback_base"] + self.damage*0.08
        self.vel_x = kb * from_facing
        self.vel_y = -S["attack_knockback_up"]

    def apply_knockback(self):
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        self.vel_x *= 0.85
        if abs(self.vel_x) < 0.5:
            self.vel_x = 0

# Controls
controls1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'attack': pygame.K_LCTRL}
controls2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'attack': pygame.K_RCTRL}

def main():
    game = PieGame(S["screen_width"], S["screen_height"])
    platform = Platform(*S["platform_rect"], color=C("platform_color"))
    game.add_platform(platform)
    p1 = Fighter(180, 400, C("player1_color"), C("face_color1"), C("attack_flash_color1"), controls1)
    p2 = Fighter(580, 400, C("player2_color"), C("face_color2"), C("attack_flash_color2"), controls2)
    game.add_player(p1)
    game.add_player(p2)
    winner = None
    font = pygame.font.SysFont(None, 48)
    while game.running:
        game.handle_events()
        now = pygame.time.get_ticks()/1000
        # Input and update
        for i, player in enumerate(game.players):
            player.apply_gravity(S["gravity"])
            player.move(game.platforms)
            player.apply_knockback()
            player.update_attack(now)
        # Player-vs-player collision (momentum-based, dampened bounce)
        p1, p2 = game.players
        if p1.rect.colliderect(p2.rect):
            overlap = p1.rect.clip(p2.rect)
            if overlap.width > 0:
                # Dampen factor for bounce
                DAMP = S["player_bounce_damp"]
                # Exchange a portion of horizontal velocities
                v1, v2 = p1.vel_x, p2.vel_x
                p1.vel_x = v2 * DAMP
                p2.vel_x = v1 * DAMP
                # Now resolve overlap as before (momentum-based push)
                total_vel = abs(p1.vel_x) + abs(p2.vel_x) + 1e-5
                if total_vel > 0:
                    p1_push = abs(p2.vel_x) / total_vel
                    p2_push = abs(p1.vel_x) / total_vel
                else:
                    p1_push = p2_push = 0.5
                if p1.rect.centerx < p2.rect.centerx:
                    p1.rect.x -= int(overlap.width * p1_push)
                    p2.rect.x += int(overlap.width * p2_push)
                else:
                    p1.rect.x += int(overlap.width * p1_push)
                    p2.rect.x -= int(overlap.width * p2_push)
                # Always resolve at least 1 pixel if stuck
                if p1.rect.colliderect(p2.rect):
                    if p1.rect.centerx < p2.rect.centerx:
                        p1.rect.x -= 1
                        p2.rect.x += 1
                    else:
                        p1.rect.x += 1
                        p2.rect.x -= 1
                p1.x, p1.y = p1.rect.x, p1.rect.y
                p2.x, p2.y = p2.rect.x, p2.rect.y
        # Attacks
        keys = pygame.key.get_pressed()
        if keys[controls1['attack']]:
            p1.try_attack(now)
        if keys[controls2['attack']]:
            p2.try_attack(now)
        # Check attack collisions
        for attacker, defender in [(p1, p2), (p2, p1)]:
            arect = attacker.get_attack_rect()
            if arect and arect.colliderect(defender.rect) and attacker.attacking and not defender.flash:
                defender.take_hit(attacker.facing)
                defender.flash = True
                defender.flash_timer = S["attack_duration"]
        # Flash timer
        for player in [p1, p2]:
            if player.flash:
                player.flash_timer -= 1/60
                if player.flash_timer <= 0:
                    player.flash = False
        # Check for falling off
        for i, player in enumerate([p1, p2]):
            if player.rect.top > S["screen_height"]:
                winner = 2 if i == 0 else 1
                game.running = False
        # Draw
        game.screen.fill(C("bg_color"))
        for platform in game.platforms:
            platform.draw(game.screen)
        for player in game.players:
            player.draw(game.screen)
        # Draw damage
        d1 = font.render(f"P1: {p1.damage}", True, C("player1_color"))
        d2 = font.render(f"P2: {p2.damage}", True, C("player2_color"))
        game.screen.blit(d1, (30, 30))
        game.screen.blit(d2, (S["screen_width"]-150, 30))
        pygame.display.flip()
        game.clock.tick(60)
    # Game over
    if winner:
        game.screen.fill((0,0,0))
        msg = font.render(f"Player {winner} wins!", True, (255,255,0))
        game.screen.blit(msg, (S["screen_width"]//2-120, S["screen_height"]//2-30))
        pygame.display.flip()
        pygame.time.wait(3000)

if __name__ == "__main__":
    main() 