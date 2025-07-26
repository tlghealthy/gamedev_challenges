extends Node

func _ready():
    # Ensure global singletons are present when running directly from this scene
    if not get_node_or_null("/root/GameState"):
        var game_state = preload("res://core/GameState.gd").new()
        get_tree().root.add_child(game_state)
        get_tree().set_auto_accept_quit(false)
    if not get_node_or_null("/root/ObjectPool"):
        var pool = preload("res://core/ObjectPool.gd").new()
        get_tree().root.add_child(pool)
    if not get_node_or_null("/root/AudioBus"):
        var audio = preload("res://core/AudioBus.gd").new()
        get_tree().root.add_child(audio)

    # Load Stage 1 instead of directly spawning player
    var stage_scene = preload("res://levels/Stage.gd")
    var stage = stage_scene.new()
    add_child(stage)

    # Add HUD overlay
    var hud = preload("res://ui/HUD.gd").new()
    add_child(hud) 