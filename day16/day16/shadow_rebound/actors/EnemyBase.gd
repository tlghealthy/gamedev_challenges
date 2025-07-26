extends "res://actors/CharacterBase.gd"

enum AIState { IDLE, APPROACH, ATTACK }
var state: int = AIState.IDLE
var target: Node = null

func _ready():
    target = get_tree().get_first_node_in_group("player")
    state = AIState.APPROACH

func _update_move_input(dt, vel):
    if not target:
        return
    var dir = (target.global_position - global_position).normalized()
    vel.x = dir.x * speed 