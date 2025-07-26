#!/usr/bin/env python3
"""
Test script to catch win reduction bugs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_correctly_fixed import TicTacToe, Player

def test_horizontal_reduction_bug():
    """Test horizontal win reduction bug"""
    print("Testing horizontal win reduction bug...")
    
    game = TicTacToe()
    
    # Set horizontal win requirement to 2
    game.win_requirements['horizontal'] = 2
    
    # Test case: 2 X's in a row should win
    print("\n1. Testing 2 X's in a row (should win)...")
    game.board = [
        [Player.X, Player.X, None],
        [Player.O, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Horizontal reduction failed: expected {Player.X}, got {winner}"
    
    # Test case: 2 O's in a row should win
    print("\n2. Testing 2 O's in a row (should win)...")
    game.board = [
        [Player.O, Player.O, None],
        [Player.X, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"Horizontal reduction failed: expected {Player.O}, got {winner}"
    
    # Test case: 2 X's in middle row should win
    print("\n3. Testing 2 X's in middle row (should win)...")
    game.board = [
        [None, None, None],
        [Player.X, Player.X, None],
        [Player.O, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Horizontal reduction failed: expected {Player.X}, got {winner}"
    
    print("✅ Horizontal reduction tests completed!")

def test_diagonal_reduction_bug():
    """Test diagonal win reduction bug"""
    print("\nTesting diagonal win reduction bug...")
    
    game = TicTacToe()
    
    # Set diagonal win requirement to 2
    game.win_requirements['diagonal'] = 2
    
    # Test case: 2 X's in diagonal (top-left to bottom-right) should win
    print("\n1. Testing 2 X's in diagonal (should win)...")
    game.board = [
        [Player.X, None, None],
        [None, Player.X, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Diagonal reduction failed: expected {Player.X}, got {winner}"
    
    # Test case: 2 O's in diagonal (top-right to bottom-left) should win
    print("\n2. Testing 2 O's in diagonal (should win)...")
    game.board = [
        [None, None, Player.O],
        [None, Player.O, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"Diagonal reduction failed: expected {Player.O}, got {winner}"
    
    # Test case: 2 X's in diagonal with 3rd piece in different position
    print("\n3. Testing 2 X's in diagonal with 3rd X elsewhere (should win)...")
    game.board = [
        [Player.X, None, None],
        [None, Player.X, None],
        [Player.X, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Diagonal reduction failed: expected {Player.X}, got {winner}"
    
    print("✅ Diagonal reduction tests completed!")

def test_vertical_reduction_bug():
    """Test vertical win reduction bug"""
    print("\nTesting vertical win reduction bug...")
    
    game = TicTacToe()
    
    # Set vertical win requirement to 2
    game.win_requirements['vertical'] = 2
    
    # Test case: 2 X's in column should win
    print("\n1. Testing 2 X's in column (should win)...")
    game.board = [
        [Player.X, None, None],
        [Player.X, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Vertical reduction failed: expected {Player.X}, got {winner}"
    
    # Test case: 2 O's in column should win
    print("\n2. Testing 2 O's in column (should win)...")
    game.board = [
        [None, Player.O, None],
        [None, Player.O, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"Vertical reduction failed: expected {Player.O}, got {winner}"
    
    print("✅ Vertical reduction tests completed!")

def test_edge_cases_with_reduction():
    """Test edge cases with reduced win requirements"""
    print("\nTesting edge cases with reduced win requirements...")
    
    game = TicTacToe()
    
    # Set all requirements to 2
    game.win_requirements = {'horizontal': 2, 'vertical': 2, 'diagonal': 2}
    
    # Test case: Only 1 piece (should not win)
    print("\n1. Testing single piece (should not win)...")
    game.board = [
        [Player.X, None, None],
        [None, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: None, Got: {winner}")
    assert winner is None, f"Single piece should not win: expected None, got {winner}"
    
    # Test case: 2 pieces but not consecutive (should not win)
    print("\n2. Testing non-consecutive pieces (should not win)...")
    game.board = [
        [Player.X, None, Player.X],
        [None, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: None, Got: {winner}")
    assert winner is None, f"Non-consecutive pieces should not win: expected None, got {winner}"
    
    # Test case: Mixed pieces with 2 consecutive (should win)
    print("\n3. Testing mixed board with 2 consecutive (should win)...")
    game.board = [
        [Player.X, Player.X, Player.O],
        [Player.O, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"2 consecutive should win: expected {Player.X}, got {winner}"
    
    print("✅ Edge cases with reduction tests completed!")

def test_4x4_board_with_reduction():
    """Test 4x4 board with reduced win requirements"""
    print("\nTesting 4x4 board with reduced win requirements...")
    
    game = TicTacToe()
    game.board_size = 4
    game.board = [[None]*4 for _ in range(4)]
    
    # Set requirements to 3 (for 4x4 board)
    game.win_requirements = {'horizontal': 3, 'vertical': 3, 'diagonal': 3}
    
    # Test case: 3 X's in a row on 4x4 board
    print("\n1. Testing 3 X's in a row on 4x4 board (should win)...")
    game.board = [
        [Player.X, Player.X, Player.X, None],
        [Player.O, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"3 in a row on 4x4 should win: expected {Player.X}, got {winner}"
    
    # Test case: 3 O's in diagonal on 4x4 board
    print("\n2. Testing 3 O's in diagonal on 4x4 board (should win)...")
    game.board = [
        [Player.O, None, None, None],
        [None, Player.O, None, None],
        [None, None, Player.O, None],
        [None, None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"3 in diagonal on 4x4 should win: expected {Player.O}, got {winner}"
    
    print("✅ 4x4 board with reduction tests completed!")

def main():
    """Run all win reduction bug tests"""
    print("=" * 60)
    print("WIN REDUCTION BUG TESTING")
    print("=" * 60)
    
    try:
        test_horizontal_reduction_bug()
        test_diagonal_reduction_bug()
        test_vertical_reduction_bug()
        test_edge_cases_with_reduction()
        test_4x4_board_with_reduction()
        
        print("\n" + "=" * 60)
        print("🎉 ALL WIN REDUCTION TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("This confirms the win reduction bug exists!")
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 