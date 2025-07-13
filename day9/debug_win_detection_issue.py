#!/usr/bin/env python3

from board import Board
from game_state import Player

def debug_win_detection_issue():
    """Debug the win detection issue with dynamic win conditions"""
    
    print("=== Testing Win Detection with Dynamic Win Conditions ===")
    
    # Test 1: 3x3 board with horizontal win reduction (need 2 pieces)
    print("\n--- Test 1: 3x3 board, horizontal win reduction to 2 pieces ---")
    board = Board(3)
    board.reduce_horizontal_win_requirement(1)
    
    print(f"Board size: {board.size}")
    print(f"Win requirements: {board.get_win_requirements()}")
    
    # Place 2 pieces in a row (should win)
    board.make_move(0, 0, Player.X)
    board.make_move(0, 1, Player.X)
    
    print("\nBoard state:")
    for row in range(3):
        row_str = ""
        for col in range(3):
            cell = board.get_cell(row, col)
            if cell is None:
                row_str += "."
            else:
                row_str += cell.value
        print(row_str)
    
    # Check for winner
    winner = board.check_winner()
    print(f"Winner: {winner.value if winner else 'None'}")
    
    # Test the specific line checking
    horizontal_line = [board.get_cell(0, col) for col in range(3)]
    print(f"Horizontal line 0: {horizontal_line}")
    required_horizontal = board.size - board.horizontal_win_reduction
    print(f"Required horizontal pieces: {required_horizontal}")
    
    result = board._check_line_with_length(horizontal_line, required_horizontal)
    print(f"_check_line_with_length result: {result}")
    
    # Test 2: 3x3 board with diagonal win reduction (need 2 pieces)
    print("\n--- Test 2: 3x3 board, diagonal win reduction to 2 pieces ---")
    board = Board(3)
    board.reduce_diagonal_win_requirement(1)
    
    print(f"Win requirements: {board.get_win_requirements()}")
    
    # Place 2 pieces on diagonal (should win)
    board.make_move(0, 0, Player.O)
    board.make_move(1, 1, Player.O)
    
    print("\nBoard state:")
    for row in range(3):
        row_str = ""
        for col in range(3):
            cell = board.get_cell(row, col)
            if cell is None:
                row_str += "."
            else:
                row_str += cell.value
        print(row_str)
    
    # Check for winner
    winner = board.check_winner()
    print(f"Winner: {winner.value if winner else 'None'}")
    
    # Test the specific diagonal checking
    diagonal_line = [board.get_cell(i, i) for i in range(3)]
    print(f"Main diagonal: {diagonal_line}")
    required_diagonal = board.size - board.diagonal_win_reduction
    print(f"Required diagonal pieces: {required_diagonal}")
    
    result = board._check_line_with_length(diagonal_line, required_diagonal)
    print(f"_check_line_with_length result: {result}")

if __name__ == "__main__":
    debug_win_detection_issue() 