extends Node
class_name AudioBus

var sfx: Dictionary = {}
var bgm: Dictionary = {}

func _ready():
    name = "AudioBus"
    # Load placeholder assets
    _register_sound("punch", "res://assets/placeholder/audio/punch.wav")
    _register_sound("level_up", "res://assets/placeholder/audio/level_up.wav")

func _register_sound(key: String, path: String):
    if FileAccess.file_exists(path):
        sfx[key] = preload(path)

func play_sfx(key: String):
    if not sfx.has(key):
        return
    var p = AudioStreamPlayer.new()
    p.stream = sfx[key]
    add_child(p)
    p.play()
    p.finished.connect(p.queue_free) 