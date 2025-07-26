import pygame
import sys
import os
import json
import math

# -------------------------------------------------------------
#  Simple Position‑Based Dynamics (Verlet) rope demo in Pygame
# -------------------------------------------------------------
#  • Drag a node with the left mouse button
#  • Right‑click a node to lock/unlock it in place
#  • Use ↑ / ↓ arrows to increase / decrease edge stiffness
#  • Toggle debug prints via systemconfig.json { "debug_print": true }
# -------------------------------------------------------------

CONFIG_FILE = "systemconfig.json"
DEBUG = False
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as fp:
            DEBUG = json.load(fp).get("debug_print", False)
    except Exception:
        pass


def dprint(*args):
    if DEBUG:
        print(*args)


# ---------- Simulation constants ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
BG = (30, 30, 30)
WHITE = (230, 230, 230)
GRAVITY = pygame.math.Vector2(0, 600)  # px/s²
DAMPING = 0.99
CONSTRAINT_ITERATIONS = 5


class Node:
    """Mass‑point integrated with Verlet position update."""

    def __init__(self, pos, locked=False):
        self.pos = pygame.math.Vector2(pos)
        self.prev = self.pos.copy()
        self.locked = locked

    def update(self, dt):
        """Verlet integration step."""
        if self.locked:
            return
        velocity = (self.pos - self.prev) * DAMPING
        self.prev = self.pos.copy()
        self.pos += velocity + GRAVITY * dt * dt

    def clamp_to_bounds(self):
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))


class Edge:
    """Distance constraint between two Nodes."""

    def __init__(self, a: Node, b: Node, stiffness: float = 1.0):
        self.a = a
        self.b = b
        self.rest = (a.pos - b.pos).length()
        self.stiffness = stiffness  # 0 → jelly  …  1 → rigid

    def satisfy(self):
        diff = self.a.pos - self.b.pos
        dist = diff.length()
        if dist == 0:
            return
        correction = diff * (self.rest - dist) / dist * 0.5 * self.stiffness
        if not self.a.locked:
            self.a.pos += correction
        if not self.b.locked:
            self.b.pos -= correction


# ---------- Helper to build a simple rope ----------

def build_rope(start_pos, seg_len, count):
    nodes = []
    edges = []
    for i in range(count):
        nodes.append(Node((start_pos[0] + i * seg_len, start_pos[1]), locked=(i == 0)))
        if i:
            edges.append(Edge(nodes[i - 1], nodes[i], stiffness=0.8))
    return nodes, edges


# ---------- Main loop ----------

def main():
    dprint("Debug logging enabled")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    nodes, edges = build_rope((200, 120), 40, 12)
    dragging = None

    font = pygame.font.SysFont(None, 24)

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left‑click drag
                    mx, my = event.pos
                    dragging = min(nodes, key=lambda n: (n.pos.x - mx) ** 2 + (n.pos.y - my) ** 2)
                    if (dragging.pos - pygame.Vector2(mx, my)).length() > 20:
                        dragging = None
                elif event.button == 3:  # right‑click toggle lock
                    mx, my = event.pos
                    target = min(nodes, key=lambda n: (n.pos.x - mx) ** 2 + (n.pos.y - my) ** 2)
                    if (target.pos - pygame.Vector2(mx, my)).length() < 20:
                        target.locked = not target.locked
                        dprint("Toggled lock for node", nodes.index(target), "→", target.locked)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    for e in edges:
                        e.stiffness = min(1.0, e.stiffness + 0.1)
                    dprint("Stiffness →", f"{edges[0].stiffness:.2f}")
                elif event.key == pygame.K_DOWN:
                    for e in edges:
                        e.stiffness = max(0.1, e.stiffness - 0.1)
                    dprint("Stiffness →", f"{edges[0].stiffness:.2f}")

        if dragging:
            dragging.prev = dragging.pos.copy()
            dragging.pos.update(*pygame.mouse.get_pos())

        # Integration & constraint solving
        for n in nodes:
            n.update(dt)
            n.clamp_to_bounds()

        for _ in range(CONSTRAINT_ITERATIONS):
            for e in edges:
                e.satisfy()

        # ---------- Rendering ----------
        screen.fill(BG)
        for e in edges:
            pygame.draw.line(screen, WHITE, e.a.pos, e.b.pos, 2)
        for n in nodes:
            color = (255, 80, 80) if n.locked else WHITE
            pygame.draw.circle(screen, color, (round(n.pos.x), round(n.pos.y)), 6)

        txt = font.render(
            f"Stiffness: {edges[0].stiffness:.2f}  (↑ / ↓ to change)", True, WHITE
        )
        screen.blit(txt, (10, 10))
        pygame.display.flip()


if __name__ == "__main__":
    main()
