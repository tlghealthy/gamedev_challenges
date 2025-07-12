from component import Component
import pygame

class Position(Component):
    """Component for entity position."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Velocity(Component):
    """Component for entity velocity."""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Player(Component):
    """Component for player-specific data."""
    def __init__(self, player_id, controls, color, face_left=False):
        self.player_id = player_id
        self.controls = controls
        self.color = color
        self.face_left = face_left
        self.facing = -1 if face_left else 1
        self.on_ground = False
        self.damage = 0
        self.attack_cooldown = 0
        self.attacking = False
        self.last_attack_time = 0

class Physics(Component):
    """Component for physics body reference."""
    def __init__(self, body, shape, foot_sensor=None):
        self.body = body
        self.shape = shape
        self.foot_sensor = foot_sensor

class Renderable(Component):
    """Component for rendering data."""
    def __init__(self, width, height, color, shape_type="rect"):
        self.width = width
        self.height = height
        self.color = color
        self.shape_type = shape_type

class Attack(Component):
    """Component for attack data."""
    def __init__(self, cooldown, damage, knockback_base, knockback_scalar):
        self.cooldown = cooldown
        self.damage = damage
        self.knockback_base = knockback_base
        self.knockback_scalar = knockback_scalar
        self.current_cooldown = 0
        self.attacking = False
        self.attack_duration = 0.05  # How long attack hitbox is visible

class Stage(Component):
    """Component for stage/platform data."""
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color 