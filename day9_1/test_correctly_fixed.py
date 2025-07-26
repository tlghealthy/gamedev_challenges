#!/usr/bin/env python3
"""
Test script to verify the correctly fixed version resolves all win condition bugs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the correctly fixed version
from game_correctly_fixed import TicTacToe, Player

def test_correctly_fixed_diagonal_win():
    """Test that the diagonal win bug is correctly fixed"""
    print("Testing correctly fixed diagonal win detection...")
    
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
    
    print("✅ Correctly fixed diagonal win detection works!")

def test_count_consecutive_for_player():
    """Test the new count_consecutive_for_player function"""
    print("\nTesting count_consecutive_for_player function...")
    
    game = TicTacToe()
    
    # Test various scenarios
    test_cases = [
        # (line, player, expected)
        ([Player.X, Player.X, Player.X], Player.X, 3),
        ([Player.O, Player.O, Player.O], Player.O, 3),
        ([Player.X, Player.X, Player.X], Player.O, 0),  # Wrong player
        ([Player.O, Player.O, Player.O], Player.X, 0),  # Wrong player
        ([Player.X, Player.O, Player.X], Player.X, 1),
        ([Player.X, Player.O, Player.X], Player.O, 1),
        ([None, Player.X, Player.X], Player.X, 2),
        ([Player.X, Player.X, None], Player.X, 2),
        ([None, None, Player.O], Player.O, 1),
        ([Player.O, None, None], Player.O, 1),
        ([None, None, None], Player.X, 0),
        ([None, None, None], Player.O, 0),
    ]
    
    for i, (line, player, expected) in enumerate(test_cases):
        result = game.count_consecutive_for_player(line, player)
        print(f"Test {i+1}: {line} for {player} -> Expected: {expected}, Got: {result}")
        assert result == expected, f"count_consecutive_for_player failed: expected {expected}, got {result}"
    
    print("✅ count_consecutive_for_player works correctly!")

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

def test_edge_cases():
    """Test edge cases that might cause issues"""
    print("\nTesting edge cases...")
    
    game = TicTacToe()
    
    # Test with mixed pieces but no consecutive wins
    print("\n1. Testing mixed pieces...")
    game.board = [
        [Player.X, Player.O, Player.X],
        [Player.O, Player.X, Player.O],
        [Player.X, Player.O, Player.X]
    ]
    winner = game.check_winner()
    assert winner is None, "Should be no winner with mixed pieces"
    
    # Test with only one piece
    print("2. Testing single piece...")
    game.board = [
        [Player.X, None, None],
        [None, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    assert winner is None, "Should be no winner with single piece"
    
    # Test with two pieces but not consecutive
    print("3. Testing non-consecutive pieces...")
    game.board = [
        [Player.O, None, Player.O],
        [None, None, None],
        [None, None, None]
    ]
    winner = game.check_winner()
    assert winner is None, "Should be no winner with non-consecutive pieces"
    
    print("✅ Edge cases work correctly!")

def main():
    """Run all tests for the correctly fixed version"""
    print("=" * 60)
    print("CORRECTLY FIXED VERSION WIN CONDITION TESTING")
    print("=" * 60)
    
    try:
        test_correctly_fixed_diagonal_win()
        test_count_consecutive_for_player()
        test_all_win_patterns()
        test_no_winner_cases()
        test_win_requirements()
        test_winning_line_detection()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! The bugs have been correctly fixed.")
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