import pygame
import math
from typing import Dict, List, Tuple
from utils.constants import *
from utils.helpers import distance, grid_to_pixel

class Enemy:
    def __init__(self, enemy_type: str, settings: Dict, path_waypoints: List[Tuple[int, int]]):
        self.enemy_type = enemy_type
        self.settings = settings
        self.enemy_data = settings['enemies'][enemy_type]
        
        # Stats
        self.max_health = self.enemy_data['health']
        self.health = self.max_health
        self.speed = self.enemy_data['speed']
        self.size = self.enemy_data['size']
        self.reward = self.enemy_data['reward']
        
        # Movement
        self.path_waypoints = path_waypoints
        self.current_waypoint = 0
        self.x, self.y = self.get_start_position()
        # Start targeting the next waypoint (waypoint 1) instead of current waypoint (waypoint 0)
        self.current_waypoint = 1  # Start targeting waypoint 1
        self.target_x, self.target_y = self.get_next_waypoint()
        self.current_waypoint = 0  # But we're still at waypoint 0
        
        # State
        self.distance_to_goal = self.calculate_distance_to_goal()
        
        # Debug info
        print(f"=== ENEMY SPAWNED ===")
        print(f"Type: {enemy_type}")
        print(f"Speed: {self.speed}")
        print(f"Path waypoints: {len(path_waypoints)} points")
        print(f"Start position: ({self.x}, {self.y})")
        print(f"First target: ({self.target_x}, {self.target_y})")
        print(f"Path: {path_waypoints[:5]}...")  # Show first 5 waypoints
    
    def get_start_position(self) -> Tuple[float, float]:
        """Get starting position from first waypoint"""
        if self.path_waypoints:
            start_pos = grid_to_pixel(self.path_waypoints[0], self.settings['gameplay']['grid_size'])
            return start_pos
        return (0.0, 0.0)
    
    def get_next_waypoint(self) -> Tuple[float, float]:
        """Get next waypoint position"""
        next_waypoint_index = self.current_waypoint + 1
        if next_waypoint_index < len(self.path_waypoints):
            next_pos = grid_to_pixel(self.path_waypoints[next_waypoint_index], 
                                   self.settings['gameplay']['grid_size'])
            return next_pos
        # If we've reached the end, return the final waypoint position
        # This will cause the enemy to reach the goal on the next update
        final_pos = grid_to_pixel(self.path_waypoints[-1], self.settings['gameplay']['grid_size'])
        return final_pos
    
    def update(self, dt: float, path_waypoints: List[Tuple[int, int]]):
        """Update enemy movement and state"""
        # Debug: Print update info every 60 frames (1 second at 60 FPS)
        if pygame.time.get_ticks() % 1000 < 16:
            print(f"=== ENEMY UPDATE ===")
            print(f"Position: ({self.x:.1f}, {self.y:.1f})")
            print(f"Target: ({self.target_x:.1f}, {self.target_y:.1f})")
            print(f"Current waypoint: {self.current_waypoint}/{len(self.path_waypoints)}")
            print(f"Speed: {self.speed}, dt: {dt:.3f}")
            print(f"Reached goal: {self.reached_goal()}")
        
        # Update path if it changed
        if path_waypoints != self.path_waypoints:
            self.path_waypoints = path_waypoints
            self.current_waypoint = min(self.current_waypoint, len(path_waypoints) - 1)
            self.target_x, self.target_y = self.get_next_waypoint()
        
        # Only move if we haven't reached the goal
        if self.reached_goal():
            if pygame.time.get_ticks() % 1000 < 16:
                print("Enemy reached goal, not moving")
            return
        
        # Move towards target waypoint
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        
        if pygame.time.get_ticks() % 1000 < 16:
            print(f"Distance to target: {distance_to_target:.1f}")
            print(f"Move distance: {self.speed * dt:.1f}")
        
        # Use a small threshold to prevent getting stuck due to floating point precision
        if distance_to_target < 1.0:
            # We're very close to the target, consider it reached
            old_waypoint = self.current_waypoint
            self.x, self.y = self.target_x, self.target_y
            self.current_waypoint += 1
            if self.current_waypoint < len(self.path_waypoints):
                old_target = (self.target_x, self.target_y)
                self.target_x, self.target_y = self.get_next_waypoint()
                if pygame.time.get_ticks() % 1000 < 16:
                    print(f"Reached waypoint {old_waypoint} (close), moving from {old_target} to ({self.target_x:.1f}, {self.target_y:.1f})")
                    print(f"New waypoint index: {self.current_waypoint}")
            else:
                if pygame.time.get_ticks() % 1000 < 16:
                    print(f"Reached final waypoint {old_waypoint}, enemy should reach goal")
                    print(f"ENEMY GOAL CHECK: current_waypoint={self.current_waypoint}, total_waypoints={len(self.path_waypoints)}, reached_goal={self.reached_goal()}")
        elif distance_to_target > 0:
            # Normal movement
            move_distance = self.speed * dt
            if move_distance >= distance_to_target:
                # Reached waypoint, move to next
                old_waypoint = self.current_waypoint
                self.x, self.y = self.target_x, self.target_y
                self.current_waypoint += 1
                if self.current_waypoint < len(self.path_waypoints):
                    old_target = (self.target_x, self.target_y)
                    self.target_x, self.target_y = self.get_next_waypoint()
                    if pygame.time.get_ticks() % 1000 < 16:
                        print(f"Reached waypoint {old_waypoint}, moving from {old_target} to ({self.target_x:.1f}, {self.target_y:.1f})")
                        print(f"New waypoint index: {self.current_waypoint}")
                else:
                    if pygame.time.get_ticks() % 1000 < 16:
                        print(f"Reached final waypoint {old_waypoint}, enemy should reach goal")
                        print(f"ENEMY GOAL CHECK: current_waypoint={self.current_waypoint}, total_waypoints={len(self.path_waypoints)}, reached_goal={self.reached_goal()}")
            else:
                # Move towards waypoint
                old_x, old_y = self.x, self.y
                self.x += (dx / distance_to_target) * move_distance
                self.y += (dy / distance_to_target) * move_distance
                if pygame.time.get_ticks() % 1000 < 16:
                    print(f"Moved from ({old_x:.1f}, {old_y:.1f}) to ({self.x:.1f}, {self.y:.1f})")
        else:
            # Fallback: force progression if completely stuck
            if pygame.time.get_ticks() % 1000 < 16:
                print("Enemy completely stuck, forcing progression")
            if self.current_waypoint + 1 < len(self.path_waypoints):
                self.current_waypoint += 1
                self.target_x, self.target_y = self.get_next_waypoint()
            elif self.current_waypoint + 1 == len(self.path_waypoints):
                # Force progression to final waypoint to trigger goal
                self.current_waypoint += 1
                self.target_x, self.target_y = self.get_next_waypoint()
        
        # Update distance to goal
        self.distance_to_goal = self.calculate_distance_to_goal()
    
    def calculate_distance_to_goal(self) -> float:
        """Calculate distance to final goal"""
        if not self.path_waypoints:
            return 0.0
        
        goal_pos = grid_to_pixel(self.path_waypoints[-1], self.settings['gameplay']['grid_size'])
        return distance((self.x, self.y), goal_pos)
    
    def take_damage(self, damage: int):
        """Take damage from tower"""
        self.health -= damage
    
    def is_dead(self) -> bool:
        """Check if enemy is dead"""
        return self.health <= 0
    
    def reached_goal(self) -> bool:
        """Check if enemy reached the goal"""
        goal_reached = self.current_waypoint >= len(self.path_waypoints)
        if goal_reached:
            print(f"ENEMY GOAL CHECK: current_waypoint={self.current_waypoint}, total_waypoints={len(self.path_waypoints)}, reached_goal={goal_reached}")
        return goal_reached 