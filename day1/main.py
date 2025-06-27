import sys, json, pathlib, pygame
from pygame import Rect, Vector2

# ------------------------------------------------------------- CONFIG LOAD
ROOT = pathlib.Path(__file__).parent
C    = json.loads((ROOT / "settings.json").read_text())

SCR_W, SCR_H, FPS = C["screen_width"], C["screen_height"], C["fps"]

GRAVITY   = C["gravity"]
JUMP_VEL  = C["jump_velocity"]
MOVE_SPD  = C["move_speed"]
AIR_CTR   = C["air_control_factor"]

ATK_CD    = C["attack_cooldown_ms"]
ATK_DUR   = C["attack_duration_ms"]
ATK_RNG   = C["attack_range"]
ATK_DMG   = C["attack_damage"]

KNOCK_B   = C["base_knockback"]
KNOCK_S   = C["knockback_scaling"]
KNOCK_UP  = C["upward_knockback"]

HITSTUN   = C["hitstun_ms"]
FRICTION  = C["horizontal_friction"]

STAGE     = Rect(*C["stage_rect"])
PW, PH    = C["player_width"], C["player_height"]
FACE      = C["face_size"]

UI_SZ     = C["ui_font_size"]
BAR_W     = C["damage_bar"]["width"]
BAR_H     = C["damage_bar"]["height"]
BAR_LO    = C["damage_bar"]["low"]
BAR_HI    = C["damage_bar"]["high"]

COL       = C["colours"]

# ------------------------------------------------------------- UTILITIES
def lerp(a, b, t):
    return a + (b - a) * t

def lerp_col(lo, hi, t):
    return [round(lerp(lo[i], hi[i], t)) for i in range(3)]

