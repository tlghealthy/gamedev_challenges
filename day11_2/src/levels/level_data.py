from utils.constants import *
import random
import math

# Helper function to generate placeable tiles
def generate_placeable_tiles(path, grid_width=30, grid_height=20):
    """Generate placeable tiles based on path"""
    path_set = set(path)
    placeable = []
    for x in range(grid_width):
        for y in range(grid_height):
            if (x, y) not in path_set:
                placeable.append((x, y))
    return placeable

def generate_procedural_level(difficulty=50, path_length=50, grid_width=30, grid_height=20, seed=None):
    """
    Generate a procedural level with path and obstacles
    
    Args:
        difficulty (0-100): Higher values create more obstacles and complex paths
        path_length (0-100): Higher values create longer paths
        grid_width, grid_height: Grid dimensions
        seed: Random seed for reproducible generation
    """
    if seed is not None:
        random.seed(seed)
    
    # Convert difficulty and length to actual values
    actual_length = int(20 + (path_length / 100) * 40)  # 20-60 waypoints
    obstacle_chance = difficulty / 100  # 0-1 chance of placing obstacles
    
    # Generate path using A* inspired algorithm with noise
    path = generate_path(grid_width, grid_height, actual_length, difficulty)
    
    # Generate obstacles based on path and difficulty
    obstacles = generate_obstacles(path, grid_width, grid_height, obstacle_chance)
    
    # Combine path and obstacles to get final placeable tiles
    all_blocked = set(path) | set(obstacles)
    placeable_tiles = []
    for x in range(grid_width):
        for y in range(grid_height):
            if (x, y) not in all_blocked:
                placeable_tiles.append((x, y))
    
    return {
        'path': path,
        'placeable_tiles': placeable_tiles,
        'obstacles': obstacles,
        'difficulty': difficulty,
        'path_length': path_length
    }

