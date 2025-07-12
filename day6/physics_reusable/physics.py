# physics.py
import itertools

class Body:
    def __init__(self, x, y, w, h, vx=0, vy=0, static=False, dampening=1.0):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.vx, self.vy = vx, vy
        self.fx, self.fy = 0, 0
        self.static = static
        self.dampening = dampening

    @property
    def pos(self):
        return self.x, self.y

    @property
    def size(self):
        return self.w, self.h

class Engine:
    def __init__(self):
        self.bodies = {}
        self._id_counter = 0

    def create_body(self, x, y, w, h, vx=0, vy=0, static=False, dampening=1.0):
        bid = self._id_counter
        self.bodies[bid] = Body(x, y, w, h, vx, vy, static, dampening)
        self._id_counter += 1
        return bid

    def remove_body(self, bid):
        self.bodies.pop(bid, None)

    def get_body(self, bid):
        return self.bodies[bid]

    def apply_force(self, bid, fx, fy):
        b = self.get_body(bid)
        b.fx += fx
        b.fy += fy

    def update(self, dt):
        # Apply forces and integrate
        for b in self.bodies.values():
            if not b.static:
                b.vx += b.fx * dt
                b.vy += b.fy * dt
                b.x += b.vx * dt
                b.y += b.vy * dt
            b.fx = b.fy = 0

        # Depenetration (naive n^2, ok for <50 bodies)
        pairs = list(itertools.combinations(self.bodies.values(), 2))
        for a, b in pairs:
            if self._aabb_overlap(a, b):
                self._depenetrate(a, b)
                # --- Simple friction: apply average dampening if at least one is not static ---
                if not (a.static and b.static):
                    avg_damp = (a.dampening + b.dampening) / 2
                    if not a.static:
                        a.vx *= avg_damp
                        a.vy *= avg_damp
                    if not b.static:
                        b.vx *= avg_damp
                        b.vy *= avg_damp

    def _aabb_overlap(self, a, b):
        return (a.x < b.x + b.w and a.x + a.w > b.x and
                a.y < b.y + b.h and a.y + a.h > b.y)

    def _depenetrate(self, a, b):
        # Minimum translation vector
        dx = (a.x + a.w/2) - (b.x + b.w/2)
        dy = (a.y + a.h/2) - (b.y + b.h/2)
        overlap_x = (a.w + b.w)/2 - abs(dx)
        overlap_y = (a.h + b.h)/2 - abs(dy)
        if overlap_x < overlap_y:
            shift = overlap_x / 2
            if dx > 0:
                if not a.static and not b.static:
                    a.x += shift
                    b.x -= shift
                elif not a.static:
                    a.x += shift * 2
                elif not b.static:
                    b.x -= shift * 2
            else:
                if not a.static and not b.static:
                    a.x -= shift
                    b.x += shift
                elif not a.static:
                    a.x -= shift * 2
                elif not b.static:
                    b.x += shift * 2
        else:
            shift = overlap_y / 2
            if dy > 0:
                if not a.static and not b.static:
                    a.y += shift
                    b.y -= shift
                elif not a.static:
                    a.y += shift * 2
                elif not b.static:
                    b.y -= shift * 2
            else:
                if not a.static and not b.static:
                    a.y -= shift
                    b.y += shift
                elif not a.static:
                    a.y -= shift * 2
                elif not b.static:
                    b.y += shift * 2
