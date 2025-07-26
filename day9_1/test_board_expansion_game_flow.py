#!/usr/bin/env python3
"""
Test script to verify board expansion functionality during actual game flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import TicTacToe, Player, Phase

def test_board_expansion_in_game_flow():
    """Test board expansion during actual game flow"""
    print("Testing board expansion in game flow...")
    
    # Create game instance
    game = TicTacToe()
    
    # Simulate a complete round
    print("Simulating a complete round...")
    
    # Fill the board to trigger voting
    for row in range(game.board_size):
        for col in range(game.board_size):
            if game.board[row][col] is None:
                game.board[row][col] = game.current_player
                game.current_player = Player.O if game.current_player == Player.X else Player.X
    
    print(f"Board filled. Current phase: {game.phase}")
    
    # Force the game to voting phase
    game.phase = Phase.VOTING
    game.generate_vote_options()
    
    print(f"Vote options: {game.vote_options}")
    
    # Check if board_expansion is available
    if 'board_expansion' in game.vote_options:
        print("✓ Board expansion is available as a vote option")
        
        # Simulate selecting board expansion
        print("Simulating selection of board expansion...")
        game.handle_vote_click((0, 0))  # This should apply a random modifier
        
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

def test_board_expansion_availability():
    """Test that board expansion is always available"""
    print("\nTesting board expansion availability...")
    
    # Test multiple games to see if board_expansion appears
    board_expansion_found = False
    
    for i in range(10):
        game = TicTacToe()
        game.phase = Phase.VOTING
        game.generate_vote_options()
        
        if 'board_expansion' in game.vote_options:
            board_expansion_found = True
            print(f"Board expansion found in game {i+1}")
            break
    
    if board_expansion_found:
        print("✓ Board expansion is available in vote options")
    else:
        print("✗ Board expansion was not found in 10 attempts")
    
    print("Test completed!")

if __name__ == "__main__":
    test_board_expansion_in_game_flow()
    test_board_expansion_availability() 