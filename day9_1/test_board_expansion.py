#!/usr/bin/env python3
"""
Test script to verify board expansion functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import TicTacToe

def test_board_expansion():
    """Test that board expansion works correctly"""
    print("Testing board expansion functionality...")
    
    # Create game instance
    game = TicTacToe()
    
    # Check initial board size
    print(f"Initial board size: {game.board_size}")
    print(f"Initial board dimensions: {len(game.board)}x{len(game.board[0])}")
    assert game.board_size == 3, f"Expected board size 3, got {game.board_size}"
    
    # Apply board expansion
    print("\nApplying board expansion...")
    game.apply_modifier('board_expansion')
    
    # Check board size after expansion
    print(f"Board size after expansion: {game.board_size}")
    print(f"Board dimensions after expansion: {len(game.board)}x{len(game.board[0])}")
    assert game.board_size == 4, f"Expected board size 4, got {game.board_size}"
    assert len(game.board) == 4, f"Expected board rows 4, got {len(game.board)}"
    assert len(game.board[0]) == 4, f"Expected board cols 4, got {len(game.board[0])}"
    
    # Check that board expansion is in active modifiers
    assert 'board_expansion' in game.active_modifiers, "Board expansion should be in active modifiers"
    
    print("✓ Board expansion test passed!")
    
    # Test that board expansion doesn't work again (should be limited)
    print("\nTesting that board expansion doesn't work again...")
    old_size = game.board_size
    game.apply_modifier('board_expansion')
    print(f"Board size after second expansion attempt: {game.board_size}")
    
    # The board should not expand again since it's already 4x4
    # Let's check what the condition should be
    print(f"Current board size: {game.board_size}")
    print(f"Condition 'board_size < 5': {game.board_size < 5}")
    
    if game.board_size == old_size:
        print("✓ Board expansion correctly prevented from expanding again")
    else:
        print("✗ Board expansion incorrectly expanded again")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_board_expansion() 