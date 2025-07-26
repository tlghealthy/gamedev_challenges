import pygame
from typing import Dict, List, Optional, Tuple
from utils.constants import *
from entities.tower import Tower
from entities.enemy import Enemy
from systems.wave_manager import WaveManager
from systems.economy import Economy
from levels.level_loader import LevelLoader

class GameState:
    def __init__(self, settings: Dict):
        self.settings = settings
        self.state = MENU  # Start in menu state
        self.current_level = 1  # Start at level 1
        self.max_level = settings['levels']['max_levels']
        
        # Game systems
        self.economy = Economy(settings)
        self.wave_manager = WaveManager(settings)
        self.level_loader = LevelLoader(settings)
        
        # Game entities
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []
        self.projectiles: List = []  # Will implement later
        
        # Game data
        self.grid_size = settings['gameplay']['grid_size']
        self.grid_width = settings['display']['width'] // self.grid_size
        self.grid_height = settings['display']['height'] // self.grid_size
        
        # Current level data
        self.level_data = None
        self.path_waypoints = []
        self.placeable_tiles = set()
        
        # UI state
        self.selected_tower_type = None
        self.hovered_grid_pos = None
        
        # Level progression
        self.victory_timer = 0
        self.victory_delay = 2.0  # Show victory screen for 2 seconds before auto-progressing
        
        # Don't load level immediately - wait for menu selection
        # self.load_level(1)
    
    def load_level(self, level_num: int):
        """Load level data and initialize game state"""
        self.current_level = level_num
        self.level_data = self.level_loader.load_level(level_num)
        self.path_waypoints = self.level_data['path']
        self.placeable_tiles = set(self.level_data['placeable_tiles'])
        
        # Reset game state
        self.towers.clear()
        self.enemies.clear()
        self.projectiles.clear()
        self.economy.reset()
        self.wave_manager.start_level(level_num, self.level_data['waves'])
        
        # Start the first wave automatically
        self.wave_manager.start_next_wave()
        
        self.state = PLAYING
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.hovered_grid_pos = self.pixel_to_grid(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click"""
        if self.state != PLAYING:
            return
        
        grid_pos = self.pixel_to_grid(pos)
        
        # Check if clicking on existing tower first (for upgrades)
        if self.get_tower_at(grid_pos):
            self.select_tower(grid_pos)
        # Check if clicking on placeable tile for new tower
        elif grid_pos in self.placeable_tiles and self.selected_tower_type:
            self.place_tower(grid_pos, self.selected_tower_type)
    
    def handle_keydown(self, key: int):
        """Handle keyboard input"""
        if key == pygame.K_1:
            self.selected_tower_type = TOWER_RED
        elif key == pygame.K_2:
            self.selected_tower_type = TOWER_BLUE
        elif key == pygame.K_3:
            self.selected_tower_type = TOWER_GREEN
        elif key == pygame.K_SPACE:
            self.wave_manager.start_next_wave()
        elif key == pygame.K_ESCAPE:
            self.selected_tower_type = None
        elif key == pygame.K_n and self.state == VICTORY:
            # Next level shortcut
            self.progress_to_next_level()
        
        # Debug/Testing keys
        elif key == pygame.K_9 and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Secret level skip: Ctrl+9
            print(f"SECRET: Skipping from level {self.current_level} to level {self.current_level + 1}")
            if self.current_level < self.max_level:
                self.progress_to_next_level()
        elif key == pygame.K_m and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Money cheat: Ctrl+M
            print("SECRET: Adding 500 money")
            self.economy.add_money(500)
        elif key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Life cheat: Ctrl+L
            print("SECRET: Adding 10 lives")
            self.economy.gain_life(10)
        elif key == pygame.K_k and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Kill all enemies: Ctrl+K
            print("SECRET: Killing all enemies")
            self.enemies.clear()
        elif key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Win level: Ctrl+W
            print("SECRET: Completing current level")
            self.state = VICTORY
            self.victory_timer = 0
        elif key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Restart level: Ctrl+R
            print("SECRET: Restarting current level")
            self.load_level(self.current_level)
        elif key == pygame.K_0 and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Go to level 1: Ctrl+0
            print("SECRET: Going to level 1")
            self.load_level(1)
        elif key == pygame.K_5 and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Go to level 5: Ctrl+5
            print("SECRET: Going to level 5")
            self.load_level(5)
        elif key == pygame.K_p and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Test procedural generation: Ctrl+P
            print("SECRET: Testing procedural generation (level 10)")
            self.load_level(10)
        elif key == pygame.K_t and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Test high difficulty: Ctrl+T
            print("SECRET: Testing high difficulty procedural level")
            # Temporarily override level loader to generate high difficulty level
            import random
            from levels.level_data import generate_procedural_level, generate_waves_for_difficulty
            grid_width = self.settings['display']['width'] // self.settings['gameplay']['grid_size']
            grid_height = self.settings['display']['height'] // self.settings['gameplay']['grid_size']
            
            level_data = generate_procedural_level(
                difficulty=90,
                path_length=80,
                grid_width=grid_width,
                grid_height=grid_height,
                seed=random.randint(1, 1000)
            )
            level_data['waves'] = generate_waves_for_difficulty(90, 80)
            
            # Apply the generated level
            self.path_waypoints = level_data['path']
            self.placeable_tiles = set(level_data['placeable_tiles'])
            self.towers.clear()
            self.enemies.clear()
            self.projectiles.clear()
            self.economy.reset()
            self.wave_manager.start_level(self.current_level, level_data['waves'])
            self.wave_manager.start_next_wave()
            self.state = PLAYING
    
    def progress_to_next_level(self):
        """Progress to the next level"""
        if self.current_level < self.max_level:
            next_level = self.current_level + 1
            print(f"Progressing from level {self.current_level} to level {next_level}")
            self.load_level(next_level)
        else:
            # Game complete - go back to menu
            print("Game complete! Returning to menu.")
            self.state = MENU
    
    def place_tower(self, grid_pos: Tuple[int, int], tower_type: str):
        """Place tower at grid position"""
        # Check if there's already a tower at this position
        if self.get_tower_at(grid_pos):
            print(f"Tower already exists at position {grid_pos}")
            return
        
        # Check if position is placeable and player can afford it
        if grid_pos in self.placeable_tiles and self.economy.can_afford(self.settings['towers'][tower_type]['cost']):
            tower = Tower(grid_pos, tower_type, self.settings)
            self.towers.append(tower)
            self.economy.spend(self.settings['towers'][tower_type]['cost'])
            self.placeable_tiles.discard(grid_pos)
            print(f"Placed {tower_type} tower at {grid_pos}")
        elif not self.economy.can_afford(self.settings['towers'][tower_type]['cost']):
            print(f"Cannot afford {tower_type} tower")
        elif grid_pos not in self.placeable_tiles:
            print(f"Position {grid_pos} is not placeable")
    
    def check_tower_affordability(self):
        """Check if player can afford selected tower and clear selection if not"""
        if self.selected_tower_type:
            tower_cost = self.settings['towers'][self.selected_tower_type]['cost']
            if not self.economy.can_afford(tower_cost):
                print(f"Cannot afford {self.selected_tower_type} tower (${tower_cost}), clearing selection")
                self.selected_tower_type = None
    
    def select_tower(self, grid_pos: Tuple[int, int]):
        """Select tower for upgrade or info"""
        tower = self.get_tower_at(grid_pos)
        if tower and self.economy.can_afford(tower.get_upgrade_cost()):
            tower.upgrade()
            self.economy.spend(tower.get_upgrade_cost())
    
    def get_tower_at(self, grid_pos: Tuple[int, int]) -> Optional[Tower]:
        """Get tower at grid position"""
        for tower in self.towers:
            if tower.grid_pos == grid_pos:
                return tower
        return None
    
    def pixel_to_grid(self, pixel_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert pixel position to grid position"""
        return (pixel_pos[0] // self.grid_size, pixel_pos[1] // self.grid_size)
    
    def update(self, dt: float):
        """Update game state"""
        if self.state == VICTORY:
            # Update victory timer for auto-progression
            self.victory_timer += dt
            if self.victory_timer >= self.victory_delay:
                self.progress_to_next_level()
            return
        elif self.state != PLAYING:
            return
        
        # Debug: Print update info occasionally
        if pygame.time.get_ticks() % 1000 < 16:
            print(f"=== GAME STATE UPDATE ===")
            print(f"Enemies: {len(self.enemies)}")
            print(f"Towers: {len(self.towers)}")
            print(f"Wave active: {self.wave_manager.wave_active}")
            print(f"Current wave: {self.wave_manager.current_wave}")
        
        # Update systems
        self.wave_manager.update(dt, self)
        self.economy.update(dt)
        
        # Check if player can still afford selected tower
        self.check_tower_affordability()
        
        # Update entities
        for tower in self.towers:
            tower.update(dt, self.enemies)
            tower.update_projectiles()
        
        for enemy in self.enemies[:]:
            enemy.update(dt, self.path_waypoints)
            if enemy.reached_goal():
                print(f"ENEMY REACHED GOAL! Removing enemy, losing life. Lives: {self.economy.lives} -> {self.economy.lives - 1}")
                self.enemies.remove(enemy)
                self.economy.lose_life()
                if self.economy.lives <= 0:
                    self.state = GAME_OVER
            elif enemy.is_dead():
                print(f"Enemy died, adding money: {enemy.reward}")
                self.enemies.remove(enemy)
                self.economy.add_money(enemy.reward)
        
        # Check level completion
        if self.wave_manager.is_level_complete() and not self.enemies:
            print(f"Level {self.current_level} complete!")
            self.state = VICTORY
            self.victory_timer = 0  # Reset victory timer 