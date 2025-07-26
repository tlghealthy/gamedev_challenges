import pygame
import math
from typing import Dict, List, Tuple, Optional
from utils.constants import *
from utils.helpers import distance, grid_to_pixel

class Tower:
    def __init__(self, grid_pos: Tuple[int, int], tower_type: str, settings: Dict):
        self.grid_pos = grid_pos
        self.tower_type = tower_type
        self.settings = settings
        self.tower_data = settings['towers'][tower_type]
        
        # Stats
        self.level = 1
        self.damage = self.tower_data['damage']
        self.fire_rate = self.tower_data['fire_rate']
        self.range = self.tower_data['range']
        self.projectile_speed = self.tower_data['projectile_speed']
        
        # State
        self.last_shot_time = 0
        self.target = None
        self.pixel_pos = grid_to_pixel(grid_pos, settings['gameplay']['grid_size'])
        
        # Projectiles for visualization
        self.projectiles = []
    
    def update(self, dt: float, enemies: List):
        """Update tower logic"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Find target if none or target is dead/out of range
        if not self.target or not self.is_target_valid(self.target, enemies):
            self.target = self.find_target(enemies)
        
        # Shoot if we have a target and enough time has passed
        if self.target and current_time - self.last_shot_time >= self.fire_rate:
            self.shoot(self.target)
            self.last_shot_time = current_time
    
    def find_target(self, enemies: List) -> Optional:
        """Find best target based on tower type"""
        valid_enemies = [e for e in enemies if self.is_in_range(e)]
        
        if not valid_enemies:
            return None
        
        # Different targeting strategies based on tower type
        if self.tower_type == TOWER_RED:  # Fast, anti-swarm
            return min(valid_enemies, key=lambda e: e.health)  # Target weakest
        elif self.tower_type == TOWER_BLUE:  # Balanced
            return min(valid_enemies, key=lambda e: e.distance_to_goal)  # Target closest to goal
        elif self.tower_type == TOWER_GREEN:  # Heavy, anti-boss
            return max(valid_enemies, key=lambda e: e.health)  # Target strongest
        
        return valid_enemies[0]  # Default to first enemy
    
    def is_in_range(self, enemy) -> bool:
        """Check if enemy is in tower range"""
        return distance(self.pixel_pos, (enemy.x, enemy.y)) <= self.range
    
    def is_target_valid(self, target, enemies: List) -> bool:
        """Check if current target is still valid"""
        return target in enemies and self.is_in_range(target) and not target.is_dead()
    
    def shoot(self, target):
        """Shoot at target"""
        # Create visual projectile
        projectile = {
            'start_pos': self.pixel_pos,
            'end_pos': (target.x, target.y),
            'frames_remaining': 2,
            'color': self.settings['colors']['projectile']
        }
        self.projectiles.append(projectile)
        
        # Apply damage
        target.take_damage(self.damage)
    
    def update_projectiles(self):
        """Update projectile visualization"""
        # Update existing projectiles
        for projectile in self.projectiles[:]:
            projectile['frames_remaining'] -= 1
            if projectile['frames_remaining'] <= 0:
                self.projectiles.remove(projectile)
    
    def get_projectiles(self):
        """Get current projectiles for rendering"""
        return self.projectiles
    
    def upgrade(self):
        """Upgrade tower"""
        if self.level < self.tower_data['max_level']:
            self.level += 1
            # Increase stats by 50% per level
            multiplier = 1 + (self.level - 1) * 0.5
            self.damage = int(self.tower_data['damage'] * multiplier)
            self.fire_rate = self.tower_data['fire_rate'] / multiplier
            self.range = int(self.tower_data['range'] * multiplier)
    
    def get_upgrade_cost(self) -> int:
        """Get cost to upgrade tower"""
        if self.level >= self.tower_data['max_level']:
            return 0
        return self.tower_data['upgrade_cost'] * self.level 