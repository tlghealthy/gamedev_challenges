from typing import Dict, List
from levels.level_data import LEVEL_DATA, generate_procedural_level, generate_waves_for_difficulty

class LevelLoader:
    def __init__(self, settings: Dict):
        self.settings = settings
        self.levels = LEVEL_DATA
    
    def load_level(self, level_num: int) -> Dict:
        """Load level data by number - all levels are now procedural"""
        return self.generate_procedural_level(level_num)
    
    def generate_procedural_level(self, level_num: int) -> Dict:
        """Generate procedural level for all levels"""
        # Calculate difficulty and path length based on level number
        # Start with moderate difficulty and scale up
        base_difficulty = 25 + (level_num - 1) * 8  # Start at 25, increase by 8 per level
        base_path_length = 35 + (level_num - 1) * 4  # Start at 35, increase by 4 per level
        
        # Add some randomness while keeping similar difficulty
        difficulty = max(15, min(120, base_difficulty + (level_num * 7) % 25 - 12))
        path_length = max(25, min(120, base_path_length + (level_num * 11) % 30 - 15))
        
        # Use level number as seed for reproducible generation
        seed = level_num
        
        # Generate the level
        level_data = generate_procedural_level(
            difficulty=difficulty,
            path_length=path_length,
            grid_width=self.settings['display']['width'] // self.settings['gameplay']['grid_size'],
            grid_height=self.settings['display']['height'] // self.settings['gameplay']['grid_size'],
            seed=seed
        )
        
        # Generate appropriate waves for this difficulty
        level_data['waves'] = generate_waves_for_difficulty(difficulty, path_length)
        
        print(f"Generated procedural level {level_num}: difficulty={difficulty}, path_length={path_length}")
        
        return level_data 