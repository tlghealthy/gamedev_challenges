"""
Platform-fighter demo with procedural arenas and pre-game modifiers.
Refactored to use extensible procedural stage generation scaffolding.
"""

from __future__ import annotations
import json, pathlib, random, sys, pygame
from pygame import Rect, Vector2
from typing import List, Set
from gameday5 import StageData, BaseStageGenerator, DefaultStageGenerator, Stage

# ----------------------------------------------------- load settings
ROOT = pathlib.Path(__file__).parent
S    = json.loads((ROOT / "settings.json").read_text())
COL  = S["colours"]

SCR_W, SCR_H, FPS = S["screen_width"], S["screen_height"], S["fps"]

# ----------------------------------------------------- helpers
def lerp(a, b, t): return a + (b - a) * t
def lerp_col(lo, hi, t): return [round(lerp(lo[i], hi[i], t)) for i in range(3)]

# ----------------------------------------------------- Procedural Stage Generation
class DefaultStageGeneratorImpl(DefaultStageGenerator):
    """
    Implements a segmented main stage with bumps and floating platforms.
    """
    def generate(self) -> StageData:
        g = S["stage_gen"]
        rand = random.randint
        randf = random.random

        # --- Main stage segments ---
        num_segments = rand(1, 4)
        segment_min_w = g.get("main_min_w", 220)
        segment_max_w = g.get("main_max_w", 320)
        segment_h = g.get("main_h", 32)
        segment_y_base = g.get("main_y", SCR_H - 180)
        segment_y_var = g.get("main_y_variance", 32)
        margin_x = g.get("margin_x", 80)
        gap_min = g.get("main_gap_min", 40)
        gap_max = g.get("main_gap_max", 120)

        segments = []
        x = margin_x
        for i in range(num_segments):
            w = rand(segment_min_w, segment_max_w)
            y = segment_y_base + rand(-segment_y_var, segment_y_var)
            if x + w > SCR_W - margin_x:
                w = SCR_W - margin_x - x
            if w < segment_min_w:
                break
            seg = Rect(x, y, w, segment_h)
            segments.append(seg)
            x += w + rand(gap_min, gap_max)
            if x > SCR_W - margin_x:
                break
        if not segments:
            # fallback: one big platform
            main = Rect(margin_x, segment_y_base, SCR_W - 2 * margin_x, segment_h)
            segments = [main]

        # --- Bumps (boxes) on main stage ---
        bumps = []
        bump_min_w = g.get("bump_min_w", 32)
        bump_max_w = g.get("bump_max_w", 64)
        bump_min_h = g.get("bump_min_h", 24)
        bump_max_h = g.get("bump_max_h", 48)
        for seg in segments:
            num_bumps = rand(0, 5)
            for _ in range(num_bumps):
                bw = rand(bump_min_w, min(bump_max_w, seg.width // 2))
                bh = rand(bump_min_h, bump_max_h)
                bx = rand(seg.left, seg.right - bw)
                by = seg.top - bh
                bump_rect = Rect(bx, by, bw, bh)
                # Avoid major overlap with other bumps on this segment
                if not any(bump_rect.colliderect(b) for b in bumps):
                    bumps.append(bump_rect)

        # --- Floating platforms ---
        floats = []
        float_min = g.get("float_min_count", 1)
        float_max = g.get("float_max_count", 4)
        float_min_w = g.get("float_min_w", 80)
        float_max_w = g.get("float_max_w", 180)
        float_h = g.get("float_h", 20)
        float_min_y_above = g.get("float_min_y_above", 80)
        float_max_y_above = g.get("float_max_y_above", 220)
        float_min_gap = g.get("float_min_gap", 32)
        num_floats = rand(float_min, float_max)
        attempts = 0
        while len(floats) < num_floats and attempts < 30:
            attempts += 1
            w = rand(float_min_w, float_max_w)
            seg = random.choice(segments)
            x = rand(seg.left, seg.right - w)
            y = seg.top - rand(float_min_y_above, float_max_y_above)
            float_rect = Rect(x, y, w, float_h)
            # Avoid overlap with other floats
            if not any(float_rect.colliderect(f) for f in floats):
                floats.append(float_rect)

        # --- Combine all platforms ---
        platforms = segments + bumps + floats
        main = segments[0]  # define the first segment as the main for spawn
        platforms.sort(key=lambda r: (r.top, r.left))
        return StageData(platforms, main)

    def _valid_float(self, rect: Rect, platforms: List[Rect], gap: int) -> bool:
        for p in platforms:
            if abs(rect.top - p.top) < 10 and rect.colliderect(p):
                return False
            if rect.top < p.top and rect.right + gap > p.left and rect.left - gap < p.right:
                return False
        return True

# ----------------------------------------------------- Fighter
class Fighter:
    def __init__(self, pos, controls, body_c, face_c, mods: Set[str]):
        self.pos = Vector2(pos)
        self.vel = Vector2()
        self.w = S["player_width"]
        self.h = S["player_height"]
        self.rect = Rect(self.pos, (self.w, self.h))

        self.body_c, self.face_c = body_c, face_c
        self.controls = controls
        self.mods = mods

        self.facing = 1
        self.on_ground = False
        self.prev_jump = False

        self.damage = 0
        self.last_atk = -S["attack_cooldown_ms"]
        self.hitstun_end = 0

        self.jumps_max = 2 if "double_jump" in mods else 1
        self.jumps_left = self.jumps_max

        self.last_dir = 0
        self.last_dir_t = 0
        self.dash_cd_end = 0

    # ------------------------------ input
    def handle_input(self, keys, now):
        if now < self.hitstun_end:
            self.prev_jump = keys[self.controls["jump"]]
            return

        dx = 0
        if keys[self.controls["left"]]:
            dx = -1
        if keys[self.controls["right"]]:
            dx = 1
        if dx:
            self.facing = dx

        # ground / air horizontal
        if self.on_ground:
            self.vel.x = dx * S["move_speed"]
        else:
            target = dx * S["move_speed"]
            self.vel.x += (target - self.vel.x) * S["air_control_factor"]

        # dash (double-tap)
        if "dash" in self.mods and dx and now >= self.dash_cd_end:
            dash_cfg = S["modifiers"]["dash"]
            if dx == self.last_dir and now - self.last_dir_t <= dash_cfg["dash_window_ms"]:
                self.vel.x = dx * dash_cfg["dash_speed"]
                self.dash_cd_end = now + dash_cfg["dash_cooldown_ms"]
            self.last_dir, self.last_dir_t = dx, now

        # jump / double-jump
        jump_now = keys[self.controls["jump"]]
        if jump_now and not self.prev_jump and self.jumps_left:
            self.vel.y = S["jump_velocity"]
            self.on_ground = False
            self.jumps_left -= 1
        self.prev_jump = jump_now

    # ------------------------------ physics
    def physics(self, stage: Stage):
        prev_bottom = self.rect.bottom

        self.vel.x *= S["horizontal_friction"]
        self.vel.y += S["gravity"]
        self.pos += self.vel
        self.rect.topleft = self.pos

        plat = landing_platform(self.rect.centerx, prev_bottom, self.rect.bottom, stage.platforms)
        if plat and self.vel.y >= 0:
            self.rect.bottom = plat.top
            self.pos.y = self.rect.top
            self.vel.y = 0
            self.on_ground = True
            self.jumps_left = self.jumps_max
        else:
            self.on_ground = False

    # ------------------------------ combat
    def attacking(self, now): return now - self.last_atk < S["attack_duration_ms"]
    def try_attack(self, now):
        if now - self.last_atk >= S["attack_cooldown_ms"]:
            self.last_atk = now
    def attack_hitbox(self):
        off = (self.w / 2 + S["attack_range"]) * self.facing
        left = self.rect.centerx + min(0, off)
        return Rect(left, self.rect.top, abs(off), self.h)
    def take_hit(self, dir_, now):
        kb = S["base_knockback"] + self.damage * S["knockback_scaling"]
        self.vel.x += kb * dir_
        self.vel.y = -S["upward_knockback"]
        self.damage += S["attack_damage"]
        self.hitstun_end = now + S["hitstun_ms"]

    # ------------------------------ draw
    def draw(self, surf, font, now):
        x, y = self.rect.topleft
        r = S["face_size"]
        # capsule body
        pygame.draw.rect(surf, self.body_c, (x, y + r, self.w, self.h - 2 * r))
        pygame.draw.circle(surf, self.body_c, (self.rect.centerx, y + r), r)
        pygame.draw.circle(surf, self.body_c, (self.rect.centerx, self.rect.bottom - r), r)
        # eye
        eye = (self.rect.centerx + self.facing * (r // 2), y + r // 2)
        pygame.draw.circle(surf, self.face_c, eye, r // 3)
        # attack flash
        if self.attacking(now):
            pygame.draw.rect(surf, COL["attack_flash"], self.attack_hitbox(), 2)
        # damage UI
        dmg = font.render(f"{self.damage}%", True, COL["text"])
        surf.blit(dmg, dmg.get_rect(center=(self.rect.centerx, y - 28)))
        t = min(self.damage / 200, 1)
        bw, bh = S["damage_bar"]["width"], S["damage_bar"]["height"]
        bar_col = lerp_col(S["damage_bar"]["low"], S["damage_bar"]["high"], t)
        pygame.draw.rect(surf, bar_col, (self.rect.centerx - bw // 2, y - 18, bw * t, bh))
        pygame.draw.rect(surf, COL["text"], (self.rect.centerx - bw // 2, y - 18, bw, bh), 1)

# ----------------------------------------------------- Platform Landing Helper
def landing_platform(x_center: float, prev_bottom: float, new_bottom: float, platforms: List[Rect]) -> Rect | None:
    best = None
    for p in platforms:
        if p.left <= x_center <= p.right and prev_bottom <= p.top <= new_bottom:
            if best is None or p.top < best.top:
                best = p
    return best

# ----------------------------------------------------- HUD & menus
class HUD:
    def __init__(self):
        self.big = pygame.font.SysFont(None, 48)
        self.small = pygame.font.SysFont(None, S["ui_font_size"])
        self.winner = None

    def menu(self, surf, sel1, sel2, cur1, cur2, mods):
        surf.fill(COL["bg"])
        title = self.big.render("Pick a modifier", True, COL["ui_yellow"])
        surf.blit(title, title.get_rect(center=(SCR_W // 2, 80)))

        for i, key in enumerate(mods):
            label = S["modifiers"][key]["label"]
            color = COL["text"]
            if i == cur1:
                color = COL["p1_body"]
            if i == cur2:
                color = COL["p2_body"]

            s = self.small.render(f"{i + 1}. {label}", True, color)
            surf.blit(s, (SCR_W // 2 - 200, 140 + i * 28))

        inst = self.small.render("P1 Q/E   P2 U/O", True, COL["text"])
        surf.blit(inst, inst.get_rect(center=(SCR_W // 2, SCR_H - 40)))

        if sel1:
            msg = f"P1 ✔ {S['modifiers'][sel1]['label']}"
            surf.blit(self.small.render(msg, True, COL["p1_body"]), (40, 40))
        if sel2:
            msg = f"P2 ✔ {S['modifiers'][sel2]['label']}"
            surf.blit(self.small.render(msg, True, COL["p2_body"]), (SCR_W - 280, 40))

    def draw_winner(self, surf):
        if self.winner:
            s = self.big.render(self.winner + "  (any key)", True, COL["text"])
            surf.blit(s, s.get_rect(center=(SCR_W // 2, SCR_H // 3)))

# ----------------------------------------------------- Game
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCR_W, SCR_H))
        pygame.display.set_caption("Platform-Fighter – Procedural")
        self.clock = pygame.time.Clock()
        self.hud = HUD()

        self.state = "select"
        self.mods = list(S["modifiers"].keys())
        self.cur1 = 0
        self.cur2 = 1
        self.pick1 = None
        self.pick2 = None

        self.stage_generator = DefaultStageGeneratorImpl()
        self.stage = self._generate_stage()
        self._spawn_players()

    def _generate_stage(self):
        stage_data = self.stage_generator.generate()
        return Stage(stage_data)

    def _spawn_players(self):
        p = self.stage.main
        self.p1 = Fighter((p.left + 120, p.top - S["player_height"]),
                          dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w, attack=pygame.K_LCTRL),
                          COL["p1_body"], COL["p1_face"],
                          {self.pick1} if self.pick1 else set())

        self.p2 = Fighter((p.right - 120 - S["player_width"], p.top - S["player_height"]),
                          dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP, attack=pygame.K_RCTRL),
                          COL["p2_body"], COL["p2_face"],
                          {self.pick2} if self.pick2 else set())

    # ------------------------------ main loop
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.state == "select":
                    self._handle_select_events(e)
                else:
                    self._handle_play_events(e, now)

            if self.state == "play":
                self._update_play(keys, now)

            self._draw(now)

    # ------------------------------ event handlers
    def _handle_select_events(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if e.key == pygame.K_q:
            self.cur1 = (self.cur1 + 1) % len(self.mods)
        elif e.key == pygame.K_e:
            self.pick1 = self.mods[self.cur1]
        elif e.key == pygame.K_u:
            self.cur2 = (self.cur2 + 1) % len(self.mods)
        elif e.key == pygame.K_o:
            self.pick2 = self.mods[self.cur2]

        if self.pick1 and self.pick2:
            self.state = "play"
            self.stage = self._generate_stage()
            self._spawn_players()

    def _handle_play_events(self, e, now):
        if self.hud.winner and e.type == pygame.KEYDOWN:
            self.__init__()  # restart
            return
        if e.type == pygame.KEYDOWN:
            if e.key == self.p1.controls["attack"]:
                self.p1.try_attack(now)
            if e.key == self.p2.controls["attack"]:
                self.p2.try_attack(now)

    # ------------------------------ gameplay update
    def _update_play(self, keys, now):
        if self.hud.winner:
            return

        for f in (self.p1, self.p2):
            f.handle_input(keys, now)
            f.physics(self.stage)

        if self.p1.attacking(now) and self.p1.attack_hitbox().colliderect(self.p2.rect):
            self.p2.take_hit(self.p1.facing, now)
        if self.p2.attacking(now) and self.p2.attack_hitbox().colliderect(self.p1.rect):
            self.p1.take_hit(self.p2.facing, now)

        if self.p1.rect.top > SCR_H:
            self.hud.winner = "BLUE WINS!"
        elif self.p2.rect.top > SCR_H:
            self.hud.winner = "RED WINS!"

    # ------------------------------ drawing
    def _draw(self, now):
        if self.state == "select":
            self.hud.menu(self.screen, self.pick1, self.pick2, self.cur1, self.cur2, self.mods)
            pygame.display.flip()
            return

        self.screen.fill(COL["bg"])
        for p in self.stage.platforms:
            pygame.draw.rect(self.screen, COL["stage"], p)
        self.p1.draw(self.screen, self.hud.small, now)
        self.p2.draw(self.screen, self.hud.small, now)
        self.hud.draw_winner(self.screen)
        pygame.display.flip()

# ----------------------------------------------------- entry
if __name__ == "__main__":
    Game().run() 