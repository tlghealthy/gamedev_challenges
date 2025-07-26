extends Node2D

class_name Stage

@export var waves: Array = [] # Array of Array[Dictionary] entries {type:String, position:Vector2}
@onready var spawn_controller := SpawnController.new()
var current_wave: int = -1

func _ready():
    add_child(spawn_controller)
    _spawn_player()
    _define_temp_waves()
    _start_next_wave()
    spawn_controller.all_enemies_defeated.connect(_on_wave_cleared)

func _spawn_player():
    var player_scene = preload("res://actors/Player.gd")
    var player = player_scene.new()
    add_child(player)
    player.global_position = Vector2.ZERO
    player.add_to_group("player")

    # Camera follow
    var cam = Camera2D.new()
    cam.zoom = Vector2(0.5, 0.5)
    player.add_child(cam)
    cam.current = true

func _define_temp_waves():
    # TEMP hard-coded waves until JSON loader exists
    waves = [
        [ {"type": "Thug", "position": Vector2(200,0)} ],
        [ {"type": "Thug", "position": Vector2(250,0)}, {"type": "Thug", "position": Vector2(300,0)} ]
    ]

func _start_next_wave():
    current_wave += 1
    if current_wave >= waves.size():
        _victory()
        return
    spawn_controller.spawn_wave(waves[current_wave])

func _on_wave_cleared():
    _start_next_wave()

func _victory():
    print("Stage cleared!")
    # For now just restart the scene
    get_tree().reload_current_scene()

#------------------------------------------------
class SpawnController := Node:
    signal all_enemies_defeated
    func spawn_wave(entries: Array):
        for entry in entries:
            _spawn_enemy(entry)
    func _spawn_enemy(entry):
        var t := entry.get("type", "Thug")
        var enemy_scene = preload("res://actors/EnemyBase.gd")
        var enemy = enemy_scene.new()
        get_parent().add_child(enemy)
        enemy.global_position = entry.get("position", Vector2.ZERO)
        enemy.died.connect(_check_clear)
    func _check_clear():
        # If no enemies remain, emit signal
        for n in get_parent().get_children():
            if n is EnemyBase:
                return
        emit_signal("all_enemies_defeated") 