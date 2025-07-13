#!/usr/bin/env python3
"""
Example: How to add a new modifier to Tic Tac Toe Evolution

This script demonstrates the extensibility of the modifier system
by creating a custom modifier that changes the win condition.
"""

from modifier_system import Modifier
from game_state import GameState
from board import Board

class CornerWinModifier(Modifier):
    """
    A custom modifier that changes the win condition.
    Players must place their marks in all four corners to win.
    """
    
    def __init__(self):
        super().__init__(
            "Corner Win",
            "Win by placing your marks in all four corners of the board",
            "Win Condition"
        )
        
    def can_apply(self, game_state, board):
        """Check if this modifier can be applied"""
        # Can be applied to any 3x3 or larger board
        return board.size >= 3
        
    def apply(self, game_state, board):
        """Apply the modifier effect"""
        # This modifier changes the win condition, so we need to
        # override the board's check_winner method or add a flag
        # For this example, we'll just return True to indicate success
        print(f"Applied {self.name}: {self.description}")
        return True
        
    def check_corner_win(self, board, player):
        """
        Custom win condition: check if player has marks in all four corners
        """
        if board.size < 3:
            return False
            
        corners = [
            (0, 0),  # Top-left
            (0, board.size - 1),  # Top-right
            (board.size - 1, 0),  # Bottom-left
            (board.size - 1, board.size - 1)  # Bottom-right
        ]
        
        return all(board.get_cell(row, col) == player for row, col in corners)

class ReverseWinModifier(Modifier):
    """
    Another example modifier that reverses the normal win condition.
    Players must avoid getting three in a row to win.
    """
    
    def __init__(self):
        super().__init__(
            "Reverse Win",
            "Avoid getting three in a row - the first to get three in a row loses!",
            "Win Condition"
        )
        
    def can_apply(self, game_state, board):
        return True
        
    def apply(self, game_state, board):
        print(f"Applied {self.name}: {self.description}")
        return True

def demonstrate_modifier_usage():
    """Demonstrate how to use the custom modifiers"""
    print("=== Custom Modifier Example ===\n")
    
    # Create game components
    game_state = GameState()
    board = Board(3)
    
    # Create and test the corner win modifier
    corner_mod = CornerWinModifier()
    print(f"Modifier: {corner_mod.name}")
    print(f"Description: {corner_mod.description}")
    print(f"Category: {corner_mod.category}")
    print(f"Can apply: {corner_mod.can_apply(game_state, board)}")
    
    # Test the corner win condition
    print("\nTesting corner win condition...")
    
    # Place marks in three corners (should not win)
    board.make_move(0, 0, game_state.current_player)  # Top-left
    board.make_move(0, 2, game_state.current_player)  # Top-right
    board.make_move(2, 0, game_state.current_player)  # Bottom-left
    
    has_corner_win = corner_mod.check_corner_win(board, game_state.current_player)
    print(f"Has marks in 3 corners: {has_corner_win}")
    
    # Place mark in fourth corner (should win)
    board.make_move(2, 2, game_state.current_player)  # Bottom-right
    
    has_corner_win = corner_mod.check_corner_win(board, game_state.current_player)
    print(f"Has marks in all 4 corners: {has_corner_win}")
    
    print("\n=== Integration Instructions ===")
    print("To add this modifier to the game:")
    print("1. Add the modifier class to modifier_system.py")
    print("2. Import and instantiate it in game.py")
    print("3. Add it to the modifier pool in _initialize_modifiers()")
    print("4. Update the win detection logic to check for custom win conditions")

if __name__ == "__main__":
    demonstrate_modifier_usage() 