#!/usr/bin/env python3
"""
Debug script to understand the win detection logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_fixed import TicTacToe, Player

def debug_diagonal_win():
    """Debug the diagonal win detection step by step"""
    print("DEBUGGING DIAGONAL WIN DETECTION")
    print("=" * 50)
    
    game = TicTacToe()
    
    # Set up the problematic board
    game.board = [
        [None, None, Player.O],  # Top-right
        [None, Player.O, None],  # Middle
        [Player.O, None, None]   # Bottom-left
    ]
    
    print("Board setup:")
    for i, row in enumerate(game.board):
        print(f"Row {i}: {row}")
    
    print(f"\nBoard size: {game.board_size}")
    print(f"Win requirements: {game.win_requirements}")
    
    # Check diagonals manually
    diagonal1 = [game.board[i][i] for i in range(game.board_size)]
    diagonal2 = [game.board[i][game.board_size-1-i] for i in range(game.board_size)]
    
    print(f"\nDiagonal 1 (top-left to bottom-right): {diagonal1}")
    print(f"Diagonal 2 (top-right to bottom-left): {diagonal2}")
    
    # Test count_consecutive on each diagonal
    count1 = game.count_consecutive(diagonal1)
    count2 = game.count_consecutive(diagonal2)
    
    print(f"\nConsecutive count for diagonal 1: {count1}")
    print(f"Consecutive count for diagonal 2: {count2}")
    
    # Step through the check_winner function
    print(f"\nStep through check_winner:")
    for player in [Player.X, Player.O]:
        print(f"\nChecking player: {player}")
        
        # Check rows
        for row in range(game.board_size):
            row_consecutive = game.count_consecutive(game.board[row])
            print(f"  Row {row}: {game.board[row]} -> consecutive: {row_consecutive}")
            if row_consecutive >= game.win_requirements['horizontal']:
                print(f"    -> WINNER! {player}")
                return player
        
        # Check columns
        for col in range(game.board_size):
            column = [game.board[row][col] for row in range(game.board_size)]
            col_consecutive = game.count_consecutive(column)
            print(f"  Column {col}: {column} -> consecutive: {col_consecutive}")
            if col_consecutive >= game.win_requirements['vertical']:
                print(f"    -> WINNER! {player}")
                return player
        
        # Check diagonals
        diagonal1 = [game.board[i][i] for i in range(game.board_size)]
        diagonal2 = [game.board[i][game.board_size-1-i] for i in range(game.board_size)]
        
        diag1_consecutive = game.count_consecutive(diagonal1)
        diag2_consecutive = game.count_consecutive(diagonal2)
        
        print(f"  Diagonal 1: {diagonal1} -> consecutive: {diag1_consecutive}")
        print(f"  Diagonal 2: {diagonal2} -> consecutive: {diag2_consecutive}")
        
        if diag1_consecutive >= game.win_requirements['diagonal']:
            print(f"    -> WINNER! {player} (diagonal 1)")
            return player
        if diag2_consecutive >= game.win_requirements['diagonal']:
            print(f"    -> WINNER! {player} (diagonal 2)")
            return player
    
    print("  -> No winner")
    return None

def debug_count_consecutive():
    """Debug the count_consecutive function"""
    print("\n\nDEBUGGING COUNT_CONSECUTIVE FUNCTION")
    print("=" * 50)
    
    game = TicTacToe()
    
    # Test the problematic diagonal
    line = [None, Player.O, None]  # This is diagonal1 for our test case
    
    print(f"Testing line: {line}")
    
    max_count = 0
    current_count = 0
    current_player = None
    
    for i, cell in enumerate(line):
        print(f"\nStep {i}: cell = {cell}")
        print(f"  Before: current_player = {current_player}, current_count = {current_count}, max_count = {max_count}")
        
        if cell is None:
            current_count = 0
            current_player = None
        elif cell == current_player:
            current_count += 1
            max_count = max(max_count, current_count)
        else:
            current_player = cell
            current_count = 1
            max_count = max(max_count, current_count)
        
        print(f"  After: current_player = {current_player}, current_count = {current_count}, max_count = {max_count}")
    
    print(f"\nFinal result: {max_count}")
    
    # Compare with the function result
    function_result = game.count_consecutive(line)
    print(f"Function result: {function_result}")
    print(f"Match: {max_count == function_result}")

def debug_winning_line():
    """Debug the winning line detection"""
    print("\n\nDEBUGGING WINNING LINE DETECTION")
    print("=" * 50)
    
    game = TicTacToe()
    
    # Set up a winning board
    game.board = [
        [None, None, Player.O],  # Top-right
        [None, Player.O, None],  # Middle
        [Player.O, None, None]   # Bottom-left
    ]
    
    print("Board:")
    for i, row in enumerate(game.board):
        print(f"Row {i}: {row}")
    
    winning_line = game.get_winning_line()
    print(f"\nWinning line: {winning_line}")
    
    # Check what the function is actually doing
    for player in [Player.X, Player.O]:
        print(f"\nChecking player: {player}")
        
        # Check diagonals
        diagonal1 = [game.board[i][i] for i in range(game.board_size)]
        diagonal2 = [game.board[i][game.board_size-1-i] for i in range(game.board_size)]
        
        diag1_consecutive = game.count_consecutive(diagonal1)
        diag2_consecutive = game.count_consecutive(diagonal2)
        
        print(f"  Diagonal 1: {diagonal1} -> consecutive: {diag1_consecutive}")
        print(f"  Diagonal 2: {diagonal2} -> consecutive: {diag2_consecutive}")
        
        if diag1_consecutive >= game.win_requirements['diagonal']:
            print(f"    -> Diagonal 1 wins!")
            return [(i, i) for i in range(game.board_size)]
        if diag2_consecutive >= game.win_requirements['diagonal']:
            print(f"    -> Diagonal 2 wins!")
            return [(i, game.board_size-1-i) for i in range(game.board_size)]

def main():
    """Run all debug functions"""
    print("DIAGONAL WIN BUG DEBUGGING")
    print("=" * 60)
    
    # Debug the diagonal win detection
    winner = debug_diagonal_win()
    print(f"\nFinal winner: {winner}")
    
    # Debug the count_consecutive function
    debug_count_consecutive()
    
    # Debug the winning line detection
    debug_winning_line()

if __name__ == "__main__":
    main() 