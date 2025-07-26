#!/usr/bin/env python3
"""
Test script to identify bugs in win condition logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import TicTacToe, Player

def test_basic_win_conditions():
    """Test basic 3x3 win conditions"""
    print("Testing basic 3x3 win conditions...")
    
    game = TicTacToe()
    
    # Test horizontal win
    print("\n1. Testing horizontal win...")
    game.board = [
        [Player.X, Player.X, Player.X],
        [Player.O, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Horizontal win failed: expected {Player.X}, got {winner}"
    
    # Test vertical win
    print("\n2. Testing vertical win...")
    game.board = [
        [Player.O, None, None],
        [Player.O, None, None],
        [Player.O, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"Vertical win failed: expected {Player.O}, got {winner}"
    
    # Test diagonal win (top-left to bottom-right)
    print("\n3. Testing diagonal win (top-left to bottom-right)...")
    game.board = [
        [Player.X, None, None],
        [None, Player.X, None],
        [None, None, Player.X]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Diagonal win failed: expected {Player.X}, got {winner}"
    
    # Test diagonal win (top-right to bottom-left)
    print("\n4. Testing diagonal win (top-right to bottom-left)...")
    game.board = [
        [None, None, Player.O],
        [None, Player.O, None],
        [Player.O, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"Diagonal win failed: expected {Player.O}, got {winner}"
    
    print("✅ All basic win conditions passed!")

def test_win_requirement_modifiers():
    """Test win requirement modifiers"""
    print("\nTesting win requirement modifiers...")
    
    game = TicTacToe()
    
    # Test horizontal reduction
    print("\n1. Testing horizontal reduction...")
    game.win_requirements['horizontal'] = 2
    game.board = [
        [Player.X, Player.X, None],
        [Player.O, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Horizontal reduction failed: expected {Player.X}, got {winner}"
    
    # Test diagonal reduction
    print("\n2. Testing diagonal reduction...")
    game.win_requirements['diagonal'] = 2
    game.board = [
        [Player.O, None, None],
        [None, Player.O, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"Diagonal reduction failed: expected {Player.O}, got {winner}"
    
    print("✅ All win requirement modifier tests passed!")

def test_board_expansion():
    """Test 4x4 board win conditions"""
    print("\nTesting 4x4 board win conditions...")
    
    game = TicTacToe()
    game.board_size = 4
    game.board = [[None]*4 for _ in range(4)]
    
    # Test 4x4 horizontal win
    print("\n1. Testing 4x4 horizontal win...")
    game.board = [
        [Player.X, Player.X, Player.X, Player.X],
        [Player.O, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"4x4 horizontal win failed: expected {Player.X}, got {winner}"
    
    # Test 4x4 diagonal win
    print("\n2. Testing 4x4 diagonal win...")
    game.board = [
        [Player.O, None, None, None],
        [None, Player.O, None, None],
        [None, None, Player.O, None],
        [None, None, None, Player.O]
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"4x4 diagonal win failed: expected {Player.O}, got {winner}"
    
    print("✅ All 4x4 board tests passed!")

def test_edge_cases():
    """Test edge cases and potential bugs"""
    print("\nTesting edge cases...")
    
    game = TicTacToe()
    
    # Test no winner
    print("\n1. Testing no winner...")
    game.board = [
        [Player.X, Player.O, Player.X],
        [Player.O, Player.X, Player.O],
        [Player.O, Player.X, Player.O]
    ]
    winner = game.check_winner()
    print(f"Expected: None, Got: {winner}")
    assert winner is None, f"No winner test failed: expected None, got {winner}"
    
    # Test partial board
    print("\n2. Testing partial board...")
    game.board = [
        [Player.X, None, None],
        [None, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: None, Got: {winner}")
    assert winner is None, f"Partial board test failed: expected None, got {winner}"
    
    # Test mixed board with no win
    print("\n3. Testing mixed board with no win...")
    game.board = [
        [Player.X, Player.O, Player.X],
        [Player.O, Player.X, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    print(f"Expected: None, Got: {winner}")
    assert winner is None, f"Mixed board test failed: expected None, got {winner}"
    
    print("✅ All edge case tests passed!")

def test_consecutive_counting():
    """Test the consecutive counting logic"""
    print("\nTesting consecutive counting logic...")
    
    game = TicTacToe()
    
    # Test consecutive counting
    test_cases = [
        ([Player.X, Player.X, Player.X], 3),
        ([Player.O, Player.O, None], 2),
        ([Player.X, Player.O, Player.X], 1),
        ([None, None, None], 0),
        ([Player.X, None, Player.X], 1),
        ([Player.O, Player.O, Player.O], 3),
    ]
    
    for i, (line, expected) in enumerate(test_cases):
        result = game.count_consecutive(line)
        print(f"Test {i+1}: {line} -> Expected: {expected}, Got: {result}")
        assert result == expected, f"Consecutive counting failed for {line}: expected {expected}, got {result}"
    
    print("✅ All consecutive counting tests passed!")

def test_winning_line_detection():
    """Test winning line detection"""
    print("\nTesting winning line detection...")
    
    game = TicTacToe()
    
    # Test horizontal winning line
    print("\n1. Testing horizontal winning line...")
    game.board = [
        [Player.X, Player.X, Player.X],
        [Player.O, None, None],
        [None, None, None]
    ]
    winning_line = game.get_winning_line()
    expected = [(0, 0), (0, 1), (0, 2)]
    print(f"Expected: {expected}, Got: {winning_line}")
    assert winning_line == expected, f"Horizontal winning line failed: expected {expected}, got {winning_line}"
    
    # Test diagonal winning line
    print("\n2. Testing diagonal winning line...")
    game.board = [
        [Player.O, None, None],
        [None, Player.O, None],
        [None, None, Player.O]
    ]
    winning_line = game.get_winning_line()
    expected = [(0, 0), (1, 1), (2, 2)]
    print(f"Expected: {expected}, Got: {winning_line}")
    assert winning_line == expected, f"Diagonal winning line failed: expected {expected}, got {winning_line}"
    
    print("✅ All winning line detection tests passed!")

def test_potential_bugs():
    """Test for potential bugs in the win condition logic"""
    print("\nTesting for potential bugs...")
    
    game = TicTacToe()
    
    # BUG 1: Check if the logic correctly handles non-consecutive wins
    print("\n1. Testing non-consecutive win detection...")
    game.board = [
        [Player.X, Player.O, Player.X],
        [Player.O, Player.X, Player.O],
        [Player.X, Player.O, Player.X]
    ]
    winner = game.check_winner()
    print(f"Board with no consecutive wins - Expected: None, Got: {winner}")
    # This should return None since there are no consecutive wins
    
    # BUG 2: Test with reduced win requirements on a board that shouldn't win
    print("\n2. Testing reduced requirements edge case...")
    game.win_requirements['horizontal'] = 2
    game.board = [
        [Player.X, Player.O, Player.X],
        [Player.O, Player.X, Player.O],
        [Player.X, Player.O, Player.X]
    ]
    winner = game.check_winner()
    print(f"Board with 2-requirement but no consecutive 2 - Expected: None, Got: {winner}")
    # This should return None since there are no consecutive 2 pieces
    
    # BUG 3: Test the logic with board expansion
    print("\n3. Testing board expansion edge case...")
    game.board_size = 4
    game.board = [[None]*4 for _ in range(4)]
    game.board[0][0] = Player.X
    game.board[1][1] = Player.X
    game.board[2][2] = Player.X
    # Missing the 4th piece for diagonal win
    winner = game.check_winner()
    print(f"4x4 board with 3 diagonal pieces - Expected: None, Got: {winner}")
    
    print("✅ Potential bug tests completed!")

def main():
    """Run all tests"""
    print("=" * 60)
    print("WIN CONDITION BUG TESTING")
    print("=" * 60)
    
    try:
        test_basic_win_conditions()
        test_win_requirement_modifiers()
        test_board_expansion()
        test_edge_cases()
        test_consecutive_counting()
        test_winning_line_detection()
        test_potential_bugs()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! No obvious bugs found.")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 