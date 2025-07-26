from typing import Dict

class Economy:
    def __init__(self, settings: Dict):
        self.settings = settings
        self.money = settings['gameplay']['starting_money']
        self.lives = settings['gameplay']['starting_lives']
        self.max_lives = settings['gameplay']['starting_lives']
    
    def can_afford(self, cost: int) -> bool:
        """Check if player can afford cost"""
        return self.money >= cost
    
    def spend(self, amount: int):
        """Spend money"""
        if self.can_afford(amount):
            self.money -= amount
    
    def add_money(self, amount: int):
        """Add money (from killing enemies)"""
        self.money += amount
    
    def lose_life(self):
        """Lose a life when enemy reaches goal"""
        old_lives = self.lives
        self.lives = max(0, self.lives - 1)
        print(f"ECONOMY: lose_life() called. Lives: {old_lives} -> {self.lives}")
    
    def gain_life(self, amount: int = 1):
        """Gain life (bonus)"""
        self.lives = min(self.max_lives, self.lives + amount)
    
    def reset(self):
        """Reset economy for new level"""
        self.money = self.settings['gameplay']['starting_money']
        self.lives = self.settings['gameplay']['starting_lives']
    
    def update(self, dt: float):
        """Update economy (for future features like passive income)"""
        pass 