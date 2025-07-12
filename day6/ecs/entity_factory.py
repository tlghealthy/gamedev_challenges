from entity import Entity
from components import Position, Velocity, Player, Physics, Renderable, Attack, Stage
from physics_engine import PhysicsEngine

class EntityFactory:
    """Factory for creating game entities."""
    def __init__(self, physics_engine, settings):
        self.physics_engine = physics_engine
        self.settings = settings

    def create_player(self, player_id, pos, controls, color, face_left=False):
        """Create a player entity with all necessary components."""
        entity = Entity()
        
        # Add components
        entity.add_component(Position(pos[0], pos[1]))
        entity.add_component(Velocity())
        entity.add_component(Player(player_id, controls, color, face_left))
        entity.add_component(Renderable(50, 90, color))
        entity.add_component(Attack(
            self.settings.ATTACK_COOLDOWN,
            self.settings.DAMAGE_PER_HIT,
            self.settings.BASE_KB,
            self.settings.KB_SCALAR
        ))
        
        # Create physics body
        body, shape, foot_sensor = self.physics_engine.add_player(
            pos, (50, 90), mass=2, friction=0.8
        )
        entity.add_component(Physics(body, shape, foot_sensor))
        
        return entity

    def create_stage(self, pos, width, height):
        """Create a stage entity."""
        entity = Entity()
        
        # Add components
        entity.add_component(Position(pos[0], pos[1]))
        entity.add_component(Stage(width, height, self.settings.STAGE_COLOR))
        
        # Create physics body
        start_px = (pos[0] - width//2, pos[1])
        end_px = (pos[0] + width//2, pos[1])
        body, shape = self.physics_engine.add_platform(start_px, end_px, thickness=height)
        entity.add_component(Physics(body, shape))
        
        return entity 