#!/usr/bin/env python3

from board import Board
from game_state import Player, GameState
from modifier_system import ModifierSystem, BoardExpansionModifier, HorizontalWinReductionModifier

def debug_full_scenario():
    """Debug the full scenario from the user's log"""
    
    # Create game state and board
    game_state = GameState()
    board = Board(3)  # Start with 3x3
    modifier_system = ModifierSystem()
    
    print("=== Initial Setup ===")
    print(f"Board size: {board.size}")
    print(f"Win requirements: {board.get_win_requirements()}")
    
    # Simulate the first game (3x3)
    print("\n=== First Game (3x3) ===")
    
    # Player X moves
    board.make_move(0, 0, Player.X)
    board.make_move(0, 1, Player.X)
    board.make_move(0, 2, Player.X)
    
    print("Board after X's moves:")
    for row in range(3):
        row_str = ""
        for col in range(3):
            cell = board.get_cell(row, col)
            if cell is None:
                row_str += "."
            else:
                row_str += cell.value
        print(row_str)
    
    winner = board.check_winner()
    print(f"Winner: {winner.value if winner else 'None'}")
    
    # Simulate board expansion
    print("\n=== Board Expansion ===")
    expansion_modifier = BoardExpansionModifier()
    expansion_modifier.apply(game_state, board)
    modifier_system.active_modifiers.append(expansion_modifier)
    
    print(f"Board size after expansion: {board.size}")
    print(f"Win requirements after expansion: {board.get_win_requirements()}")
    
    # Simulate horizontal win reduction
    print("\n=== Horizontal Win Reduction ===")
    horizontal_modifier = HorizontalWinReductionModifier()
    horizontal_modifier.apply(game_state, board)
    modifier_system.active_modifiers.append(horizontal_modifier)
    
    print(f"Win requirements after horizontal reduction: {board.get_win_requirements()}")
    
    # Now simulate the moves that should create a win
    print("\n=== Testing Win Detection ===")
    
    # Clear the board for the new round
    board.reset()
    
    # Apply the modifiers again (since they're active)
    for modifier in modifier_system.active_modifiers:
        modifier.apply(game_state, board)
    
    print(f"Final board size: {board.size}")
    print(f"Final win requirements: {board.get_win_requirements()}")
    
    # Simulate the moves from the user's log
    # Player X moves (3 in a row horizontally)
    board.make_move(0, 0, Player.X)
    board.make_move(0, 1, Player.X)
    board.make_move(0, 2, Player.X)
    
    print("\nBoard after X's 3 moves:")
    for row in range(4):
        row_str = ""
        for col in range(4):
            cell = board.get_cell(row, col)
            if cell is None:
                row_str += "."
            else:
                row_str += cell.value
        print(row_str)
    
    winner = board.check_winner()
    print(f"Winner: {winner.value if winner else 'None'}")
    
    winning_line = board.get_winning_line()
    print(f"Winning line: {winning_line}")
    
    # Test the specific horizontal line
    horizontal_line = [board.get_cell(0, col) for col in range(4)]
    print(f"Horizontal line 0: {horizontal_line}")
    
    required_horizontal = board.size - board.horizontal_win_reduction
    print(f"Required horizontal pieces: {required_horizontal}")
    
    result = board._check_line_with_length(horizontal_line, required_horizontal)
    print(f"_check_line_with_length result: {result}")

if __name__ == "__main__":
    debug_full_scenario() 