import pygame
import random
from typing import Dict, List
from utils.constants import *
from entities.enemy import Enemy

class WaveManager:
    def __init__(self, settings: Dict):
        self.settings = settings
        self.current_wave = 0
        self.total_waves = 0
        self.wave_data = []
        
        # Wave state
        self.wave_active = False
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.spawn_delay = 1.0  # Time between enemy spawns
        self.wave_delay = 3.0   # Time between waves
        
        # Level data
        self.current_level = 1
        self.difficulty_multiplier = 1.0
    
    def start_level(self, level_num: int, wave_data: List[Dict]):
        """Start a new level with wave data"""
        self.current_level = level_num
        self.wave_data = wave_data
        self.total_waves = len(wave_data)
        self.current_wave = 0
        self.wave_active = False
        self.difficulty_multiplier = 1.0 + (level_num - 1) * 0.2
    
    def start_next_wave(self):
        """Start the next wave"""
        if self.current_wave < self.total_waves and not self.wave_active:
            self.current_wave += 1
            self.prepare_wave(self.current_wave)
            self.wave_active = True
            self.spawn_timer = 0
    
    def prepare_wave(self, wave_num: int):
        """Prepare enemies for the current wave"""
        wave_info = self.wave_data[wave_num - 1]
        self.enemies_to_spawn = []
        
        # Apply difficulty scaling
        base_count = wave_info.get('count', 5)
        scaled_count = int(base_count * self.difficulty_multiplier)
        
        # Create enemy list
        for _ in range(scaled_count):
            enemy_type = self.select_enemy_type(wave_info)
            self.enemies_to_spawn.append(enemy_type)
        
        # Shuffle for variety
        random.shuffle(self.enemies_to_spawn)
    
    def select_enemy_type(self, wave_info: Dict) -> str:
        """Select enemy type based on wave configuration"""
        enemy_weights = wave_info.get('enemies', {ENEMY_SMALL: 1})
        
        # Convert to list for random selection
        enemy_types = list(enemy_weights.keys())
        weights = list(enemy_weights.values())
        
        return random.choices(enemy_types, weights=weights)[0]
    
    def update(self, dt: float, game_state):
        """Update wave spawning logic"""
        if not self.wave_active:
            return
        
        self.spawn_timer += dt
        
        # Spawn enemies
        if self.enemies_to_spawn and self.spawn_timer >= self.spawn_delay:
            enemy_type = self.enemies_to_spawn.pop(0)
            enemy = Enemy(enemy_type, self.settings, game_state.path_waypoints)
            game_state.enemies.append(enemy)
            self.spawn_timer = 0
        
        # Check if wave is complete
        if not self.enemies_to_spawn and not game_state.enemies:
            self.wave_active = False
            if self.current_wave >= self.total_waves:
                # Level complete
                pass
    
    def is_level_complete(self) -> bool:
        """Check if all waves are complete"""
        return self.current_wave >= self.total_waves and not self.wave_active
    
    def get_wave_progress(self) -> float:
        """Get wave completion progress (0.0 to 1.0)"""
        if self.total_waves == 0:
            return 0.0
        return self.current_wave / self.total_waves 