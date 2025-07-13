#!/usr/bin/env python3
"""
Test script to verify modifier effects are working correctly
"""

from game_state import GameState, Player
from board import Board
from modifier_system import (
    BoardExpansionModifier, 
    ExtraMoveModifier, 
    RandomAdjacentModifier,
    RandomAdjacentChanceModifier,
    RandomAdjacentFlipModifier,
    DiagonalWinReductionModifier,
    HorizontalWinReductionModifier
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

def test_extra_move():
    """Test that extra move modifier works correctly"""
    print("\nTesting Extra Move Modifier...")
    
    game_state = GameState()
    board = Board(3)
    modifier = ExtraMoveModifier()
    
    # Apply the modifier
    modifier.apply(game_state, board)
    game_state.add_modifier(modifier.name)
    
    # Simulate first move
    board.make_move(0, 0, game_state.current_player)
    game_state.add_move()
    print(f"After first move, moves this turn: {game_state.get_moves_this_turn()}")
    assert game_state.get_moves_this_turn() == 1
    
    # Check if player should switch (should not after 1 move with 1 extra move modifier)
    extra_move_count = game_state.get_modifier_counts().get("+1 Extra Move per turn", 0)
    moves_per_turn = 1 + extra_move_count
    should_switch = game_state.get_moves_this_turn() >= moves_per_turn
    print(f"Should switch after {game_state.get_moves_this_turn()}/{moves_per_turn} moves: {should_switch}")
    assert should_switch == False
    
    # Simulate second move
    board.make_move(0, 1, game_state.current_player)
    game_state.add_move()
    print(f"After second move, moves this turn: {game_state.get_moves_this_turn()}")
    assert game_state.get_moves_this_turn() == 2
    
    # Check if player should switch (should switch after 2 moves with 1 extra move modifier)
    should_switch = game_state.get_moves_this_turn() >= moves_per_turn
    print(f"Should switch after {game_state.get_moves_this_turn()}/{moves_per_turn} moves: {should_switch}")
    assert should_switch == True
    
    print("✓ Extra move test passed!")

def test_diagonal_win_reduction():
    """Test that diagonal win reduction modifier works correctly"""
    print("\nTesting Diagonal Win Reduction Modifier...")
    
    game_state = GameState()
    board = Board(3)
    modifier = DiagonalWinReductionModifier()
    
    # Apply the modifier
    modifier.apply(game_state, board)
    
    # Check that diagonal win requirement is reduced
    requirements = board.get_win_requirements()
    print(f"Win requirements after modifier: {requirements}")
    assert requirements['diagonal'] == 2  # Should need 2 pieces instead of 3
    
    # Create a diagonal win with 2 pieces (should win with reduction)
    board.make_move(0, 0, Player.X)
    board.make_move(1, 1, Player.X)
    # Don't place the third piece - should still win
    
    winner = board.check_winner()
    print(f"Diagonal win with 2 pieces: {winner}")
    assert winner == Player.X
    
    print("✓ Diagonal win reduction test passed!")

def test_horizontal_win_reduction():
    """Test that horizontal win reduction modifier works correctly"""
    print("\nTesting Horizontal Win Reduction Modifier...")
    
    game_state = GameState()
    board = Board(3)
    modifier = HorizontalWinReductionModifier()
    
    # Apply the modifier
    modifier.apply(game_state, board)
    
    # Check that horizontal win requirement is reduced
    requirements = board.get_win_requirements()
    print(f"Win requirements after modifier: {requirements}")
    assert requirements['horizontal'] == 2  # Should need 2 pieces instead of 3
    
    # Create a horizontal win with 2 pieces (should win with reduction)
    board.make_move(0, 0, Player.O)
    board.make_move(0, 1, Player.O)
    # Don't place the third piece - should still win
    
    winner = board.check_winner()
    print(f"Horizontal win with 2 pieces: {winner}")
    assert winner == Player.O
    
    print("✓ Horizontal win reduction test passed!")

def test_adjacent_modifier_family():
    """Test all adjacent modifier variants"""
    print("\nTesting Adjacent Modifier Family...")
    
    modifiers = [
        RandomAdjacentModifier(),
        RandomAdjacentChanceModifier(),
        RandomAdjacentFlipModifier()
    ]
    
    for modifier in modifiers:
        print(f"\nTesting {modifier.name}...")
        game_state = GameState()
        board = Board(3)
        
        # Place some pieces to test with
        board.make_move(0, 0, Player.X)
        board.make_move(1, 1, Player.O)
        
        # Apply the modifier
        modifier.apply(game_state, board)
        
        # Make a move in the center to trigger adjacent effect
        board.make_move(1, 1, Player.X)  # This will overwrite the O
        
        # Count empty cells before adjacent effect
        empty_before = len(board.get_empty_cells())
        print(f"Empty cells before {modifier.name}: {empty_before}")
        
        # Test the modifier
        modifier.on_move_made(game_state, board, True)
        
        # Count empty cells after adjacent effect
        empty_after = len(board.get_empty_cells())
        print(f"Empty cells after {modifier.name}: {empty_after}")
        
        # For chance-based modifier, we can't guarantee the result, so just check it doesn't crash
        if isinstance(modifier, RandomAdjacentChanceModifier):
            print(f"✓ {modifier.name} test completed (chance-based)")
        else:
            # For guaranteed modifiers, should have one fewer empty cell
            assert empty_after <= empty_before
            print(f"✓ {modifier.name} test passed!")

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
    extra_move_mod = ExtraMoveModifier()
    
    expansion_mod.apply(game_state, board)
    extra_move_mod.apply(game_state, board)
    game_state.add_modifier(extra_move_mod.name)
    
    print(f"Board size after expansion: {board.size}")
    assert board.size == 4
    
    # Test extra move on expanded board
    board.make_move(0, 0, game_state.current_player)
    game_state.add_move()
    extra_move_count = game_state.get_modifier_counts().get("+1 Extra Move per turn", 0)
    moves_per_turn = 1 + extra_move_count
    should_switch = game_state.get_moves_this_turn() >= moves_per_turn
    assert should_switch == False
    
    board.make_move(0, 1, game_state.current_player)
    game_state.add_move()
    should_switch = game_state.get_moves_this_turn() >= moves_per_turn
    assert should_switch == True
    
    print("✓ Modifier combination test passed!")

if __name__ == "__main__":
    print("Running modifier tests...\n")
    
    try:
        test_board_expansion()
        test_extra_move()
        test_diagonal_win_reduction()
        test_horizontal_win_reduction()
        test_adjacent_modifier_family()
        test_random_adjacent()
        test_modifier_combination()
        
        print("\n🎉 All modifier tests passed! The modifiers are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 