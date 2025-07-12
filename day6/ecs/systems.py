from system import System
from components import Player, Physics, Position, Renderable, Attack, Stage
import pygame
import pymunk

class InputSystem(System):
    """Handles player input and movement."""
    def __init__(self, settings):
        self.settings = settings

    def update(self, entities):
        keys = pygame.key.get_pressed()
        dt = 1/60.0  # Assuming 60 FPS

        for entity in entities:
            player = entity.get_component(Player)
            physics = entity.get_component(Physics)
            
            if player and physics:
                # Handle movement
                move = 0
                if keys[player.controls["left"]]:
                    move -= 1
                if keys[player.controls["right"]]:
                    move += 1
                
                if move != 0:
                    player.facing = move
                
                # Apply movement velocity
                vx, vy = physics.body.velocity
                physics.body.velocity = (move * self.settings.MOVE_SPEED * 60, vy)
                
                # Handle jumping
                if keys[player.controls["jump"]] and player.on_ground:
                    physics.body.velocity = (physics.body.velocity[0], self.settings.JUMP_VELOCITY * 60)
                    player.on_ground = False

class PhysicsSystem(System):
    """Handles physics simulation and collision detection."""
    def __init__(self, space):
        self.space = space

    def update(self, entities):
        # Step physics simulation
        self.space.step(1/60.0)
        
        # Update entity positions from physics bodies
        for entity in entities:
            physics = entity.get_component(Physics)
            position = entity.get_component(Position)
            
            if physics and position:
                position.x = physics.body.position.x
                position.y = physics.body.position.y

class AttackSystem(System):
    """Handles attack logic and collision detection."""
    def __init__(self, settings):
        self.settings = settings

    def update(self, entities):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks() / 1000.0
        
        # Process attacks
        attacks = []
        for entity in entities:
            player = entity.get_component(Player)
            attack = entity.get_component(Attack)
            physics = entity.get_component(Physics)
            
            if player and attack and physics:
                # Handle attack input
                if keys[player.controls["attack"]] and attack.current_cooldown <= 0:
                    attack.attacking = True
                    attack.current_cooldown = attack.cooldown
                    player.last_attack_time = now
                    attacks.append((entity, self._make_attack_hitbox(entity)))
                
                # Update cooldown
                if attack.current_cooldown > 0:
                    attack.current_cooldown = max(0, attack.current_cooldown - 1/60.0)
                    if attack.current_cooldown <= attack.cooldown - attack.attack_duration:
                        attack.attacking = False
        
        # Process attack collisions
        self._process_attack_collisions(entities, attacks)

    def _make_attack_hitbox(self, attacker):
        """Create attack hitbox for the attacker."""
        player = attacker.get_component(Player)
        position = attacker.get_component(Position)
        renderable = attacker.get_component(Renderable)
        
        if player and position and renderable:
            offset = (renderable.width // 2 + 20) * player.facing
            x = position.x + offset
            y = position.y
            rect = pygame.Rect(0, 0, 40, 30)
            rect.center = (x, y)
            return rect
        return None

    def _process_attack_collisions(self, entities, attacks):
        """Process collisions between attacks and players."""
        for attacker, hitbox in attacks:
            if not hitbox:
                continue
                
            for defender in entities:
                defender_player = defender.get_component(Player)
                defender_physics = defender.get_component(Physics)
                defender_renderable = defender.get_component(Renderable)
                
                if (defender_player and defender_physics and defender_renderable and 
                    defender != attacker):
                    
                    # Create defender hitbox
                    def_rect = pygame.Rect(0, 0, defender_renderable.width, defender_renderable.height)
                    def_rect.center = (int(defender_physics.body.position.x), 
                                     int(defender_physics.body.position.y))
                    
                    if hitbox.colliderect(def_rect):
                        # Apply damage and knockback
                        attacker_player = attacker.get_component(Player)
                        attacker_attack = attacker.get_component(Attack)
                        
                        if attacker_player and attacker_attack:
                            defender_player.damage += attacker_attack.damage
                            kb = (attacker_attack.knockback_base + 
                                  defender_player.damage * attacker_attack.knockback_scalar)
                            vec = (kb * attacker_player.facing, -kb * 0.2)
                            defender_physics.body.velocity = (vec[0] * 60, vec[1] * 60)

class RenderSystem(System):
    """Handles rendering of all entities."""
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings

    def update(self, entities):
        # Clear screen
        self.screen.fill(self.settings.BG_COLOR)
        
        # Render all entities
        for entity in entities:
            self._render_entity(entity)
        
        # Update display
        pygame.display.flip()

    def _render_entity(self, entity):
        """Render a single entity."""
        position = entity.get_component(Position)
        renderable = entity.get_component(Renderable)
        player = entity.get_component(Player)
        attack = entity.get_component(Attack)
        stage = entity.get_component(Stage)
        
        if not position or not renderable:
            return
        
        if stage:
            # Render stage
            rect = pygame.Rect(position.x - stage.width//2, position.y - stage.height//2, 
                             stage.width, stage.height)
            pygame.draw.rect(self.screen, stage.color, rect)
        else:
            # Render player
            rect = pygame.Rect(0, 0, renderable.width, renderable.height)
            rect.center = (int(position.x), int(position.y))
            pygame.draw.rect(self.screen, renderable.color, rect)
            
            # Draw face triangle
            if player:
                face_color = (0, 255, 0) if not attack or not attack.attacking else (255, 255, 0)
                tri = self._face_triangle(rect, player.facing)
                pygame.draw.polygon(self.screen, face_color, tri)
                
                # Draw damage
                font = pygame.font.SysFont(None, 28)
                dmg_surf = font.render(str(player.damage), True, (255, 255, 255))
                self.screen.blit(dmg_surf, (rect.centerx - 12, rect.top - 28))
            
            # Draw attack hitbox
            if attack and attack.attacking and attack.current_cooldown > attack.cooldown - attack.attack_duration:
                hitbox = self._make_attack_hitbox(entity)
                if hitbox:
                    pygame.draw.rect(self.screen, self.settings.ATTACK_COLOR, hitbox)

    def _face_triangle(self, rect, facing):
        """Create face triangle for player."""
        cx, cy = rect.center
        if facing == 1:
            tip = (rect.right + 10, cy)
            base1 = (rect.right, cy - 10)
            base2 = (rect.right, cy + 10)
        else:
            tip = (rect.left - 10, cy)
            base1 = (rect.left, cy - 10)
            base2 = (rect.left, cy + 10)
        return [tip, base1, base2]

    def _make_attack_hitbox(self, entity):
        """Create attack hitbox for rendering."""
        player = entity.get_component(Player)
        position = entity.get_component(Position)
        renderable = entity.get_component(Renderable)
        
        if player and position and renderable:
            offset = (renderable.width // 2 + 20) * player.facing
            x = position.x + offset
            y = position.y
            rect = pygame.Rect(0, 0, 40, 30)
            rect.center = (x, y)
            return rect
        return None 