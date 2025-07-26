import pygame
import json
import math
import random
from typing import List, Tuple

class Settings:
    def __init__(self): self.data = json.load(open('settings.json'))
    def __getitem__(self, key): return self.data[key]

class Explosion:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], duration: float):
        self.x, self.y, self.color, self.duration, self.timer = x, y, color, duration, 0
    def update(self, dt: float) -> bool:
        self.timer += dt
        return self.timer < self.duration
    def draw(self, screen: pygame.Surface, radius: int):
        alpha = int(255 * (1 - self.timer / self.duration))
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (radius, radius), radius, 3)
        screen.blit(surf, (self.x - radius, self.y - radius))

class Shot:
    def __init__(self, target_x: int, target_y: int, speed: float):
        self.x, self.y = 400, 580
        self.target_x, self.target_y = target_x, target_y
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        self.vx, self.vy = (dx/dist) * speed, (dy/dist) * speed
        self.exploded = False
        self.trail = []  # Store previous positions for trail effect
    def update(self, dt: float) -> bool:
        if self.exploded: return False
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        if math.dist((self.x, self.y), (self.target_x, self.target_y)) < 10:
            self.exploded = True
        return True
    def draw(self, screen: pygame.Surface, radius: int, color: Tuple[int, int, int]):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail[:-1]):
            alpha = int(255 * (i+1) / len(self.trail))
            trail_color = (*color, alpha)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, trail_color, (radius, radius), radius)
            screen.blit(surf, (int(trail_x) - radius, int(trail_y) - radius))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)

class Attacker:
    def __init__(self, target_x: int, speed: float):
        # Random start position along the top of the screen
        self.x = random.randint(50, 750)  # Random X position, avoiding edges
        self.y = -10
        
        # Calculate angle to target with some variance
        dx = target_x - self.x
        dy = 600 - self.y  # Distance to bottom of screen
        angle = math.atan2(dx, dy) + random.uniform(-0.26, 0.26)  # ±15 degrees variance
        
        self.vx, self.vy = math.sin(angle) * speed, math.cos(angle) * speed
        self.trail = []
    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        return self.y < 600
    def draw(self, screen: pygame.Surface, radius: int, color: Tuple[int, int, int]):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail[:-1]):
            alpha = int(255 * (i+1) / len(self.trail))
            trail_color = (*color, alpha)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, trail_color, (radius, radius), radius)
            screen.blit(surf, (int(trail_x) - radius, int(trail_y) - radius))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)

