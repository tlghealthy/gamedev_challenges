import pygame
import json
import sys

# Load settings
with open('settings.json') as f:
    S = json.load(f)

# Key bindings
P1_KEYS = {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s, 'attack': pygame.K_LCTRL}
P2_KEYS = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN, 'attack': pygame.K_RCTRL}

pygame.init()
screen = pygame.display.set_mode((S['screen_width'], S['screen_height']))
pygame.display.set_caption('2 Player Fighting Platformer')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# Helper functions
def draw_capsule(surface, color, x, y, w, h, r):
    # Draws a vertical capsule at (x, y) center
    rect = pygame.Rect(x - w//2, y - h//2 + r, w, h - 2*r)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.circle(surface, color, (x, y - h//2 + r), r)
    pygame.draw.circle(surface, color, (x, y + h//2 - r), r)

def clamp(val, mn, mx):
    return max(mn, min(mx, val))

class Player:
    def __init__(self, x, color, face_color, keys, facing):
        self.x = x
        self.y = S['stage_y'] - S['player_height']//2
        self.vx = 0
        self.vy = 0
        self.color = color
        self.face_color = face_color
        self.keys = keys
        self.facing = facing  # 1 for right, -1 for left
        self.on_ground = True
        self.attack_cooldown = 0
        self.attack_timer = 0
        self.damage = 0
        self.hit_flash = 0
        self.last_attack_dir = 1

    def rect(self):
        return pygame.Rect(self.x - S['player_width']//2, self.y - S['player_height']//2, S['player_width'], S['player_height'])

    def face_pos(self):
        # Offset in facing direction
        return (int(self.x + self.facing * S['face_offset']), int(self.y - S['player_height']//2 + S['face_radius'] + 4))

    def attack_rect(self):
        # Attack hitbox in front of player
        ax = self.x + self.facing * (S['player_width']//2 + S['face_radius'] + 8)
        ay = self.y - S['player_height']//4
        return pygame.Rect(ax - 18, ay - 18, 36, 36)

    def update(self, keys, stage_rect):
        # Movement
        move = 0
        if keys[self.keys['left']]:
            move -= 1
        if keys[self.keys['right']]:
            move += 1
        if move != 0:
            self.facing = move
        # Only apply movement if not being knocked back
        if self.hit_flash == 0:
            self.vx = move * S['move_speed']
        else:
            # Preserve knockback velocity but allow some movement influence (reduced for floatiness)
            self.vx += move * S['move_speed'] * 0.15
        # Jump
        if keys[self.keys['up']] and self.on_ground:
            self.vy = S['jump_velocity']
            self.on_ground = False
        # Gravity (reduced for floatiness)
        self.vy += S['gravity']
        # Apply velocity
        self.x += self.vx
        self.y += self.vy
        # Stage collision (platform)
        player_bottom = self.y + S['player_height']//2
        if (stage_rect.left < self.x < stage_rect.right) and (player_bottom >= stage_rect.top) and (self.vy >= 0):
            self.y = stage_rect.top - S['player_height']//2
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False
        # Screen bounds with velocity zeroing
        min_x = S['player_width']//2
        max_x = S['screen_width'] - S['player_width']//2
        if self.x < min_x:
            self.x = min_x
            if self.vx < 0:
                self.vx = 0
        elif self.x > max_x:
            self.x = max_x
            if self.vx > 0:
                self.vx = 0
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def start_attack(self):
        if self.attack_cooldown == 0:
            self.attack_timer = S['attack_duration']
            self.attack_cooldown = S['attack_cooldown']
            self.last_attack_dir = self.facing

    def is_attacking(self):
        return self.attack_timer > 0

    def take_hit(self, from_dir):
        self.damage += S['attack_damage']
        scale = 1 + self.damage * S['damage_knockback_scale']
        self.vx = from_dir * S['attack_knockback'] * scale
        self.vy = -S['attack_upward_knockback'] * scale
        self.hit_flash = 8

    def draw(self, surface):
        # Body
        draw_capsule(surface, self.color, int(self.x), int(self.y), S['player_width'], S['player_height'], S['player_radius'])
        # Face
        face_pos = self.face_pos()
        pygame.draw.circle(surface, self.face_color, face_pos, S['face_radius'])
        # Attack flash
        if self.is_attacking():
            attack_rect = self.attack_rect()
            color = S['attack_flash_color1'] if self.color == S['player1_color'] else S['attack_flash_color2']
            pygame.draw.ellipse(surface, color, attack_rect, 0)
        # Hit flash
        if self.hit_flash > 0:
            pygame.draw.circle(surface, (255,255,0), (int(self.x), int(self.y - S['player_height']//2)), 18, 3)
        # Damage text
        dmg = font.render(str(self.damage), True, S['font_color'])
        surface.blit(dmg, (self.x - 18, self.y - S['player_height']//2 - 36))

def main():
    # Stage
    stage_rect = pygame.Rect((S['screen_width'] - S['stage_width'])//2, S['stage_y'], S['stage_width'], S['stage_height'])
    # Players
    p1 = Player(stage_rect.left + S['player_width']*2, S['player1_color'], S['face1_color'], P1_KEYS, 1)
    p2 = Player(stage_rect.right - S['player_width']*2, S['player2_color'], S['face2_color'], P2_KEYS, -1)
    running = True
    winner = None
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if winner and event.key == pygame.K_r:
                    main()  # Restart
                if not winner:
                    if event.key == p1.keys['attack']:
                        p1.start_attack()
                    if event.key == p2.keys['attack']:
                        p2.start_attack()
        if not winner:
            p1.update(keys, stage_rect)
            p2.update(keys, stage_rect)
            # Attacks
            if p1.is_attacking() and p1.attack_rect().colliderect(p2.rect()):
                if p2.hit_flash == 0:
                    p2.take_hit(p1.last_attack_dir)
            if p2.is_attacking() and p2.attack_rect().colliderect(p1.rect()):
                if p1.hit_flash == 0:
                    p1.take_hit(p2.last_attack_dir)
            # Win condition
            if p1.y - S['player_height']//2 > S['screen_height']:
                winner = 'Blue Wins!'
            elif p2.y - S['player_height']//2 > S['screen_height']:
                winner = 'Red Wins!'
        # Draw
        screen.fill(S['background_color'])
        pygame.draw.rect(screen, S['platform_color'], stage_rect)
        p1.draw(screen)
        p2.draw(screen)
        if winner:
            text = font.render(winner, True, (255,255,0))
            screen.blit(text, (S['screen_width']//2 - text.get_width()//2, 120))
            sub = font.render('Press R to restart', True, (200,200,200))
            screen.blit(sub, (S['screen_width']//2 - sub.get_width()//2, 180))
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main() 