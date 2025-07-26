from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence, Iterable, Tuple, Callable
import math
import pygame

Vec = pygame.Vector2          # swap out for any float‑Vec2 you like
R   = 8                       # increased node radius for better collision detection

@dataclass
class Node:
    pos: Vec
    prev: Vec
    locked: bool = False

    def integrate(self, dt: float, g: Vec, damp: float):
        if self.locked:
            return
        vel  = (self.pos - self.prev) * damp
        self.prev = self.pos.copy()
        self.pos += vel + g * dt * dt

@dataclass
class Edge:
    a: Node
    b: Node
    rest: float
    k: float                     # stiffness 0–1

    def satisfy(self):
        d = self.a.pos - self.b.pos
        dist = d.length() or 1e-8
        corr = d * (self.rest - dist) / dist * .5 * self.k
        if not self.a.locked: self.a.pos += corr
        if not self.b.locked: self.b.pos -= corr


class World:
    def __init__(self,
                 gravity=(0,200),  # Much reduced gravity for stability
                 damping=.998,  # Much increased damping for stability
                 iterations=12,  # Further increased iterations for stability
                 collide_node_edge=True,
                 fixed_dt=1/120.0):  # Fixed timestep for Phase 1
        self.g = Vec(gravity)
        self.damp = damping
        self.iters = iterations
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self._collide = collide_node_edge
        self.fixed_dt = fixed_dt
        self.accumulator = 0.0  # Time accumulator for fixed timestep

    # ---------- public factory helpers ---------- #
    def rope(self, start: Tuple[float,float], seg_len: float,
             count: int, k=.8) -> Sequence[Node]:
        ns = [self._node((start[0] + i*seg_len, start[1]), locked=(i==0))
              for i in range(count)]
        for i in range(1,count):
            self._edge(ns[i-1], ns[i], k)
        return ns

    def box(self, pos, w, h, k=.95) -> Sequence[Node]:  # Increased stiffness for stability
        x,y = pos
        n00,n10,n11,n01 = (self._node((x,y)),      self._node((x+w,y)),
                           self._node((x+w,y+h)),  self._node((x,  y+h)))
        for a,b in ((n00,n10),(n10,n11),(n11,n01),(n01,n00),(n00,n11),(n10,n01)):
            self._edge(a,b,k)
        return (n00,n10,n11,n01)

    def capsule(self, p0, p1, radius, segs=6, k=.9):
        # quick poly‑rope approximation; good enough for casual collision
        axis = Vec(p1) - p0
        step = axis / (segs-1)
        ns = [self._node(Vec(p0)+step*i) for i in range(segs)]
        for i in range(1,segs):
            self._edge(ns[i-1], ns[i], k)
        return ns

    # ---------- simulation with fixed timestep ---------- #
    def step(self, dt: float):
        # Fixed timestep accumulator for Phase 1
        self.accumulator += dt
        
        # Run fixed timestep steps
        while self.accumulator >= self.fixed_dt:
            self._step_fixed(self.fixed_dt)
            self.accumulator -= self.fixed_dt
    
    def _step_fixed(self, dt: float):
        # Integration step
        for n in self.nodes:
            n.integrate(dt, self.g, self.damp)
        
        # Constraint solving
        for _ in range(self.iters):
            for e in self.edges: 
                e.satisfy()
            if self._collide: 
                self._solve_collisions()
            self._solve_ground_constraint()  # Add ground constraint

    # ---------- optional ---------- #
    def debug_render(self, surf, color_nodes=(230,230,230),
                     color_edges=(230,230,230)):
        draw = pygame.draw
        for e in self.edges:
            draw.line(surf, color_edges, e.a.pos, e.b.pos, 2)
        for n in self.nodes:
            c = (255,80,80) if n.locked else color_nodes
            draw.circle(surf, c, (int(n.pos.x),int(n.pos.y)), R)

    # ---------- internals ---------- #
    def _node(self, pos, locked=False):
        n = Node(Vec(pos), Vec(pos), locked)
        self.nodes.append(n);  return n

    def _edge(self, a,b,k): 
        self.edges.append(Edge(a,b,(a.pos-b.pos).length(), k))

    def _solve_collisions(self):
        rad2 = R*R
        for n in self.nodes:
            for e in self.edges:
                if n in (e.a,e.b): continue
                ab = e.b.pos - e.a.pos
                t  = max(0,min(1,(n.pos-e.a.pos).dot(ab)/(ab.length_squared()+1e-8)))
                p  = e.a.pos + ab*t       # closest point on edge
                d  = n.pos - p
                ds2 = d.length_squared()
                if 1e-12 < ds2 < rad2:
                    dist = math.sqrt(ds2)
                    push = (R - dist) * 0.6  # Further reduced push factor
                    n_corr = d / dist * push
                    if not n.locked: n.pos += n_corr
                    if not e.a.locked: e.a.pos -= n_corr*.5
                    if not e.b.locked: e.b.pos -= n_corr*.5
        
        # Additional node-node collision detection for better stability
        for i, n1 in enumerate(self.nodes):
            for n2 in self.nodes[i+1:]:
                d = n1.pos - n2.pos
                ds2 = d.length_squared()
                if 1e-12 < ds2 < rad2:
                    dist = math.sqrt(ds2)
                    push = (R - dist) * 0.5
                    n_corr = d / dist * push
                    if not n1.locked: n1.pos += n_corr * 0.5
                    if not n2.locked: n2.pos -= n_corr * 0.5

    def _solve_ground_constraint(self):
        """Prevent nodes from going outside window boundaries"""
        # Window boundaries (assuming 800x600 window)
        # Use a larger boundary to account for box sizes
        left = 40  # Account for box width
        right = 800 - 40
        top = 40   # Account for box height
        bottom = 600 - 80  # Account for full box height
        
        for n in self.nodes:
            if n.locked:
                continue
                
            # Clamp position to window boundaries
            if n.pos.x < left:
                n.pos.x = left
                if n.prev.x < left:
                    n.prev.x = left
            elif n.pos.x > right:
                n.pos.x = right
                if n.prev.x > right:
                    n.prev.x = right
                    
            if n.pos.y < top:
                n.pos.y = top
                if n.prev.y < top:
                    n.prev.y = top
            elif n.pos.y > bottom:
                n.pos.y = bottom
                if n.prev.y > bottom:
                    n.prev.y = bottom


if __name__ == "__main__":
    import sys
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock  = pygame.time.Clock()

    world = World()
    world.rope((150,120), seg_len=40, count=12)
    for r in range(3):
        for c in range(3):
            world.box((350+c*120, 120+r*120), 80, 80)

    drag = None
    while True:
        dt = clock.tick(60)/1000
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                m = pygame.Vector2(e.pos)
                drag = min(world.nodes, key=lambda n:(n.pos-m).length_squared())
                if (drag.pos-m).length_squared() > R*R: drag=None
            elif e.type==pygame.MOUSEBUTTONUP and e.button==1:
                drag=None

        if drag:
            drag.prev = drag.pos.copy()
            drag.pos.update(*pygame.mouse.get_pos())

        world.step(dt)

        screen.fill((30,30,30))
        world.debug_render(screen)
        pygame.display.flip() 