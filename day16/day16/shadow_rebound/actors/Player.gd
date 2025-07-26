extends "res://actors/CharacterBase.gd"

@onready var game_state: GameState = get_node("/root/GameState")

var hop_force: float = 350.0

func _update_move_input(dt, vel):
    var dir = Vector2.ZERO
    dir.x = Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left")
    dir.y = 0
    vel.x = dir.x * speed

    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        vel.y = -hop_force
    if Input.is_action_just_pressed("attack_light"):
        _attack_light()
    if Input.is_action_just_pressed("attack_heavy"):
        _attack_heavy()

func _attack_light():
    game_state.add_style(10)
    get_node("/root/AudioBus").play_sfx("punch")

func _attack_heavy():
    game_state.add_style(20)
    get_node("/root/AudioBus").play_sfx("punch")

func apply_level_up(stat: String):
    match stat:
        "power":
            damage += 2
        "defense":
            # no HP yet - placeholder
            pass
        "technique":
            speed += 20 