class Square:
    def __init__(self, x: int, y: int, size: int):
        self.x, self.y, self.size, self.alive, self.flash_timer = x, y, size, True, 0
    def hit(self): self.alive = False; self.flash_timer = 0.3
    def update(self, dt: float):
        if self.flash_timer > 0: self.flash_timer -= dt
    def draw(self, screen: pygame.Surface, colors: dict):
        if not self.alive: return
        color = colors['RED'] if self.flash_timer > 0 else colors['BLUE']
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings['WINDOW']['WIDTH'], self.settings['WINDOW']['HEIGHT']), pygame.DOUBLEBUF)
        pygame.display.set_caption("Defend")
        self.clock = pygame.time.Clock()
        self.fonts = {size: pygame.font.Font(None, size) for size in [24, 36, 48]}
        self.load_sounds()
        self.reset_game()
    
    def load_sounds(self):
        self.sounds = {
            'enemy_die': pygame.mixer.Sound('sounds/enemy_die.wav'),
            'wave_complete': pygame.mixer.Sound('sounds/wave_complete.wav'),
            'city_destroyed': pygame.mixer.Sound('sounds/city_destroyed.wav'),
            'intercepted_attack': pygame.mixer.Sound('sounds/intercepted_attack.wav')
        }
    
    def trigger_chain_reaction(self, x: int, y: int, visited=None, chain_length=0):
        """Trigger chain reaction explosions from a given point"""
        if visited is None: visited = set()
        killed_count = 0
        
        for attacker in self.attackers[:]:
            if (attacker.x, attacker.y) not in visited and math.dist((x, y), (attacker.x, attacker.y)) < self.settings['SHOT']['EXPLOSION_RADIUS']:
                visited.add((attacker.x, attacker.y))
                self.explosions.append(Explosion(attacker.x, attacker.y, self.settings['COLORS']['GREEN'], 0.5))
                self.score += self.settings['SCORING']['INTERCEPT_BONUS']
                self.attackers.remove(attacker)
                self.sounds['intercepted_attack'].play()
                killed_count += 1
                # Continue chain reaction
                self.trigger_chain_reaction(attacker.x, attacker.y, visited, chain_length + 1)
        
        # Award chain reaction bonus for each step in the chain
        if chain_length > 0:
            self.score += self.settings['SCORING']['CHAIN_REACTION_BONUS']
        
        # Award multi-kill bonus if this explosion killed multiple attackers
        if killed_count > 1:
            self.score += self.settings['SCORING']['MULTI_KILL_BONUS'] * killed_count
    
    def get_random_spawn_wait(self) -> float:
        """Calculate random wait time between enemy spawns with weighted distribution"""
        if random.random() < self.settings['ATTACKER']['SPAWN_VARIATION']['NO_WAIT_CHANCE']:
            return 0.0  # No wait - immediate spawn
        
        # Choose between low, medium, high, or max wait
        wait_type = random.choices(
            ['LOW_WAIT', 'MEDIUM_WAIT', 'HIGH_WAIT', 'MAX_WAIT'],
            weights=[0.6, 0.25, 0.1, 0.05]  # Makes max wait very rare
        )[0]
        
        return self.settings['ATTACKER']['SPAWN_VARIATION'][wait_type]
    
    def reset_game(self):
        self.score, self.wave, self.squares_lost_this_wave = 0, 1, 0
        self.shots, self.attackers, self.explosions = [], [], []
        self.shot_timer, self.spawn_timer, self.wave_clear_timer = 0, 0, 0
        self.game_started, self.game_over, self.wave_clear_display, self.victory = False, False, False, False
        self.squares = [Square(50 + i * 120, self.settings['SQUARE']['Y_POSITION'], 
                              self.settings['SQUARE']['SIZE']) for i in range(self.settings['GAME']['SQUARES_TO_PROTECT'])]
        self.attackers_to_spawn = self.settings['ATTACKER']['COUNTS'][self.wave - 1]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over:
                if not self.game_started: self.game_started = True
                elif self.shot_timer <= 0:
                    self.shots.append(Shot(*pygame.mouse.get_pos(), self.settings['SHOT']['PLAYER_SPEED']))
                    self.shot_timer = self.settings['GAME']['SHOT_RELOAD_TIME']
        return True
    
    def update(self, dt: float):
        if self.game_over: return
        
        # Update timers
        self.shot_timer = max(0, self.shot_timer - dt)
        if self.wave_clear_display:
            self.wave_clear_timer -= dt
            if self.wave_clear_timer <= 0: self.wave_clear_display = False
        
        # Spawn attackers
        if self.game_started and self.attackers_to_spawn > 0:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                # Random target along bottom of screen, with preference for areas with squares
                if random.random() < 0.7:  # 70% chance to target squares
                    target_x = random.choice([sq.x + self.settings['SQUARE']['SIZE']//2 for sq in self.squares if sq.alive])
                else:  # 30% chance to target random bottom position
                    target_x = random.randint(50, 750)
                
                self.attackers.append(Attacker(target_x, self.settings['ATTACKER']['ENEMY_BASE_SPEED']))
                self.attackers_to_spawn -= 1
                
                # Calculate next spawn time with variation
                base_gap = self.settings['ATTACKER']['SPAWN_GAPS'][self.wave - 1]
                variation = self.get_random_spawn_wait()
                self.spawn_timer = base_gap + variation
        
        # Update game objects
        self.shots = [shot for shot in self.shots if shot.update(dt)]
        self.attackers = [att for att in self.attackers if att.update(dt)]
        self.explosions = [exp for exp in self.explosions if exp.update(dt)]
        for square in self.squares: square.update(dt)
        
        # Handle shot explosions and chain reactions
        for shot in self.shots[:]:
            if shot.exploded:
                # Create explosion at target point
                self.explosions.append(Explosion(shot.target_x, shot.target_y, self.settings['COLORS']['GREEN'], 0.5))
                # Trigger chain reaction from target point
                self.trigger_chain_reaction(shot.target_x, shot.target_y)
        
        # Direct shot collision (before explosion)
        for shot in self.shots[:]:
            if not shot.exploded:
                for attacker in self.attackers[:]:
                    if math.dist((shot.x, shot.y), (attacker.x, attacker.y)) < self.settings['SHOT']['DIRECT_HIT_RADIUS']:
                        self.explosions.append(Explosion(attacker.x, attacker.y, self.settings['COLORS']['GREEN'], 
                                                        self.settings['GAME']['EXPLOSION_DURATION']))
                        self.score += self.settings['SCORING']['INTERCEPT_BONUS']
                        self.attackers.remove(attacker)
                        shot.exploded = True
                        self.sounds['intercepted_attack'].play()
                        # Trigger chain reaction
                        self.trigger_chain_reaction(attacker.x, attacker.y, set(), 1)
                        break
        
        # Attacker collisions
        for attacker in self.attackers[:]:
            # Check floor collision
            if attacker.y >= 590:
                self.explosions.append(Explosion(attacker.x, attacker.y, self.settings['COLORS']['ORANGE'], 0.3))
                self.attackers.remove(attacker)
                self.sounds['enemy_die'].play()
                continue
            
            # Check square collisions
            for square in self.squares:
                if square.alive and (square.x < attacker.x < square.x + self.settings['SQUARE']['SIZE'] and 
                                   square.y < attacker.y < square.y + self.settings['SQUARE']['SIZE']):
                    square.hit()
                    self.squares_lost_this_wave += 1
                    self.score += self.settings['SCORING']['SQUARE_PENALTY']
                    self.explosions.append(Explosion(attacker.x, attacker.y, self.settings['COLORS']['ORANGE'], 0.3))
                    self.attackers.remove(attacker)
                    self.sounds['city_destroyed'].play()
                    break
        
        # Wave management
        if len(self.attackers) == 0 and self.attackers_to_spawn == 0:
            alive_squares = sum(1 for sq in self.squares if sq.alive)
            if alive_squares >= 1:
                self.score += alive_squares * self.settings['SCORING']['WAVE_CLEAR_MULTIPLIER']
                if self.wave < self.settings['GAME']['TOTAL_WAVES']:
                    self.wave += 1
                    self.squares_lost_this_wave = 0
                    self.attackers_to_spawn = self.settings['ATTACKER']['COUNTS'][self.wave - 1]
                    self.wave_clear_display = True
                    self.wave_clear_timer = self.settings['GAME']['WAVE_CLEAR_DISPLAY_TIME']
                    self.sounds['wave_complete'].play()
                else:
                    self.victory = True
                    self.game_over = True
            else:
                self.game_over = True
        
        # Check wave loss
        if self.squares_lost_this_wave >= self.settings['GAME']['MAX_SQUARES_LOST']:
            self.game_over = True
    
    def draw(self):
        self.screen.fill(self.settings['COLORS']['BLACK'])
        
        # Draw game objects
        for square in self.squares: square.draw(self.screen, self.settings['COLORS'])
        for shot in self.shots: shot.draw(self.screen, self.settings['SHOT']['RADIUS'], self.settings['COLORS']['GREEN'])
        for attacker in self.attackers: attacker.draw(self.screen, self.settings['ATTACKER']['RADIUS'], self.settings['COLORS']['ORANGE'])
        for explosion in self.explosions: explosion.draw(self.screen, self.settings['SHOT']['EXPLOSION_RADIUS'])
        
        # Draw HUD
        hud_text = f"Score {self.score:04d}  ••  Lvl {self.wave}/{self.settings['GAME']['TOTAL_WAVES']}"
        hud_surf = self.fonts[24].render(hud_text, True, self.settings['COLORS']['WHITE'])
        self.screen.blit(hud_surf, (10, 10))
        
        # Draw title or game over
        if not self.game_started:
            title_surf = self.fonts[48].render("DEFEND", True, self.settings['COLORS']['WHITE'])
            self.screen.blit(title_surf, (400 - title_surf.get_width()//2, 250))
        elif self.game_over:
            final_text = f"Final Score: {self.score}"
            final_surf = self.fonts[36].render(final_text, True, self.settings['COLORS']['WHITE'])
            self.screen.blit(final_surf, (400 - final_surf.get_width()//2, 250))
            
            # Show victory message if player completed all waves
            if self.victory:
                victory_text = "Congratulations! You Defended Well."
                victory_surf = self.fonts[36].render(victory_text, True, self.settings['COLORS']['GREEN'])
                self.screen.blit(victory_surf, (400 - victory_surf.get_width()//2, 200))
        
        # Draw wave clear
        if self.wave_clear_display:
            wave_surf = self.fonts[36].render("Wave Clear!", True, self.settings['COLORS']['GREEN'])
            self.screen.blit(wave_surf, (400 - wave_surf.get_width()//2, 200))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        frame_count = 0
        last_time = pygame.time.get_ticks()
        while running:
            dt = self.clock.tick(self.settings['WINDOW']['FPS']) / 1000.0
            frame_count += 1
            
            # Debug: Print actual FPS every second
            current_time = pygame.time.get_ticks()
            if current_time - last_time >= 1000:
                actual_fps = frame_count
                print(f"Actual FPS: {actual_fps}")
                frame_count = 0
                last_time = current_time
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    Game().run() 