def generate_path(grid_width, grid_height, length, difficulty):
    """Generate a procedural path from left to right"""
    path = []
    
    # Start position (left side, random Y)
    start_y = random.randint(grid_height // 4, 3 * grid_height // 4)
    current_x, current_y = 0, start_y
    path.append((current_x, current_y))
    
    # Path generation parameters based on difficulty
    max_step = max(1, 3 - difficulty // 30)  # Higher difficulty = smaller steps
    curve_intensity = difficulty / 100  # Higher difficulty = more curves
    
    while current_x < grid_width - 1 and len(path) < length:
        # Determine next position with some randomness
        next_x = min(current_x + 1, grid_width - 1)
        
        # Y movement based on difficulty and current position
        y_change = 0
        
        # Add some curve/zigzag based on difficulty
        if random.random() < curve_intensity:
            # More likely to change direction with higher difficulty
            if random.random() < 0.5:
                y_change = random.randint(-max_step, max_step)
            else:
                # Continue current trend
                if len(path) > 1:
                    prev_y = path[-2][1]
                    trend = current_y - prev_y
                    y_change = max(-max_step, min(max_step, trend + random.randint(-1, 1)))
        
        # Ensure we stay within bounds
        next_y = max(0, min(grid_height - 1, current_y + y_change))
        
        # Add intermediate points for smoother curves
        if abs(next_y - current_y) > 1:
            steps = abs(next_y - current_y)
            for i in range(1, steps):
                intermediate_y = current_y + (next_y - current_y) * i // steps
                path.append((current_x, intermediate_y))
        
        current_x, current_y = next_x, next_y
        path.append((current_x, current_y))
    
    # Ensure path reaches the right edge
    if path[-1][0] < grid_width - 1:
        final_x = grid_width - 1
        final_y = path[-1][1]
        path.append((final_x, final_y))
    
    return path

def generate_obstacles(path, grid_width, grid_height, obstacle_chance):
    """Generate obstacles around the path based on difficulty"""
    obstacles = set()
    path_set = set(path)
    
    # Create obstacle zones around the path
    for x, y in path:
        # Add obstacles near path tiles based on chance
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                obstacle_x, obstacle_y = x + dx, y + dy
                
                # Skip if out of bounds or on path
                if (obstacle_x < 0 or obstacle_x >= grid_width or 
                    obstacle_y < 0 or obstacle_y >= grid_height or
                    (obstacle_x, obstacle_y) in path_set):
                    continue
                
                # Calculate distance from path
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Higher chance of obstacles closer to path
                if distance <= 1:
                    chance = obstacle_chance * 0.8  # High chance near path
                elif distance <= 2:
                    chance = obstacle_chance * 0.4  # Medium chance
                else:
                    chance = obstacle_chance * 0.1  # Low chance far from path
                
                # Add some randomness to make it less predictable
                if random.random() < chance:
                    obstacles.add((obstacle_x, obstacle_y))
    
    # Add some random obstacle clusters for variety
    num_clusters = int(obstacle_chance * 5)  # More clusters with higher difficulty
    for _ in range(num_clusters):
        cluster_x = random.randint(0, grid_width - 1)
        cluster_y = random.randint(0, grid_height - 1)
        
        # Don't place clusters on path
        if (cluster_x, cluster_y) not in path_set:
            cluster_size = random.randint(2, 5)
            for dx in range(-cluster_size, cluster_size + 1):
                for dy in range(-cluster_size, cluster_size + 1):
                    if abs(dx) + abs(dy) <= cluster_size:  # Diamond shape
                        ox, oy = cluster_x + dx, cluster_y + dy
                        if (0 <= ox < grid_width and 0 <= oy < grid_height and
                            (ox, oy) not in path_set):
                            obstacles.add((ox, oy))
    
    return list(obstacles)

def generate_waves_for_difficulty(difficulty, path_length):
    """Generate appropriate waves based on difficulty and path length"""
    base_wave_count = 4 + int(difficulty / 15)  # 4-10 waves
    base_enemy_count = 6 + int(difficulty / 8)  # 6-18 enemies per wave
    
    waves = []
    for wave_num in range(base_wave_count):
        # Increase difficulty with each wave
        wave_difficulty = difficulty + (wave_num * 15)
        
        # Enemy count increases with wave number
        enemy_count = base_enemy_count + (wave_num * 3)
        
        # Enemy type distribution based on difficulty
        if wave_difficulty < 40:
            # Early levels: mostly small enemies, some fast
            enemies = {ENEMY_SMALL: 3, ENEMY_FAST: 1}
        elif wave_difficulty < 70:
            # Mid levels: mix of small, medium, and fast
            enemies = {ENEMY_SMALL: 2, ENEMY_MEDIUM: 1, ENEMY_FAST: 1}
        elif wave_difficulty < 100:
            # Higher levels: more variety, introduce large enemies
            enemies = {ENEMY_SMALL: 1, ENEMY_MEDIUM: 2, ENEMY_LARGE: 1, ENEMY_FAST: 1}
        else:
            # High levels: all enemy types, introduce tanks
            enemies = {ENEMY_SMALL: 1, ENEMY_MEDIUM: 2, ENEMY_LARGE: 1, ENEMY_FAST: 1, ENEMY_TANK: 1}
        
        # Add boss waves every 5 waves
        if (wave_num + 1) % 5 == 0:
            # Boss wave: fewer but stronger enemies
            enemy_count = max(3, enemy_count // 2)
            if wave_difficulty < 60:
                enemies = {ENEMY_MEDIUM: 2, ENEMY_LARGE: 1}
            elif wave_difficulty < 100:
                enemies = {ENEMY_LARGE: 2, ENEMY_TANK: 1}
            else:
                enemies = {ENEMY_LARGE: 1, ENEMY_TANK: 2}
        
        waves.append({
            'count': enemy_count,
            'enemies': enemies
        })
    
    return waves

# Predefined level data - REMOVED: All levels are now procedural
LEVEL_DATA = [] 