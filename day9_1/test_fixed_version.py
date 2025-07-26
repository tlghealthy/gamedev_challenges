#!/usr/bin/env python3
"""
Test script to verify the fixed version resolves win condition bugs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed version
from game_fixed import TicTacToe, Player

def test_fixed_diagonal_win():
    """Test that the diagonal win bug is fixed"""
    print("Testing fixed diagonal win detection...")
    
    game = TicTacToe()
    
    # Test the problematic case that failed before
    print("\n1. Testing top-right to bottom-left diagonal...")
    game.board = [
        [None, None, Player.O],  # Top-right
        [None, Player.O, None],  # Middle
        [Player.O, None, None]   # Bottom-left
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.O}, Got: {winner}")
    assert winner == Player.O, f"Diagonal win still broken: expected {Player.O}, got {winner}"
    
    # Test the other diagonal
    print("\n2. Testing top-left to bottom-right diagonal...")
    game.board = [
        [Player.X, None, None],  # Top-left
        [None, Player.X, None],  # Middle
        [None, None, Player.X]   # Bottom-right
    ]
    winner = game.check_winner()
    print(f"Expected: {Player.X}, Got: {winner}")
    assert winner == Player.X, f"Diagonal win broken: expected {Player.X}, got {winner}"
    
    print("✅ Fixed diagonal win detection works correctly!")

def test_fixed_consecutive_counting():
    """Test the improved consecutive counting logic"""
    print("\nTesting fixed consecutive counting...")
    
    game = TicTacToe()
    
    # Test edge cases that might have been problematic
    test_cases = [
        ([None, Player.X, Player.X], 2),  # Starts with None
        ([Player.O, None, Player.O], 1),  # Middle is None
        ([Player.X, Player.X, None], 2),  # Ends with None
        ([None, None, Player.O], 1),      # Multiple None at start
        ([Player.X, None, None], 1),      # Multiple None at end
    ]
    
    for i, (line, expected) in enumerate(test_cases):
        result = game.count_consecutive(line)
        print(f"Test {i+1}: {line} -> Expected: {expected}, Got: {result}")
        assert result == expected, f"Consecutive counting failed for {line}: expected {expected}, got {result}"
    
    print("✅ Fixed consecutive counting works correctly!")

def test_all_win_patterns():
    """Test all possible win patterns"""
    print("\nTesting all win patterns...")
    
    game = TicTacToe()
    
    # Test horizontal wins
    print("\n1. Testing horizontal wins...")
    for row in range(3):
        game.board = [[None]*3 for _ in range(3)]
        game.board[row] = [Player.X, Player.X, Player.X]
        winner = game.check_winner()
        assert winner == Player.X, f"Horizontal win on row {row} failed"
    
    # Test vertical wins
    print("2. Testing vertical wins...")
    for col in range(3):
        game.board = [[None]*3 for _ in range(3)]
        for row in range(3):
            game.board[row][col] = Player.O
        winner = game.check_winner()
        assert winner == Player.O, f"Vertical win on column {col} failed"
    
    # Test diagonal wins
    print("3. Testing diagonal wins...")
    # Top-left to bottom-right
    game.board = [
        [Player.X, None, None],
        [None, Player.X, None],
        [None, None, Player.X]
    ]
    winner = game.check_winner()
    assert winner == Player.X, "Diagonal win (top-left to bottom-right) failed"
    
    # Top-right to bottom-left
    game.board = [
        [None, None, Player.O],
        [None, Player.O, None],
        [Player.O, None, None]
    ]
    winner = game.check_winner()
    assert winner == Player.O, "Diagonal win (top-right to bottom-left) failed"
    
    print("✅ All win patterns work correctly!")

def test_no_winner_cases():
    """Test cases where there should be no winner"""
    print("\nTesting no winner cases...")
    
    game = TicTacToe()
    
    # Test full board with no winner
    print("\n1. Testing full board with no winner...")
    game.board = [
        [Player.X, Player.O, Player.X],
        [Player.O, Player.X, Player.O],
        [Player.O, Player.X, Player.O]
    ]
    winner = game.check_winner()
    assert winner is None, "Should be no winner on full board"
    
    # Test partial board with no winner
    print("2. Testing partial board with no winner...")
    game.board = [
        [Player.X, Player.O, None],
        [None, Player.X, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    assert winner is None, "Should be no winner on partial board"
    
    # Test scattered pieces
    print("3. Testing scattered pieces...")
    game.board = [
        [Player.X, None, Player.O],
        [None, Player.X, None],
        [Player.O, None, Player.X]
    ]
    winner = game.check_winner()
    assert winner is None, "Should be no winner with scattered pieces"
    
    print("✅ No winner cases work correctly!")

def test_win_requirements():
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
    assert winner == Player.X, "Horizontal reduction failed"
    
    # Test diagonal reduction
    print("2. Testing diagonal reduction...")
    game.win_requirements['diagonal'] = 2
    game.board = [
        [Player.O, None, None],
        [None, Player.O, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    assert winner == Player.O, "Diagonal reduction failed"
    
    # Reset requirements
    game.win_requirements = {'horizontal': 3, 'vertical': 3, 'diagonal': 3}
    
    print("✅ Win requirement modifiers work correctly!")

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
    assert winning_line == expected, f"Horizontal winning line failed: expected {expected}, got {winning_line}"
    
    # Test diagonal winning line
    print("2. Testing diagonal winning line...")
    game.board = [
        [None, None, Player.O],
        [None, Player.O, None],
        [Player.O, None, None]
    ]
    winning_line = game.get_winning_line()
    expected = [(0, 2), (1, 1), (2, 0)]
    assert winning_line == expected, f"Diagonal winning line failed: expected {expected}, got {winning_line}"
    
    print("✅ Winning line detection works correctly!")

def main():
    """Run all tests for the fixed version"""
    print("=" * 60)
    print("FIXED VERSION WIN CONDITION TESTING")
    print("=" * 60)
    
    try:
        test_fixed_diagonal_win()
        test_fixed_consecutive_counting()
        test_all_win_patterns()
        test_no_winner_cases()
        test_win_requirements()
        test_winning_line_detection()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! The bugs have been fixed.")
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