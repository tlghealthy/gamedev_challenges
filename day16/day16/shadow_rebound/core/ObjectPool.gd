extends Node
class_name ObjectPool

var pools: Dictionary = {}

func _ready():
    name = "ObjectPool"

func preload_scene(id: String, path: String) -> void:
    pools[id] = {
        "scene": preload(path),
        "free": []
    }

func instance(id: String) -> Node:
    if not pools.has(id):
        push_error("Pool for %s not preloaded" % id)
        return null
    var entry = pools[id]
    var node: Node = entry["free"].pop_back() if entry["free"].size() > 0 else entry["scene"].instance()
    return node

func recycle(node: Node) -> void:
    var id = node.get_meta("pool_id") if node.has_meta("pool_id") else null
    if id and pools.has(id):
        pools[id]["free"].push_back(node)
        if node.get_parent():
            node.get_parent().remove_child(node)
    else:
        node.queue_free() 