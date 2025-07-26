import pygame
import math
import json
import os
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# -------------------------------------------------------------
#  Verlet Physics Engine for Pygame Games
# -------------------------------------------------------------
#  Features:
#  • Rigid body physics (rectangles, circles, polygons)
#  • Collision detection and response
#  • Static and dynamic objects
#  • Player interaction and controls
#  • Environment constraints and boundaries
#  • Configurable physics properties
# -------------------------------------------------------------

CONFIG_FILE = "physics_config.json"
DEBUG = False

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as fp:
            config = json.load(fp)
            DEBUG = config.get("debug_print", False)
    except Exception:
        pass

def dprint(*args):
    if DEBUG:
        print(*args)

class BodyType(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    KINEMATIC = "kinematic"

class CollisionShape(Enum):
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"

@dataclass
class PhysicsMaterial:
    """Defines physical properties of objects"""
    density: float = 1.0
    friction: float = 0.3
    restitution: float = 0.5  # bounciness
    damping: float = 0.99

class Vector2(pygame.math.Vector2):
    """Extended Vector2 with physics utilities"""
    
    def rotate_around(self, center: 'Vector2', angle: float) -> 'Vector2':
        """Rotate this vector around a center point"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        dx = self.x - center.x
        dy = self.y - center.y
        return Vector2(
            center.x + dx * cos_a - dy * sin_a,
            center.y + dx * sin_a + dy * cos_a
        )

class Node:
    """Mass point with Verlet integration"""
    
    def __init__(self, pos: Tuple[float, float], mass: float = 1.0, locked: bool = False):
        self.pos = Vector2(pos)
        self.prev = self.pos.copy()
        self.mass = mass
        self.locked = locked
        self.force = Vector2(0, 0)
    
    def update(self, dt: float, gravity: Vector2, damping: float = 0.99):
        """Verlet integration step"""
        if self.locked:
            return
        
        velocity = (self.pos - self.prev) * damping
        self.prev = self.pos.copy()
        
        # Apply forces
        acceleration = self.force / self.mass + gravity
        self.pos += velocity + acceleration * dt * dt
        
        # Reset forces
        self.force = Vector2(0, 0)
    
    def apply_force(self, force: Vector2):
        """Apply a force to this node"""
        self.force += force

class Constraint:
    """Base class for physics constraints"""
    
    def satisfy(self):
        """Satisfy this constraint"""
        pass

class DistanceConstraint(Constraint):
    """Distance constraint between two nodes"""
    
    def __init__(self, a: Node, b: Node, rest_length: float, stiffness: float = 1.0):
        self.a = a
        self.b = b
        self.rest_length = rest_length
        self.stiffness = stiffness
    
    def satisfy(self):
        diff = self.a.pos - self.b.pos
        dist = diff.length()
        if dist == 0:
            return
        
        correction = diff * (self.rest_length - dist) / dist * 0.5 * self.stiffness
        if not self.a.locked:
            self.a.pos += correction
        if not self.b.locked:
            self.b.pos -= correction

class AngleConstraint(Constraint):
    """Angle constraint between three nodes"""
    
    def __init__(self, a: Node, b: Node, c: Node, rest_angle: float, stiffness: float = 1.0):
        self.a = a
        self.b = b
        self.c = c
        self.rest_angle = rest_angle
        self.stiffness = stiffness
    
    def satisfy(self):
        # Calculate current angle
        ba = self.a.pos - self.b.pos
        bc = self.c.pos - self.b.pos
        
        if ba.length() == 0 or bc.length() == 0:
            return
        
        current_angle = math.atan2(bc.y, bc.x) - math.atan2(ba.y, ba.x)
        angle_diff = self.rest_angle - current_angle
        
        # Apply correction
        correction = angle_diff * self.stiffness * 0.1
        # This is a simplified angle constraint - in practice you'd want more sophisticated handling

class RigidBody:
    """Rigid body composed of nodes and constraints"""
    
    def __init__(self, body_type: BodyType = BodyType.DYNAMIC, material: PhysicsMaterial = None):
        self.body_type = body_type
        self.material = material or PhysicsMaterial()
        self.nodes: List[Node] = []
        self.constraints: List[Constraint] = []
        self.shape_type: CollisionShape = None
        self.shape_data = {}
        self.velocity = Vector2(0, 0)
        self.angular_velocity = 0.0
        self.rotation = 0.0
        self.active = True
        self.collision_group = 0
        self.collision_mask = 0xFFFFFFFF
    
    def add_node(self, pos: Tuple[float, float], mass: float = 1.0, locked: bool = None):
        """Add a node to this body"""
        if locked is None:
            locked = self.body_type == BodyType.STATIC
        node = Node(pos, mass, locked)
        self.nodes.append(node)
        return node
    
    def add_constraint(self, constraint: Constraint):
        """Add a constraint to this body"""
        self.constraints.append(constraint)
    
    def update(self, dt: float, gravity: Vector2):
        """Update this body's physics"""
        if not self.active or self.body_type == BodyType.STATIC:
            return
        
        # Update nodes
        for node in self.nodes:
            node.update(dt, gravity, self.material.damping)
        
        # Satisfy constraints
        for _ in range(3):  # Multiple iterations for stability
            for constraint in self.constraints:
                constraint.satisfy()
    
    def get_center(self) -> Vector2:
        """Get the center of mass of this body"""
        if not self.nodes:
            return Vector2(0, 0)
        
        center = Vector2(0, 0)
        total_mass = 0
        
        for node in self.nodes:
            center += node.pos * node.mass
            total_mass += node.mass
        
        return center / total_mass if total_mass > 0 else center
    
    def apply_force_at_point(self, force: Vector2, point: Vector2):
        """Apply a force at a specific point on the body"""
        center = self.get_center()
        for node in self.nodes:
            # Simplified force application
            node.apply_force(force / len(self.nodes))
    
    def set_velocity(self, velocity: Vector2):
        """Set the velocity of this body"""
        if self.body_type == BodyType.DYNAMIC:
            center = self.get_center()
            for node in self.nodes:
                node.prev = node.pos - velocity * 0.016  # Approximate for 60 FPS

class CircleBody(RigidBody):
    """Circular rigid body"""
    
    def __init__(self, center: Tuple[float, float], radius: float, **kwargs):
        super().__init__(**kwargs)
        self.shape_type = CollisionShape.CIRCLE
        self.shape_data = {"radius": radius}
        
        # Create nodes around the circle
        num_nodes = max(8, int(radius * 2))
        for i in range(num_nodes):
            angle = (i / num_nodes) * 2 * math.pi
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            self.add_node((x, y))
        
        # Create distance constraints between adjacent nodes
        for i in range(len(self.nodes)):
            j = (i + 1) % len(self.nodes)
            dist = (self.nodes[i].pos - self.nodes[j].pos).length()
            self.add_constraint(DistanceConstraint(self.nodes[i], self.nodes[j], dist, 1.0))

class RectangleBody(RigidBody):
    """Rectangular rigid body"""
    
    def __init__(self, center: Tuple[float, float], width: float, height: float, **kwargs):
        super().__init__(**kwargs)
        self.shape_type = CollisionShape.RECTANGLE
        self.shape_data = {"width": width, "height": height}
        
        # Create nodes at corners
        half_w, half_h = width / 2, height / 2
        corners = [
            (center[0] - half_w, center[1] - half_h),
            (center[0] + half_w, center[1] - half_h),
            (center[0] + half_w, center[1] + half_h),
            (center[0] - half_w, center[1] + half_h)
        ]
        
        for corner in corners:
            self.add_node(corner)
        
        # Create edge constraints
        for i in range(4):
            j = (i + 1) % 4
            dist = (self.nodes[i].pos - self.nodes[j].pos).length()
            self.add_constraint(DistanceConstraint(self.nodes[i], self.nodes[j], dist, 1.0))
        
        # Create diagonal constraints for stability
        dist = (self.nodes[0].pos - self.nodes[2].pos).length()
        self.add_constraint(DistanceConstraint(self.nodes[0], self.nodes[2], dist, 0.8))

class PolygonBody(RigidBody):
    """Polygonal rigid body"""
    
    def __init__(self, vertices: List[Tuple[float, float]], **kwargs):
        super().__init__(**kwargs)
        self.shape_type = CollisionShape.POLYGON
        self.shape_data = {"vertices": vertices}
        
        # Create nodes at vertices
        for vertex in vertices:
            self.add_node(vertex)
        
        # Create edge constraints
        for i in range(len(self.nodes)):
            j = (i + 1) % len(self.nodes)
            dist = (self.nodes[i].pos - self.nodes[j].pos).length()
            self.add_constraint(DistanceConstraint(self.nodes[i], self.nodes[j], dist, 1.0))

class PhysicsWorld:
    """Main physics simulation world"""
    
    def __init__(self, gravity: Vector2 = None, bounds: Tuple[int, int] = None):
        self.gravity = gravity or Vector2(0, 600)
        self.bounds = bounds or (800, 600)
        self.bodies: List[RigidBody] = []
        self.static_bodies: List[RigidBody] = []
        self.dynamic_bodies: List[RigidBody] = []
        self.collision_callbacks: List[Callable] = []
        self.time_step = 1.0 / 60.0
        self.iterations = 3
    
    def add_body(self, body: RigidBody):
        """Add a body to the physics world"""
        self.bodies.append(body)
        if body.body_type == BodyType.STATIC:
            self.static_bodies.append(body)
        else:
            self.dynamic_bodies.append(body)
    
    def remove_body(self, body: RigidBody):
        """Remove a body from the physics world"""
        if body in self.bodies:
            self.bodies.remove(body)
        if body in self.static_bodies:
            self.static_bodies.remove(body)
        if body in self.dynamic_bodies:
            self.dynamic_bodies.remove(body)
    
    def update(self, dt: float):
        """Update the physics simulation"""
        # Update dynamic bodies
        for body in self.dynamic_bodies:
            if body.active:
                body.update(dt, self.gravity)
        
        # Handle collisions
        self.handle_collisions()
        
        # Apply bounds constraints
        self.apply_bounds()
    
    def handle_collisions(self):
        """Handle collision detection and response"""
        # Check dynamic vs dynamic collisions
        for i, body1 in enumerate(self.dynamic_bodies):
            if not body1.active:
                continue
            for body2 in self.dynamic_bodies[i+1:]:
                if not body2.active:
                    continue
                if self.check_collision(body1, body2):
                    self.resolve_collision(body1, body2)
        
        # Check dynamic vs static collisions
        for body1 in self.dynamic_bodies:
            if not body1.active:
                continue
            for body2 in self.static_bodies:
                if not body2.active:
                    continue
                if self.check_collision(body1, body2):
                    self.resolve_collision(body1, body2)
    
    def check_collision(self, body1: RigidBody, body2: RigidBody) -> bool:
        """Check if two bodies are colliding"""
        # Simple AABB check first
        bounds1 = self.get_body_bounds(body1)
        bounds2 = self.get_body_bounds(body2)
        
        if not self.aabb_overlap(bounds1, bounds2):
            return False
        
        # More detailed collision detection based on shape types
        if body1.shape_type == CollisionShape.CIRCLE and body2.shape_type == CollisionShape.CIRCLE:
            return self.circle_circle_collision(body1, body2)
        elif body1.shape_type == CollisionShape.RECTANGLE and body2.shape_type == CollisionShape.RECTANGLE:
            return self.rect_rect_collision(body1, body2)
        # Add more collision types as needed
        
        return True  # Default to collision if shapes are complex
    
    def get_body_bounds(self, body: RigidBody) -> Tuple[float, float, float, float]:
        """Get the bounding box of a body"""
        if not body.nodes:
            return (0, 0, 0, 0)
        
        min_x = min(node.pos.x for node in body.nodes)
        max_x = max(node.pos.x for node in body.nodes)
        min_y = min(node.pos.y for node in body.nodes)
        max_y = max(node.pos.y for node in body.nodes)
        
        return (min_x, min_y, max_x, max_y)
    
    def aabb_overlap(self, bounds1: Tuple[float, float, float, float], 
                    bounds2: Tuple[float, float, float, float]) -> bool:
        """Check if two AABBs overlap"""
        return not (bounds1[2] < bounds2[0] or bounds1[0] > bounds2[2] or
                   bounds1[3] < bounds2[1] or bounds1[1] > bounds2[3])
    
    def circle_circle_collision(self, body1: RigidBody, body2: RigidBody) -> bool:
        """Check collision between two circular bodies"""
        center1 = body1.get_center()
        center2 = body2.get_center()
        radius1 = body1.shape_data["radius"]
        radius2 = body2.shape_data["radius"]
        
        distance = (center1 - center2).length()
        return distance < radius1 + radius2
    
    def rect_rect_collision(self, body1: RigidBody, body2: RigidBody) -> bool:
        """Check collision between two rectangular bodies"""
        # Simplified rectangle collision - in practice you'd want more sophisticated detection
        bounds1 = self.get_body_bounds(body1)
        bounds2 = self.get_body_bounds(body2)
        return self.aabb_overlap(bounds1, bounds2)
    
    def resolve_collision(self, body1: RigidBody, body2: RigidBody):
        """Resolve collision between two bodies"""
        # Simple collision response - push bodies apart
        center1 = body1.get_center()
        center2 = body2.get_center()
        
        if center1 == center2:
            return
        
        direction = (center1 - center2).normalize()
        overlap = 1.0  # Simplified overlap calculation
        
        # Push bodies apart
        if body1.body_type == BodyType.DYNAMIC:
            for node in body1.nodes:
                node.pos += direction * overlap * 0.5
        
        if body2.body_type == BodyType.DYNAMIC:
            for node in body2.nodes:
                node.pos -= direction * overlap * 0.5
        
        # Call collision callbacks
        for callback in self.collision_callbacks:
            callback(body1, body2)
    
    def apply_bounds(self):
        """Apply world boundary constraints"""
        for body in self.dynamic_bodies:
            if not body.active:
                continue
            
            for node in body.nodes:
                node.pos.x = max(0, min(self.bounds[0], node.pos.x))
                node.pos.y = max(0, min(self.bounds[1], node.pos.y))
    
    def add_collision_callback(self, callback: Callable):
        """Add a collision callback function"""
        self.collision_callbacks.append(callback)
    
    def raycast(self, start: Vector2, direction: Vector2, max_distance: float) -> Optional[RigidBody]:
        """Cast a ray and return the first body hit"""
        end = start + direction * max_distance
        
        for body in self.bodies:
            if not body.active:
                continue
            
            # Simple raycast against bounding box
            bounds = self.get_body_bounds(body)
            if self.ray_aabb_intersection(start, end, bounds):
                return body
        
        return None
    
    def ray_aabb_intersection(self, start: Vector2, end: Vector2, 
                            bounds: Tuple[float, float, float, float]) -> bool:
        """Check if a ray intersects with an AABB"""
        # Simplified ray-AABB intersection
        # In practice, you'd want a more robust implementation
        return True  # Placeholder

class PlayerController:
    """Player input and movement controller"""
    
    def __init__(self, body: RigidBody, speed: float = 300.0, jump_force: float = 400.0):
        self.body = body
        self.speed = speed
        self.jump_force = jump_force
        self.on_ground = False
        self.can_jump = True
    
    def handle_input(self, keys, dt: float):
        """Handle player input"""
        if not self.body.active:
            return
        
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.body.set_velocity(Vector2(-self.speed, self.body.velocity.y))
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.body.set_velocity(Vector2(self.speed, self.body.velocity.y))
        else:
            # Apply damping when no input
            self.body.set_velocity(Vector2(self.body.velocity.x * 0.8, self.body.velocity.y))
        
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.can_jump:
            self.body.apply_force_at_point(Vector2(0, -self.jump_force), self.body.get_center())
            self.can_jump = False
    
    def update(self, dt: float):
        """Update player state"""
        # Check if on ground (simplified)
        center = self.body.get_center()
        self.on_ground = center.y > 550  # Assuming ground is at y=550
        
        if self.on_ground:
            self.can_jump = True

# Utility functions for game development

def create_platform(world: PhysicsWorld, x: float, y: float, width: float, height: float):
    """Create a static platform"""
    platform = RectangleBody((x, y), width, height, body_type=BodyType.STATIC)
    world.add_body(platform)
    return platform

def create_player(world: PhysicsWorld, x: float, y: float, size: float = 30.0):
    """Create a player character"""
    player = RectangleBody((x, y), size, size, body_type=BodyType.DYNAMIC)
    player.material.density = 1.0
    player.material.friction = 0.3
    world.add_body(player)
    return player

def create_ball(world: PhysicsWorld, x: float, y: float, radius: float = 15.0):
    """Create a bouncing ball"""
    ball = CircleBody((x, y), radius, body_type=BodyType.DYNAMIC)
    ball.material.restitution = 0.8
    ball.material.friction = 0.1
    world.add_body(ball)
    return ball

def create_rope(world: PhysicsWorld, start_pos: Tuple[float, float], 
               segments: int, segment_length: float, stiffness: float = 0.8):
    """Create a rope with multiple segments"""
    nodes = []
    constraints = []
    
    for i in range(segments):
        pos = (start_pos[0], start_pos[1] + i * segment_length)
        node = Node(pos, locked=(i == 0))
        nodes.append(node)
        
        if i > 0:
            constraint = DistanceConstraint(nodes[i-1], node, segment_length, stiffness)
            constraints.append(constraint)
    
    # Create a custom body for the rope
    rope_body = RigidBody(body_type=BodyType.DYNAMIC)
    rope_body.nodes = nodes
    rope_body.constraints = constraints
    rope_body.shape_type = CollisionShape.POLYGON
    
    world.add_body(rope_body)
    return rope_body 