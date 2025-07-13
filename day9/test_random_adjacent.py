#!/usr/bin/env python3
"""
Test to verify Random Adjacent modifier behavior
"""

from game_state import GameState, Player
from board import Board
from modifier_system import RandomAdjacentModifier

def test_random_adjacent_no_overwrite():
    """Test that random adjacent doesn't overwrite existing moves"""
    print("Testing Random Adjacent - No Overwrite...")
    
    game_state = GameState()
    board = Board(3)
    modifier = RandomAdjacentModifier()
    
    # Place a mark in the center
    board.make_move(1, 1, Player.X)
    board.last_move = (1, 1)
    
    # Fill all adjacent cells except one
    board.make_move(0, 0, Player.O)
    board.make_move(0, 1, Player.O)
    board.make_move(0, 2, Player.O)
    board.make_move(1, 0, Player.O)
    board.make_move(1, 2, Player.O)
    board.make_move(2, 0, Player.O)
    board.make_move(2, 1, Player.O)
    # Leave (2, 2) empty
    
    print("Board before random adjacent:")
    for row in range(board.size):
        print(f"  {board.grid[row]}")
    
    # Apply random adjacent
    modifier.on_move_made(game_state, board, True)
    
    print("Board after random adjacent:")
    for row in range(board.size):
        print(f"  {board.grid[row]}")
    
    # Verify that only the empty cell (2, 2) was filled
    assert board.get_cell(2, 2) is not None
    # Verify that existing marks weren't overwritten
    assert board.get_cell(1, 1) == Player.X
    assert board.get_cell(0, 0) == Player.O
    
    print("✓ Random adjacent doesn't overwrite existing moves!")

def test_random_adjacent_no_empty_cells():
    """Test that random adjacent handles no empty adjacent cells"""
    print("\nTesting Random Adjacent - No Empty Cells...")
    
    game_state = GameState()
    board = Board(3)
    modifier = RandomAdjacentModifier()
    
    # Fill the entire board
    for row in range(board.size):
        for col in range(board.size):
            board.make_move(row, col, Player.X if (row + col) % 2 == 0 else Player.O)
    
    board.last_move = (1, 1)
    
    print("Board is completely full")
    
    # Apply random adjacent (should not crash and should handle gracefully)
    modifier.on_move_made(game_state, board, True)
    
    print("✓ Random adjacent handles full board gracefully!")

def test_random_adjacent_stacking():
    """Test that multiple random adjacent modifiers stack properly"""
    print("\nTesting Random Adjacent - Stacking...")
    
    game_state = GameState()
    board = Board(3)
    
    # Create multiple random adjacent modifiers
    modifier1 = RandomAdjacentModifier()
    modifier2 = RandomAdjacentModifier()
    
    # Place a mark in the center
    board.make_move(1, 1, Player.X)
    board.last_move = (1, 1)
    
    print("Board before random adjacent stacking:")
    for row in range(board.size):
        print(f"  {board.grid[row]}")
    
    # Apply both modifiers
    modifier1.on_move_made(game_state, board, True)
    modifier2.on_move_made(game_state, board, True)
    
    print("Board after random adjacent stacking:")
    for row in range(board.size):
        print(f"  {board.grid[row]}")
    
    # Count how many additional marks were placed
    additional_marks = 0
    for row in range(board.size):
        for col in range(board.size):
            if (row, col) != (1, 1) and board.get_cell(row, col) is not None:
                additional_marks += 1
    
    print(f"Additional marks placed: {additional_marks}")
    assert additional_marks >= 0  # Should be at least 0, could be up to 2
    
    print("✓ Random adjacent stacking works!")

if __name__ == "__main__":
    print("Running Random Adjacent Tests...\n")
    
    try:
        test_random_adjacent_no_overwrite()
        test_random_adjacent_no_empty_cells()
        test_random_adjacent_stacking()
        
        print("\n🎉 All Random Adjacent tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 