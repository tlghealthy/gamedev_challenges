class_name PhysicsUtils

static func bounce_velocity(original: Vector2, normal: Vector2) -> Vector2:
    return original.bounce(normal) 