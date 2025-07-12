#!/usr/bin/env python3
"""
Test script to verify modifier effects are working correctly
"""

from game_state import GameState, Player
from board import Board
from modifier_system import (
    BoardExpansionModifier, 
    DoubleMoveModifier, 
    RandomAdjacentModifier, 
    DiagonalOnlyModifier
)

def test_board_expansion():
    """Test that board expansion works correctly"""
    print("Testing Board Expansion Modifier...")
    
    game_state = GameState()
    board = Board(3)
    modifier = BoardExpansionModifier()
    
    # Place some marks on the original board
    board.make_move(0, 0, Player.X)
    board.make_move(1, 1, Player.O)
    
    print(f"Original board size: {board.size}")
    print(f"Original board state: {board.grid}")
    
    # Apply the modifier
    success = modifier.apply(game_state, board)
    assert success == True
    
    print(f"New board size: {board.size}")
    print(f"New board state: {board.grid}")
    
    # Verify the marks were preserved
    assert board.get_cell(0, 0) == Player.X
    assert board.get_cell(1, 1) == Player.O
    
    print("✓ Board expansion test passed!")

def test_double_move():
    """Test that double move modifier works correctly"""
    print("\nTesting Double Move Modifier...")
    
    game_state = GameState()
    board = Board(3)
    modifier = DoubleMoveModifier()
    
    # Apply the modifier
    modifier.apply(game_state, board)
    
    # Simulate first move
    board.make_move(0, 0, game_state.current_player)
    should_switch = modifier.on_move_made(game_state, board)
    print(f"After first move, should switch: {should_switch}")
    assert should_switch == False
    
    # Simulate second move
    board.make_move(0, 1, game_state.current_player)
    should_switch = modifier.on_move_made(game_state, board)
    print(f"After second move, should switch: {should_switch}")
    assert should_switch == True
    
    print("✓ Double move test passed!")

def test_diagonal_only():
    """Test that diagonal only modifier works correctly"""
    print("\nTesting Diagonal Only Modifier...")
    
    game_state = GameState()
    board = Board(3)
    modifier = DiagonalOnlyModifier()
    
    # Apply the modifier
    modifier.apply(game_state, board)
    
    # Create a horizontal win (should not win with diagonal only)
    board.make_move(0, 0, Player.X)
    board.make_move(0, 1, Player.X)
    board.make_move(0, 2, Player.X)
    
    winner = modifier.check_win_condition(board, Player.X)
    print(f"Horizontal win with diagonal only: {winner}")
    assert winner == False
    
    # Create a diagonal win (should win)
    board.reset()
    board.make_move(0, 0, Player.X)
    board.make_move(1, 1, Player.X)
    board.make_move(2, 2, Player.X)
    
    winner = modifier.check_win_condition(board, Player.X)
    print(f"Diagonal win with diagonal only: {winner}")
    assert winner == True
    
    print("✓ Diagonal only test passed!")

def test_random_adjacent():
    """Test that random adjacent modifier works correctly"""
    print("\nTesting Random Adjacent Modifier...")
    
    game_state = GameState()
    board = Board(3)
    modifier = RandomAdjacentModifier()
    
    # Apply the modifier
    modifier.apply(game_state, board)
    
    # Make a move in the center
    board.make_move(1, 1, game_state.current_player)
    
    # Count empty cells before random adjacent
    empty_before = len(board.get_empty_cells())
    print(f"Empty cells before random adjacent: {empty_before}")
    
    # Apply random adjacent effect
    modifier.on_move_made(game_state, board, True)
    
    # Count empty cells after random adjacent
    empty_after = len(board.get_empty_cells())
    print(f"Empty cells after random adjacent: {empty_after}")
    
    # Should have one fewer empty cell
    assert empty_after == empty_before - 1
    
    print("✓ Random adjacent test passed!")

def test_modifier_combination():
    """Test that multiple modifiers work together"""
    print("\nTesting Modifier Combination...")
    
    game_state = GameState()
    board = Board(3)
    
    # Apply multiple modifiers
    expansion_mod = BoardExpansionModifier()
    double_move_mod = DoubleMoveModifier()
    
    expansion_mod.apply(game_state, board)
    double_move_mod.apply(game_state, board)
    
    print(f"Board size after expansion: {board.size}")
    assert board.size == 4
    
    # Test double move on expanded board
    board.make_move(0, 0, game_state.current_player)
    should_switch = double_move_mod.on_move_made(game_state, board)
    assert should_switch == False
    
    board.make_move(0, 1, game_state.current_player)
    should_switch = double_move_mod.on_move_made(game_state, board)
    assert should_switch == True
    
    print("✓ Modifier combination test passed!")

if __name__ == "__main__":
    print("Running modifier tests...\n")
    
    try:
        test_board_expansion()
        test_double_move()
        test_diagonal_only()
        test_random_adjacent()
        test_modifier_combination()
        
        print("\n🎉 All modifier tests passed! The modifiers are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 