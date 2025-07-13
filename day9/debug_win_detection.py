#!/usr/bin/env python3

from board import Board
from game_state import Player

def debug_win_detection():
    """Debug the win detection issue with 4x4 board and horizontal win reduction"""
    
    # Create a 4x4 board
    board = Board(4)
    
    # Apply horizontal win reduction (should need 3 pieces to win horizontally)
    board.reduce_horizontal_win_requirement(1)
    
    print(f"Board size: {board.size}")
    print(f"Win requirements: {board.get_win_requirements()}")
    
    # Simulate the moves from the user's log
    # Player X moves
    board.make_move(0, 0, Player.X)  # Top-left
    board.make_move(0, 1, Player.X)  # Top-middle-left
    board.make_move(0, 2, Player.X)  # Top-middle-right
    
    print("\nBoard state after X's 3 moves:")
    for row in range(4):
        row_str = ""
        for col in range(4):
            cell = board.get_cell(row, col)
            if cell is None:
                row_str += "."
            else:
                row_str += cell.value
        print(row_str)
    
    # Check for winner
    winner = board.check_winner()
    print(f"\nWinner: {winner.value if winner else 'None'}")
    
    # Check winning line
    winning_line = board.get_winning_line()
    print(f"Winning line: {winning_line}")
    
    # Let's also test the specific line checking logic
    print(f"\nTesting horizontal line 0: {[board.get_cell(0, col) for col in range(4)]}")
    required_horizontal = board.size - board.horizontal_win_reduction
    print(f"Required horizontal pieces: {required_horizontal}")
    
    # Test the _check_line_with_length method directly
    horizontal_line = [board.get_cell(0, col) for col in range(4)]
    result = board._check_line_with_length(horizontal_line, required_horizontal)
    print(f"_check_line_with_length result: {result}")

if __name__ == "__main__":
    debug_win_detection() 