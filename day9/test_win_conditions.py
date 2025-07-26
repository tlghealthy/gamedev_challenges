#!/usr/bin/env python3

import unittest
from board import Board
from game_state import Player

class TestWinConditions(unittest.TestCase):
    """Comprehensive test suite for win conditions"""
    
    def setUp(self):
        """Set up a fresh board for each test"""
        self.board = Board(3)
    
    def test_standard_3x3_no_modifiers(self):
        """Test standard 3x3 tic-tac-toe with no modifiers (need 3 in a row)"""
        print("\n=== Testing Standard 3x3 (3 in a row required) ===")
        
        # Test horizontal win
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.X)
        self.board.make_move(0, 2, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        self.assertEqual(self.board.get_winning_line(), [(0, 0), (0, 1), (0, 2)])
        
        # Reset and test vertical win
        self.board.reset()
        self.board.make_move(0, 0, Player.O)
        self.board.make_move(1, 0, Player.O)
        self.board.make_move(2, 0, Player.O)
        self.assertEqual(self.board.check_winner(), Player.O)
        self.assertEqual(self.board.get_winning_line(), [(0, 0), (1, 0), (2, 0)])
        
        # Reset and test diagonal win
        self.board.reset()
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(1, 1, Player.X)
        self.board.make_move(2, 2, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        self.assertEqual(self.board.get_winning_line(), [(0, 0), (1, 1), (2, 2)])
        
        # Reset and test anti-diagonal win
        self.board.reset()
        self.board.make_move(0, 2, Player.O)
        self.board.make_move(1, 1, Player.O)
        self.board.make_move(2, 0, Player.O)
        self.assertEqual(self.board.check_winner(), Player.O)
        self.assertEqual(self.board.get_winning_line(), [(0, 2), (1, 1), (2, 0)])
        
        # Test no win with 2 in a row
        self.board.reset()
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.X)
        self.assertIsNone(self.board.check_winner())
        self.assertIsNone(self.board.get_winning_line())
    
    def test_3x3_horizontal_reduction(self):
        """Test 3x3 with horizontal win reduction (need 2 in a row horizontally)"""
        print("\n=== Testing 3x3 with Horizontal Win Reduction (2 in a row) ===")
        
        self.board.reduce_horizontal_win_requirement(1)
        self.assertEqual(self.board.get_win_requirements()['horizontal'], 2)
        
        # Test horizontal win with 2 pieces
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        self.assertEqual(self.board.get_winning_line(), [(0, 0), (0, 1)])
        
        # Reset and test horizontal win in middle of row
        self.board.reset()
        self.board.reduce_horizontal_win_requirement(1)
        self.board.make_move(1, 1, Player.O)
        self.board.make_move(1, 2, Player.O)
        self.assertEqual(self.board.check_winner(), Player.O)
        self.assertEqual(self.board.get_winning_line(), [(1, 1), (1, 2)])
        
        # Test vertical still needs 3
        self.board.reset()
        self.board.reduce_horizontal_win_requirement(1)
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(1, 0, Player.X)
        self.assertIsNone(self.board.check_winner())
        
        # Test diagonal still needs 3
        self.board.reset()
        self.board.reduce_horizontal_win_requirement(1)
        self.board.make_move(0, 0, Player.O)
        self.board.make_move(1, 1, Player.O)
        self.assertIsNone(self.board.check_winner())
    
    def test_3x3_vertical_reduction(self):
        """Test 3x3 with vertical win reduction (need 2 in a row vertically)"""
        print("\n=== Testing 3x3 with Vertical Win Reduction (2 in a row) ===")
        
        self.board.reduce_vertical_win_requirement(1)
        self.assertEqual(self.board.get_win_requirements()['vertical'], 2)
        
        # Test vertical win with 2 pieces
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(1, 0, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        self.assertEqual(self.board.get_winning_line(), [(0, 0), (1, 0)])
        
        # Reset and test vertical win in middle of column
        self.board.reset()
        self.board.reduce_vertical_win_requirement(1)
        self.board.make_move(1, 1, Player.O)
        self.board.make_move(2, 1, Player.O)
        self.assertEqual(self.board.check_winner(), Player.O)
        self.assertEqual(self.board.get_winning_line(), [(1, 1), (2, 1)])
        
        # Test horizontal still needs 3
        self.board.reset()
        self.board.reduce_vertical_win_requirement(1)
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.X)
        self.assertIsNone(self.board.check_winner())
    
    def test_3x3_diagonal_reduction(self):
        """Test 3x3 with diagonal win reduction (need 2 in a row diagonally)"""
        print("\n=== Testing 3x3 with Diagonal Win Reduction (2 in a row) ===")
        
        self.board.reduce_diagonal_win_requirement(1)
        self.assertEqual(self.board.get_win_requirements()['diagonal'], 2)
        
        # Test main diagonal win with 2 pieces
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(1, 1, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        self.assertEqual(self.board.get_winning_line(), [(0, 0), (1, 1)])
        
        # Reset and test anti-diagonal win with 2 pieces
        self.board.reset()
        self.board.reduce_diagonal_win_requirement(1)
        self.board.make_move(0, 2, Player.O)
        self.board.make_move(1, 1, Player.O)
        self.assertEqual(self.board.check_winner(), Player.O)
        self.assertEqual(self.board.get_winning_line(), [(0, 2), (1, 1)])
        
        # Test horizontal still needs 3
        self.board.reset()
        self.board.reduce_diagonal_win_requirement(1)
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.X)
        self.assertIsNone(self.board.check_winner())
    
    def test_3x3_multiple_reductions(self):
        """Test 3x3 with multiple win reductions"""
        print("\n=== Testing 3x3 with Multiple Win Reductions ===")
        
        # Reduce both horizontal and diagonal to 2
        self.board.reduce_horizontal_win_requirement(1)
        self.board.reduce_diagonal_win_requirement(1)
        
        # Test horizontal win
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        
        # Reset and test diagonal win
        self.board.reset()
        self.board.reduce_horizontal_win_requirement(1)
        self.board.reduce_diagonal_win_requirement(1)
        self.board.make_move(0, 0, Player.O)
        self.board.make_move(1, 1, Player.O)
        self.assertEqual(self.board.check_winner(), Player.O)
        
        # Test vertical still needs 3
        self.board.reset()
        self.board.reduce_horizontal_win_requirement(1)
        self.board.reduce_diagonal_win_requirement(1)
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(1, 0, Player.X)
        self.assertIsNone(self.board.check_winner())
    
    def test_4x4_board(self):
        """Test 4x4 board with various win conditions"""
        print("\n=== Testing 4x4 Board ===")
        
        self.board = Board(4)
        
        # Test standard 4x4 (need 4 in a row)
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.X)
        self.board.make_move(0, 2, Player.X)
        self.board.make_move(0, 3, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        self.assertEqual(self.board.get_winning_line(), [(0, 0), (0, 1), (0, 2), (0, 3)])
        
        # Reset and test with horizontal reduction to 3
        self.board.reset()
        self.board.reduce_horizontal_win_requirement(1)
        self.board.make_move(1, 0, Player.O)
        self.board.make_move(1, 1, Player.O)
        self.board.make_move(1, 2, Player.O)
        self.assertEqual(self.board.check_winner(), Player.O)
        self.assertEqual(self.board.get_winning_line(), [(1, 0), (1, 1), (1, 2)])
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n=== Testing Edge Cases ===")
        
        # Test minimum win requirement (2 pieces)
        self.board.reduce_horizontal_win_requirement(1)
        self.board.reduce_vertical_win_requirement(1)
        self.board.reduce_diagonal_win_requirement(1)
        
        # Test that 1 piece doesn't win
        self.board.make_move(0, 0, Player.X)
        self.assertIsNone(self.board.check_winner())
        
        # Test that 2 pieces win
        self.board.make_move(0, 1, Player.X)
        self.assertEqual(self.board.check_winner(), Player.X)
        
        # Test mixed players don't win
        self.board.reset()
        self.board.reduce_horizontal_win_requirement(1)
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(0, 1, Player.O)
        self.assertIsNone(self.board.check_winner())
        
        # Test empty board
        self.board.reset()
        self.assertIsNone(self.board.check_winner())
        self.assertIsNone(self.board.get_winning_line())
    
    def test_winning_line_accuracy(self):
        """Test that winning line coordinates are accurate"""
        print("\n=== Testing Winning Line Accuracy ===")
        
        # Test horizontal win in middle of row
        self.board.make_move(1, 0, Player.X)
        self.board.make_move(1, 1, Player.X)
        self.board.make_move(1, 2, Player.X)
        winning_line = self.board.get_winning_line()
        self.assertEqual(winning_line, [(1, 0), (1, 1), (1, 2)])
        
        # Test vertical win in middle of column
        self.board.reset()
        self.board.make_move(0, 1, Player.O)
        self.board.make_move(1, 1, Player.O)
        self.board.make_move(2, 1, Player.O)
        winning_line = self.board.get_winning_line()
        self.assertEqual(winning_line, [(0, 1), (1, 1), (2, 1)])
        
        # Test diagonal win reduction
        self.board.reset()
        self.board.reduce_diagonal_win_requirement(1)
        self.board.make_move(0, 0, Player.X)
        self.board.make_move(1, 1, Player.X)
        winning_line = self.board.get_winning_line()
        self.assertEqual(winning_line, [(0, 0), (1, 1)])

def run_visual_tests():
    """Run visual tests that print board states for manual verification"""
    print("\n" + "="*50)
    print("VISUAL TESTS")
    print("="*50)
    
    # Test 1: 3x3 with horizontal reduction
    print("\n--- Visual Test 1: 3x3 with Horizontal Reduction (2 in a row) ---")
    board = Board(3)
    board.reduce_horizontal_win_requirement(1)
    
    board.make_move(0, 0, Player.X)
    board.make_move(0, 1, Player.X)
    
    print("Board state:")
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
    winning_line = board.get_winning_line()
    print(f"Winner: {winner.value if winner else 'None'}")
    print(f"Winning line: {winning_line}")
    
    # Test 2: 3x3 with diagonal reduction
    print("\n--- Visual Test 2: 3x3 with Diagonal Reduction (2 in a row) ---")
    board = Board(3)
    board.reduce_diagonal_win_requirement(1)
    
    board.make_move(0, 0, Player.O)
    board.make_move(1, 1, Player.O)
    
    print("Board state:")
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
    winning_line = board.get_winning_line()
    print(f"Winner: {winner.value if winner else 'None'}")
    print(f"Winning line: {winning_line}")

if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run visual tests
    run_visual_tests() 