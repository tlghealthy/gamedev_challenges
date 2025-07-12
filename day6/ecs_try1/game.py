class Game:
    """Main game loop and orchestrator for ECS architecture."""
    def __init__(self, settings, world, renderer, input_system):
        self.settings = settings
        self.world = world
        self.renderer = renderer
        self.input_system = input_system
        self.running = True

    def run(self):
        while self.running:
            self.input_system.process()
            self.world.update()
            self.renderer.render(self.world) 