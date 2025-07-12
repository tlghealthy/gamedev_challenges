from base_physics import BasePhysicsEngine

class SimpleBody:
    def __init__(self, x, y, w, h, vx=0, vy=0):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.vx, self.vy = vx, vy
        self.fx, self.fy = 0, 0

class SimplePhysicsEngine(BasePhysicsEngine):
    def __init__(self):
        self.bodies = {}
        self._id_counter = 0

    def create_body(self, x, y, w, h, vx=0, vy=0, **kwargs):
        bid = self._id_counter
        self.bodies[bid] = SimpleBody(x, y, w, h, vx, vy)
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
        for b in self.bodies.values():
            b.vx += b.fx * dt
            b.vy += b.fy * dt
            b.x += b.vx * dt
            b.y += b.vy * dt
            b.fx = b.fy = 0

        # Minimal collision: assume body 0 is player, body 1 is ground
        if len(self.bodies) >= 2:
            player = self.bodies[0]
            ground = self.bodies[1]
            if self._aabb_overlap(player, ground):
                # Only handle vertical depenetration (player lands on ground)
                if player.vy > 0:  # Falling down
                    player.y = ground.y - player.h
                    player.vy = 0

    def _aabb_overlap(self, a, b):
        return (a.x < b.x + b.w and a.x + a.w > b.x and
                a.y < b.y + b.h and a.y + a.h > b.y) 