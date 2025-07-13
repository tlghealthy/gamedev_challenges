#!/usr/bin/env python3

from board import Board
from game_state import Player, GameState
from modifier_system import RandomAdjacentFlipModifier

def debug_adjacent_interference():
    """Debug the adjacent modifier interference with win detection"""
    
    print("=== Testing Adjacent Modifier Interference ===")
    
    # Simulate the scenario from the user's log
    board = Board(3)
    game_state = GameState()
    
    # Apply horizontal win reduction
    board.reduce_horizontal_win_requirement(1)
    print(f"Win requirements: {board.get_win_requirements()}")
    
    # Create adjacent modifier
    adjacent_modifier = RandomAdjacentFlipModifier()
    
    print("\n--- Simulating Player X's moves ---")
    
    # Player X places first piece
    board.make_move(0, 0, Player.X)
    print(f"After X's first move: {board.check_winner()}")
    
    # Apply adjacent modifier
    adjacent_modifier.on_move_made(game_state, board, True)
    print(f"After adjacent modifier: {board.check_winner()}")
    
    # Player X places second piece (should win)
    board.make_move(0, 1, Player.X)
    print(f"After X's second move: {board.check_winner()}")
    
    # Apply adjacent modifier again
    adjacent_modifier.on_move_made(game_state, board, True)
    print(f"After adjacent modifier: {board.check_winner()}")
    
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
    
    # Now simulate Player O's move
    print("\n--- Simulating Player O's move ---")
    board.make_move(1, 1, Player.O)
    print(f"After O's move: {board.check_winner()}")
    
    # Apply adjacent modifier for O
    adjacent_modifier.on_move_made(game_state, board, True)
    print(f"After adjacent modifier: {board.check_winner()}")
    
    print("\nFinal board state:")
    for row in range(3):
        row_str = ""
        for col in range(3):
            cell = board.get_cell(row, col)
            if cell is None:
                row_str += "."
            else:
                row_str += cell.value
        print(row_str)

if __name__ == "__main__":
    debug_adjacent_interference() 