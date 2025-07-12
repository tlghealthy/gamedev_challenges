# physics.py
import math, json, pathlib, pygame, pymunk
import pymunk.pygame_util as pm_draw

CONFIG_PATH = pathlib.Path("systemconfig.json")  # optional user toggle


class Physics:
    """
    Thin convenience wrapper around a Pymunk Space tuned for 2-D platform fighters.

    Highlights
    ----------
    ▸ Fixed-dt stepping with internal accumulator (default: 1/120 s)
    ▸ Pixel-perfect interpolation helper for butter-smooth cameras/sprites
    ▸ One-liners to add players, kinematic platforms, sensors, projectiles
    ▸ Simple collision-type registry (int->str tag) + handler binding
    ▸ Optional debug rendering via space.debug_draw(...)
    """

    # “enum” of collision types you can extend as you like
    CT = {
        "PLAYER":     1,
        "FLOOR":      2,
        "ATTACKBOX":  3,
        "HURTBOX":    4,
        "PROJECTILE": 5,
        "SENSOR":     6,
    }

    def __init__(self,
                 ppm: int = 1,              # pixels-per-meter (keep 1:1 for Pygame coords)
                 gravity=(0, 900),
                 fixed_dt: float = 1/120,
                 debug: bool | None = None):

        # allow a global debug toggle in systemconfig.json → { "physics_debug": true }
        if debug is None:
            debug = json.loads(CONFIG_PATH.read_text())["physics_debug"] \
                         if CONFIG_PATH.exists() else False
        self.debug = debug
        self.ppm = ppm
        self.dt = fixed_dt
        self._accum = 0.0

        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.iterations = 10
        # Tweak for sticky footing
        self.space.collision_slop = 0.01
        self.space.collision_bias = 0.2

        self._draw_opts = None       # lazily built the first time you call debug_draw
        self._bodies_last = {}       # body → last_pos for interpolation

    # ---------------------------------------------------------------------
    # Creation helpers
    # ---------------------------------------------------------------------
    def add_player(self, pos_px, size_px=(48, 72), mass=1.0, friction=0.8):
        moment = pymunk.moment_for_box(mass, size_px)
        body   = pymunk.Body(mass, moment)
        body.position = pos_px
        shape  = pymunk.Poly.create_box(body, size_px, radius=1)
        shape.friction = friction
        shape.collision_type = self.CT["PLAYER"]
        self.space.add(body, shape)

        # foot sensor for coyote-time tests (slightly inset)
        w, h = size_px
        sensor = pymunk.Poly(body, [
            (-w*0.4,  h*0.5),
            ( w*0.4,  h*0.5),
            ( w*0.4,  h*0.55),
            (-w*0.4,  h*0.55),
        ])
        sensor.sensor = True
        sensor.collision_type = self.CT["SENSOR"]
        self.space.add(sensor)

        self._log(f"player added @ {pos_px}")
        return body, shape, sensor

    def add_platform(self, start_px, end_px, thickness=4, kinematic=False, vel_px_s=(0, 0)):
        if kinematic:
            body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            body.velocity = vel_px_s       # drive it every step if you want motion
            self.space.add(body)           # <-- add the body first
        else:
            body = self.space.static_body  # already in the space

        shape = pymunk.Segment(body, start_px, end_px, thickness)
        shape.friction        = 1.0
        shape.collision_type  = self.CT["FLOOR"]
        shape.surface_velocity = vel_px_s if not kinematic else (0, 0)
        self.space.add(shape)              # now it’s safe
        return body, shape                 # return both for convenience

    def add_projectile(self, pos_px, vel_px_s, radius=6, mass=0.1,
                       restitution=0.2):
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body   = pymunk.Body(mass, moment)
        body.position = pos_px
        body.velocity = vel_px_s
        shape = pymunk.Circle(body, radius)
        shape.elasticity = restitution
        shape.collision_type = self.CT["PROJECTILE"]
        self.space.add(body, shape)
        return body, shape

    def add_sensor_rect(self, pos_px, size_px, collision_tag: str):
        body = self.space.static_body
        w, h = size_px
        verts = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
        shape = pymunk.Poly(body, verts, offset=pos_px)
        shape.sensor = True
        shape.collision_type = self.CT[collision_tag]
        self.space.add(shape)
        return shape

    # ---------------------------------------------------------------------
    # Collision helpers
    # ---------------------------------------------------------------------
    def on(self, a_tag: str, b_tag: str,
           begin=None, pre=None, post=None, separate=None):
        """Register collision callbacks quickly by tag name."""
        h = self.space.add_collision_handler(self.CT[a_tag], self.CT[b_tag])
        h.begin     = begin
        h.pre_solve = pre
        h.post_solve= post
        h.separate  = separate
        self._log(f"handler {a_tag} ↔ {b_tag} registered")
        return h

    # ---------------------------------------------------------------------
    # Simulation update
    # ---------------------------------------------------------------------
    def step(self, real_dt_s: float):
        """Call from your game loop with *render* delta-time."""
        self._accum += real_dt_s
        while self._accum >= self.dt:
            # save last positions for interpolation
            for b in self.space.bodies:
                self._bodies_last[b] = b.position
            self.space.step(self.dt)
            self._accum -= self.dt

    # ---------------------------------------------------------------------
    # Rendering helpers
    # ---------------------------------------------------------------------
    def debug_draw(self, surface: pygame.Surface):
        if not self._draw_opts:
            self._draw_opts = pm_draw.DrawOptions(surface)
        self.space.debug_draw(self._draw_opts)

    def interp_pos(self, body: pymunk.Body) -> pymunk.Vec2d:
        """Interpolated world position to render **this frame**."""
        alpha = self._accum / self.dt
        prev = self._bodies_last.get(body, body.position)
        return body.position * (1 - alpha) + prev * alpha

    # ---------------------------------------------------------------------
    # Internal
    # ---------------------------------------------------------------------
    def _log(self, msg: str):
        if self.debug:
            print(f"[Physics] {msg}")
