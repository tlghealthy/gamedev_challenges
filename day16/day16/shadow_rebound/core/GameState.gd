extends Node
class_name GameState

signal level_up(stat_name)
signal style_xp_changed(value)

var max_hp: int = 100
var hp: int = max_hp

var power: int = 0
var defense: int = 0
var technique: int = 0

var style_xp: float = 0.0
var style_target: float = 100.0
var combo_multiplier: float = 1.0

var current_stage: int = 1

func _ready():
    name = "GameState"  # for easy singleton lookup

func add_style(points: float) -> void:
    style_xp += points * combo_multiplier
    emit_signal("style_xp_changed", style_xp)
    if style_xp >= style_target:
        _level_up()

func take_damage(amount: int) -> void:
    hp = clamp(hp - max(amount - defense, 1), 0, max_hp)
    if hp == 0:
        get_tree().call_group("player", "die")

func _level_up() -> void:
    style_xp -= style_target
    style_target *= 1.2  # progressive curve

    var roll = randi() % 3
    var stat_name := ""
    match roll:
        0:
            power += 1
            stat_name = "power"
        1:
            defense += 1
            stat_name = "defense"
        2:
            technique += 1
            stat_name = "technique"
    emit_signal("level_up", stat_name)

func reset_stage_stats():
    power = defense = technique = 0
    combo_multiplier = 1.0
    style_xp = 0.0
    style_target = 100.0 