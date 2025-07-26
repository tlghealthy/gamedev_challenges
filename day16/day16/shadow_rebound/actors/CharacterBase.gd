extends CharacterBody2D
class_name CharacterBase

signal died
signal bounced(normal)

var speed: float = 200.0
var gravity: float = 1200.0
var damage: int = 10
var is_airborne: bool = false

func _physics_process(dt):
    var vel = velocity
    if not is_on_floor():
        vel.y += gravity * dt
    _update_move_input(dt, vel)
    velocity = vel
    move_and_slide()

func _update_move_input(dt, vel):
    # To be implemented by subclasses (player/AI)
    pass

func take_hit(amount: int, impulse: Vector2 = Vector2.ZERO):
    # For now just emit died if HP reaches 0
    if has_method("apply_damage"):
        if apply_damage(amount):
            _die()
    if impulse != Vector2.ZERO:
        velocity += impulse

func bounce(normal: Vector2):
    velocity = PhysicsUtils.bounce_velocity(velocity, normal)
    emit_signal("bounced", normal)

func _die():
    emit_signal("died")
    queue_free() 