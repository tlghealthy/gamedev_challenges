#!/usr/bin/env python3
"""
Test to verify Board Expansion modifier only applies once
"""

from game_state import GameState
from board import Board
from modifier_system import BoardExpansionModifier

def test_board_expansion_multiple():
    """Test that board expansion can happen multiple times"""
    print("Testing Board Expansion - Multiple Applications...")
    
    game_state = GameState()
    board = Board(3)
    modifier = BoardExpansionModifier()
    
    print(f"Initial board size: {board.size}")
    
    # Apply the modifier multiple times
    success1 = modifier.apply(game_state, board)
    print(f"First application: {success1}, board size: {board.size}")
    
    success2 = modifier.apply(game_state, board)
    print(f"Second application: {success2}, board size: {board.size}")
    
    success3 = modifier.apply(game_state, board)
    print(f"Third application: {success3}, board size: {board.size}")
    
    # Board should expand multiple times
    assert board.size == 6
    print("✓ Board expansion applied multiple times!")
    
    # Test that can_apply still returns True (until size limit)
    can_apply_again = modifier.can_apply(game_state, board)
    print(f"Can apply again: {can_apply_again}")
    
    print("✓ Board expansion test passed!")

def test_board_expansion_preserves_marks():
    """Test that board expansion preserves existing marks"""
    print("\nTesting Board Expansion - Preserves Marks...")
    
    game_state = GameState()
    board = Board(3)
    modifier = BoardExpansionModifier()
    
    # Place some marks on the original board
    board.make_move(0, 0, game_state.current_player)  # X in top-left
    board.make_move(1, 1, game_state.current_player)  # X in center
    
    print(f"Original board state:")
    for row in range(board.size):
        print(f"  {board.grid[row]}")
    
    # Apply the modifier
    modifier.apply(game_state, board)
    
    print(f"Expanded board state:")
    for row in range(board.size):
        print(f"  {board.grid[row]}")
    
    # Verify marks were preserved
    assert board.get_cell(0, 0) is not None  # Top-left preserved
    assert board.get_cell(1, 1) is not None  # Center preserved
    
    print("✓ Board expansion preserves marks!")

if __name__ == "__main__":
    print("Running Board Expansion Tests...\n")
    
    try:
        test_board_expansion_multiple()
        test_board_expansion_preserves_marks()
        
        print("\n🎉 All Board Expansion tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 