# ------------------------------------------------------------- PLAYER CLASS
class Player:
    def __init__(self, x, y, body_c, face_c, keys):
        self.pos   = Vector2(x, y)
        self.vel   = Vector2()
        self.rect  = Rect(x, y, PW, PH)

        self.facing     = 1
        self.on_ground  = False
        self.prev_jump  = False       # for edge-trigger jump

        self.keys   = keys
        self.body_c = body_c
        self.face_c = face_c

        self.damage = 0
        self.last_atk    = -ATK_CD
        self.hitstun_end = 0

    # ------------------------------------------------ INPUT
    def handle_input(self, k, now):
        if now < self.hitstun_end:
            self.prev_jump = k[self.keys["jump"]]
            return

        input_x = 0
        if k[self.keys["left"]]:
            input_x, self.facing = -1, -1
        if k[self.keys["right"]]:
            input_x, self.facing =  1,  1

        if self.on_ground:
            self.vel.x = input_x * MOVE_SPD
        else:
            target = input_x * MOVE_SPD
            self.vel.x += (target - self.vel.x) * AIR_CTR

        # Jump on key-down only
        jump_now = k[self.keys["jump"]]
        if jump_now and not self.prev_jump and self.on_ground:
            self.vel.y = JUMP_VEL
            self.on_ground = False
        self.prev_jump = jump_now

    # ------------------------------------------------ PHYSICS
    def physics(self):
        self.vel.x *= FRICTION
        self.vel.y += GRAVITY
        self.pos   += self.vel

        # ------- FIX: update rect *before* collision test -------
        self.rect.topleft = self.pos

        # stage collision (inclusive edges)
        if (self.rect.bottom >= STAGE.top and
            STAGE.left <= self.rect.centerx <= STAGE.right):
            # clamp to floor
            self.rect.bottom = STAGE.top
            self.pos.y = self.rect.top
            self.vel.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    # ------------------------------------------------ ATTACKS
    def pressed_attack(self, now):
        if now - self.last_atk >= ATK_CD:
            self.last_atk = now
            return True
        return False

    def attacking(self, now):
        return now - self.last_atk < ATK_DUR

    def hitbox(self):
        offset = (PW // 2 + ATK_RNG) * self.facing
        left   = self.rect.centerx + min(0, offset)
        return Rect(left, self.rect.top, abs(offset), PH)

    # ------------------------------------------------ DAMAGE / KNOCK-BACK
    def take_hit(self, direction, now):
        impulse = KNOCK_B + self.damage * KNOCK_S
        self.vel.x += impulse * direction
        self.vel.y  = -KNOCK_UP
        self.damage += ATK_DMG
        self.hitstun_end = now + HITSTUN

    # ------------------------------------------------ DRAW
    def draw(self, surf, now, font):
        # capsule body
        pygame.draw.rect(surf, self.body_c,
                         (self.rect.x, self.rect.y + FACE, PW, PH - 2*FACE))
        pygame.draw.circle(surf, self.body_c,
                           (self.rect.centerx, self.rect.y + FACE), FACE)
        pygame.draw.circle(surf, self.body_c,
                           (self.rect.centerx, self.rect.bottom - FACE), FACE)

        # face indicator
        eye = (self.rect.centerx + self.facing * (FACE // 2),
               self.rect.y + FACE // 2)
        pygame.draw.circle(surf, self.face_c, eye, FACE // 3)

        # attack flash
        if self.attacking(now):
            pygame.draw.rect(surf, COL["attack_flash"], self.hitbox(), 2)

        # damage UI
        dmg_txt = font.render(f"{self.damage}%", True, COL["text"])
        surf.blit(dmg_txt,
                  dmg_txt.get_rect(center=(self.rect.centerx,
                                           self.rect.y - 28)))

        t = min(self.damage / 200.0, 1.0)
        bar_col = lerp_col(BAR_LO, BAR_HI, t)
        pygame.draw.rect(surf, bar_col,
                         (self.rect.centerx - BAR_W // 2, self.rect.y - 18,
                          BAR_W * t, BAR_H))
        pygame.draw.rect(surf, COL["text"],
                         (self.rect.centerx - BAR_W // 2, self.rect.y - 18,
                          BAR_W, BAR_H), 1)

# ------------------------------------------------------------- MAIN LOOP
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCR_W, SCR_H))
    pygame.display.set_caption("Tiny Platform Fighter")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont(None, UI_SZ)
    font_big   = pygame.font.SysFont(None, 48)

    p1 = Player(
        STAGE.left + 120, STAGE.top - PH,
        COL["p1_body"], COL["p1_face"],
        dict(left=pygame.K_a, right=pygame.K_d,
             jump=pygame.K_w, attack=pygame.K_LCTRL))

    p2 = Player(
        STAGE.right - 120 - PW, STAGE.top - PH,
        COL["p2_body"], COL["p2_face"],
        dict(left=pygame.K_LEFT, right=pygame.K_RIGHT,
             jump=pygame.K_UP, attack=pygame.K_RCTRL))

    winner = None
    while True:
        dt  = clock.tick(FPS)
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and winner:
                main()  # restart
                return
            if ev.type == pygame.KEYDOWN:
                if ev.key == p1.keys["attack"]:
                    p1.pressed_attack(now)
                if ev.key == p2.keys["attack"]:
                    p2.pressed_attack(now)

        if not winner:
            p1.handle_input(keys, now);  p2.handle_input(keys, now)
            p1.physics();                p2.physics()

            if p1.attacking(now) and p1.hitbox().colliderect(p2.rect):
                p2.take_hit(p1.facing, now)
            if p2.attacking(now) and p2.hitbox().colliderect(p1.rect):
                p1.take_hit(p2.facing, now)

            if p1.rect.top > SCR_H: winner = "BLUE WINS!"
            elif p2.rect.top > SCR_H: winner = "RED WINS!"

        # draw
        screen.fill(COL["bg"])
        pygame.draw.rect(screen, COL["stage"], STAGE)

        p1.draw(screen, now, font_small)
        p2.draw(screen, now, font_small)

        if winner:
            txt = font_big.render(
                winner + "  (press any key)", True, COL["text"])
            screen.blit(txt, txt.get_rect(center=(SCR_W // 2, SCR_H // 3)))

        pygame.display.flip()

if __name__ == "__main__":
    main()
