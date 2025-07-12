import pygame
import sys
from settings import Settings
from world import World
from systems import InputSystem, PhysicsSystem, AttackSystem, RenderSystem
from components import Physics, Player
from physics_engine import PhysicsEngine
from entity_factory import EntityFactory

class Game:
    """Main game loop and orchestrator for ECS architecture."""
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Load settings
        self.settings = Settings("settings.json")
        
        # Create screen
        self.screen = pygame.display.set_mode((self.settings.WIDTH, self.settings.HEIGHT))
        pygame.display.set_caption("ECS Fighting Platformer")
        
        # Create physics engine
        gravity = (0, self.settings.GRAVITY * 60 * 60)
        self.physics_engine = PhysicsEngine(gravity=gravity, surface=self.screen)
        
        # Create world and systems
        self.world = World()
        self.input_system = InputSystem(self.settings)
        self.physics_system = PhysicsSystem(self.physics_engine.space)
        self.attack_system = AttackSystem(self.settings)
        self.render_system = RenderSystem(self.screen, self.settings)
        
        # Add systems to world
        self.world.add_system(self.input_system)
        self.world.add_system(self.physics_system)
        self.world.add_system(self.attack_system)
        self.world.add_system(self.render_system)
        
        # Create entity factory
        self.entity_factory = EntityFactory(self.physics_engine, self.settings)
        
        # Create game entities
        self._create_entities()
        
        # Setup collision handlers
        self._setup_collision_handlers()
        
        # Game state
        self.running = True
        self.winner = None
        self.clock = pygame.time.Clock()

    def _create_entities(self):
        """Create all game entities."""
        # Create stage
        stage_pos = (self.settings.WIDTH // 2, 500)
        stage = self.entity_factory.create_stage(stage_pos, 800, 40)
        self.world.add_entity(stage)
        
        # Create players
        w = self.settings.WIDTH
        platform_y = stage_pos[1] - 20  # Stage top
        y = platform_y - 45  # Player bottom aligned with stage top
        
        p1_controls = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "attack": pygame.K_LCTRL
        }
        p2_controls = {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "attack": pygame.K_RCTRL
        }
        
        p1 = self.entity_factory.create_player(
            1, (w // 2 - 150, y), p1_controls, self.settings.P1_COLOR, face_left=False
        )
        p2 = self.entity_factory.create_player(
            2, (w // 2 + 150, y), p2_controls, self.settings.P2_COLOR, face_left=True
        )
        
        self.world.add_entity(p1)
        self.world.add_entity(p2)
        
        # Store player references for win condition
        self.players = [p1, p2]

    def _setup_collision_handlers(self):
        """Setup collision handlers for ground detection."""
        def begin_sensor(arbiter, space, data):
            # Check if this is a foot sensor hitting a platform
            if (arbiter.shapes[0].collision_type == 2 and 
                arbiter.shapes[1].collision_type == 3):
                # Find the player with this foot sensor
                for entity in self.world.entities:
                    physics = entity.get_component(Physics)
                    player = entity.get_component(Player)
                    if (physics and physics.foot_sensor == arbiter.shapes[0] and player):
                        player.on_ground = True
                        break
            return True

        def separate_sensor(arbiter, space, data):
            # Check if this is a foot sensor leaving a platform
            if (arbiter.shapes[0].collision_type == 2 and 
                arbiter.shapes[1].collision_type == 3):
                # Find the player with this foot sensor
                for entity in self.world.entities:
                    physics = entity.get_component(Physics)
                    player = entity.get_component(Player)
                    if (physics and physics.foot_sensor == arbiter.shapes[0] and player):
                        player.on_ground = False
                        break
            return True

        # Add collision handler between sensors and platforms
        self.physics_engine.add_collision_handler(2, 3, begin=begin_sensor, separate=separate_sensor)

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            self._handle_events()
            
            # Update game if no winner
            if not self.winner:
                self.world.update()
                self._check_win_condition()
            else:
                # Still render the game state
                self.render_system.update(self.world.entities)
                self._draw_winner()
        
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.winner and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self._reset_game()

    def _check_win_condition(self):
        """Check if a player has fallen off the stage."""
        for i, player_entity in enumerate(self.players):
            physics = player_entity.get_component(Physics)
            if physics and physics.body.position.y > self.settings.HEIGHT:
                self.winner = 2 if i == 0 else 1

    def _draw_winner(self):
        """Draw the winner announcement."""
        font = pygame.font.SysFont(None, 72)
        text = f"PLAYER {self.winner} WINS – press R to restart"
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT // 2))
        self.screen.blit(surf, rect)
        pygame.display.flip()

    def _reset_game(self):
        """Reset the game state."""
        # Clear all entities
        self.world.entities.clear()
        
        # Recreate entities
        self._create_entities()
        
        # Reset winner
        self.winner = None 