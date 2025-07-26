#!/usr/bin/env python3

from board import Board
from game_state import Player

def quick_test():
    """Quick test of the most important win conditions"""
    
    print("=== QUICK WIN CONDITION TEST ===")
    
    # Test 1: Standard 3x3
    print("\n1. Standard 3x3 (3 in a row)")
    board = Board(3)
    board.make_move(0, 0, Player.X)
    board.make_move(0, 1, Player.X)
    board.make_move(0, 2, Player.X)
    winner = board.check_winner()
    print(f"   Winner: {winner.value if winner else 'None'} ✓" if winner == Player.X else "   FAILED")
    
    # Test 2: 3x3 with horizontal reduction
    print("\n2. 3x3 with horizontal reduction (2 in a row)")
    board = Board(3)
    board.reduce_horizontal_win_requirement(1)
    board.make_move(0, 0, Player.O)
    board.make_move(0, 1, Player.O)
    winner = board.check_winner()
    print(f"   Winner: {winner.value if winner else 'None'} ✓" if winner == Player.O else "   FAILED")
    
    # Test 3: 3x3 with diagonal reduction
    print("\n3. 3x3 with diagonal reduction (2 in a row)")
    board = Board(3)
    board.reduce_diagonal_win_requirement(1)
    board.make_move(0, 0, Player.X)
    board.make_move(1, 1, Player.X)
    winner = board.check_winner()
    print(f"   Winner: {winner.value if winner else 'None'} ✓" if winner == Player.X else "   FAILED")
    
    # Test 4: 4x4 with horizontal reduction
    print("\n4. 4x4 with horizontal reduction (3 in a row)")
    board = Board(4)
    board.reduce_horizontal_win_requirement(1)
    board.make_move(0, 0, Player.O)
    board.make_move(0, 1, Player.O)
    board.make_move(0, 2, Player.O)
    winner = board.check_winner()
    print(f"   Winner: {winner.value if winner else 'None'} ✓" if winner == Player.O else "   FAILED")
    
    # Test 5: No win with insufficient pieces
    print("\n5. No win with insufficient pieces")
    board = Board(3)
    board.reduce_horizontal_win_requirement(1)
    board.make_move(0, 0, Player.X)
    winner = board.check_winner()
    print(f"   Winner: {winner.value if winner else 'None'} ✓" if winner is None else "   FAILED")
    
    print("\n=== ALL TESTS COMPLETE ===")

if __name__ == "__main__":
    quick_test() 