#!/usr/bin/env python3

from board import Board
from game_state import Player, GameState
from modifier_system import HorizontalWinReductionModifier, DiagonalWinReductionModifier

def test_win_reduction_fix():
    """Test that win reduction modifiers can only be applied once per instance"""
    
    print("=== Testing Win Reduction Modifier Fix ===")
    
    # Test 1: 3x3 board with horizontal win reduction
    print("\n--- Test 1: 3x3 board with horizontal win reduction ---")
    board = Board(3)
    game_state = GameState()
    modifier = HorizontalWinReductionModifier()
    
    print(f"Initial win requirements: {board.get_win_requirements()}")
    print(f"Can apply: {modifier.can_apply(game_state, board)}")
    
    # Apply the modifier
    modifier.apply(game_state, board)
    print(f"After applying: {board.get_win_requirements()}")
    print(f"Can apply again: {modifier.can_apply(game_state, board)}")
    
    # Try to apply again (should not work)
    modifier.apply(game_state, board)
    print(f"After trying to apply again: {board.get_win_requirements()}")
    
    # Test 2: 4x4 board with diagonal win reduction
    print("\n--- Test 2: 4x4 board with diagonal win reduction ---")
    board = Board(4)
    modifier = DiagonalWinReductionModifier()
    
    print(f"Initial win requirements: {board.get_win_requirements()}")
    print(f"Can apply: {modifier.can_apply(game_state, board)}")
    
    # Apply the modifier
    modifier.apply(game_state, board)
    print(f"After applying: {board.get_win_requirements()}")
    print(f"Can apply again: {modifier.can_apply(game_state, board)}")
    
    # Test 3: Multiple instances of the same modifier
    print("\n--- Test 3: Multiple instances of horizontal win reduction ---")
    board = Board(4)
    modifier1 = HorizontalWinReductionModifier()
    modifier2 = HorizontalWinReductionModifier()
    
    print(f"Initial win requirements: {board.get_win_requirements()}")
    
    # Apply first modifier
    modifier1.apply(game_state, board)
    print(f"After first modifier: {board.get_win_requirements()}")
    print(f"First modifier can apply again: {modifier1.can_apply(game_state, board)}")
    print(f"Second modifier can apply: {modifier2.can_apply(game_state, board)}")
    
    # Apply second modifier
    modifier2.apply(game_state, board)
    print(f"After second modifier: {board.get_win_requirements()}")
    print(f"Second modifier can apply again: {modifier2.can_apply(game_state, board)}")

if __name__ == "__main__":
    test_win_reduction_fix() 