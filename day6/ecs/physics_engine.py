import pymunk
import pymunk.pygame_util

class PhysicsEngine:
    """Wrapper for pymunk physics engine."""
    def __init__(self, gravity=(0, 981), surface=None):
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.surface = surface
        if surface:
            self.draw_options = pymunk.pygame_util.DrawOptions(surface)
        else:
            self.draw_options = None
        
        # Collision handlers
        self._setup_collision_handlers()

    def _setup_collision_handlers(self):
        """Setup collision handlers for ground detection."""
        def begin_sensor(arbiter, space, data):
            # This will be set up when we create players
            return True

        def separate_sensor(arbiter, space, data):
            # This will be set up when we create players
            return True

        # We'll add specific handlers when creating entities

    def add_player(self, pos, size_px, mass=2, friction=0.8):
        """Create a player physics body."""
        width, height = size_px
        
        # Create body
        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = pos
        
        # Create shape
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = friction
        shape.collision_type = 1  # Player collision type
        
        # Create foot sensor for ground detection
        foot_sensor = pymunk.Segment(body, (0, height//2), (0, height//2 + 5), 2)
        foot_sensor.sensor = True
        foot_sensor.collision_type = 2  # Sensor collision type
        
        # Add to space
        self.space.add(body, shape, foot_sensor)
        
        return body, shape, foot_sensor

    def add_platform(self, start_px, end_px, thickness=40):
        """Create a platform physics body."""
        # Create static body
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        
        # Create shape
        shape = pymunk.Segment(body, start_px, end_px, thickness)
        shape.friction = 0.8
        shape.collision_type = 3  # Platform collision type
        
        # Add to space
        self.space.add(body, shape)
        
        return body, shape

    def step(self, dt):
        """Step the physics simulation."""
        self.space.step(dt)

    def add_collision_handler(self, collision_type_a, collision_type_b, begin=None, separate=None):
        """Add a collision handler between two collision types."""
        # Use the correct pymunk API
        handler = self.space.add_collision_handler(collision_type_a, collision_type_b)
        
        if begin:
            handler.begin = begin
        if separate:
            handler.separate = separate
        return handler 