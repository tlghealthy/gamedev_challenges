class Entity:
    """A game object composed of components."""
    def __init__(self):
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    def get_component(self, component_type):
        return self.components.get(component_type) 