#!/usr/bin/env python3
"""
Test script to verify the fixed board expansion functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_fixed_voting import TicTacToe, Player, Phase

def test_fixed_board_expansion():
    """Test that the fixed version correctly handles board expansion"""
    print("Testing fixed board expansion functionality...")
    
    # Create game instance
    game = TicTacToe()
    
    # Check initial board size
    print(f"Initial board size: {game.board_size}")
    assert game.board_size == 3, f"Expected board size 3, got {game.board_size}"
    
    # Simulate a complete round to get to voting
    print("\nSimulating a complete round...")
    
    # Fill the board to trigger voting
    for row in range(game.board_size):
        for col in range(game.board_size):
            if game.board[row][col] is None:
                game.board[row][col] = game.current_player
                game.current_player = Player.O if game.current_player == Player.X else Player.X
    
    # Force the game to voting phase
    game.phase = Phase.VOTING
    game.generate_vote_options()
    
    print(f"Vote options: {game.vote_options}")
    
    # Check if board_expansion is available
    if 'board_expansion' in game.vote_options:
        print("✓ Board expansion is available as a vote option")
        
        # Simulate clicking on board expansion (first option)
        print("Simulating click on board expansion...")
        click_pos = (400, 170)  # Click in the first modifier box
        game.handle_vote_click(click_pos)
        
        print(f"Active modifiers after voting: {game.active_modifiers}")
        print(f"Board size after voting: {game.board_size}")
        
        if 'board_expansion' in game.active_modifiers:
            print("✓ Board expansion was applied")
            if game.board_size == 4:
                print("✓ Board was expanded to 4x4")
            else:
                print(f"✗ Board size is {game.board_size}, expected 4")
        else:
            print("✗ Board expansion was not applied")
    else:
        print("✗ Board expansion is not available as a vote option")
    
    print("\nTest completed!")

def test_board_expansion_limit():
    """Test that board expansion is limited to 4x4"""
    print("\nTesting board expansion limit...")
    
    game = TicTacToe()
    
    # Apply board expansion
    game.apply_modifier('board_expansion')
    print(f"Board size after first expansion: {game.board_size}")
    
    # Try to apply board expansion again
    old_size = game.board_size
    game.apply_modifier('board_expansion')
    print(f"Board size after second expansion attempt: {game.board_size}")
    
    if game.board_size == old_size:
        print("✓ Board expansion correctly limited to 4x4")
    else:
        print(f"✗ Board expansion incorrectly expanded to {game.board_size}x{game.board_size}")
    
    print("Test completed!")

if __name__ == "__main__":
    test_fixed_board_expansion()
    test_board_expansion_limit() 