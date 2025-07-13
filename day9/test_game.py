#!/usr/bin/env python3
"""
Simple test script to verify core game functionality
"""

from game_state import GameState, Player, GamePhase
from board import Board
from modifier_system import ModifierSystem, Modifier

def test_game_state():
    """Test game state functionality"""
    print("Testing GameState...")
    
    state = GameState()
    assert state.phase == GamePhase.TITLE
    assert state.current_player == Player.X
    assert state.scores[Player.X] == 0
    assert state.scores[Player.O] == 0
    
    # Test player switching
    state.switch_player()
    assert state.current_player == Player.O
    
    # Test scoring
    state.add_score(Player.X)
    assert state.scores[Player.X] == 1
    assert state.round_winner == Player.X
    
    print("✓ GameState tests passed!")

def test_board():
    """Test board functionality"""
    print("Testing Board...")
    
    board = Board(3)
    assert board.size == 3
    assert board.is_valid_move(0, 0) == True
    assert board.is_valid_move(3, 3) == False  # Out of bounds
    
    # Test making moves
    assert board.make_move(0, 0, Player.X) == True
    assert board.get_cell(0, 0) == Player.X
    assert board.is_valid_move(0, 0) == False  # Cell occupied
    
    # Test win detection
    board.make_move(0, 1, Player.X)
    board.make_move(0, 2, Player.X)
    winner = board.check_winner()
    assert winner == Player.X
    
    print("✓ Board tests passed!")

def test_modifier_system():
    """Test modifier system functionality"""
    print("Testing ModifierSystem...")
    
    system = ModifierSystem()
    
    # Create a test modifier
    class TestModifier(Modifier):
        def __init__(self):
            super().__init__("Test Modifier", "A test modifier", "Test")
        def can_apply(self, game_state, board): return True
        def apply(self, game_state, board): return True
    
    test_mod = TestModifier()
    system.add_modifier(test_mod)
    
    # Test voting
    system.generate_vote_options(1)
    assert len(system.vote_options) == 1
    assert system.vote_options[0].name == "Test Modifier"
    
    system.vote_for_modifier("Test Modifier")
    assert system.votes["Test Modifier"] == 1
    
    winner = system.get_winner()
    assert winner.name == "Test Modifier"
    
    print("✓ ModifierSystem tests passed!")

def test_full_game_flow():
    """Test a complete game flow"""
    print("Testing full game flow...")
    
    state = GameState()
    board = Board(3)
    system = ModifierSystem()
    
    # Simulate a game
    state.phase = GamePhase.PLAYING
    
    # Player X makes a move
    board.make_move(0, 0, Player.X)
    state.switch_player()
    
    # Player O makes a move
    board.make_move(1, 1, Player.O)
    state.switch_player()
    
    # Player X wins
    board.make_move(0, 1, Player.X)
    board.make_move(0, 2, Player.X)
    
    winner = board.check_winner()
    assert winner == Player.X
    
    state.add_score(Player.X)
    assert state.scores[Player.X] == 1
    assert state.phase == GamePhase.ROUND_END
    
    print("✓ Full game flow tests passed!")

if __name__ == "__main__":
    print("Running Tic Tac Toe Evolution tests...\n")
    
    try:
        test_game_state()
        test_board()
        test_modifier_system()
        test_full_game_flow()
        
        print("\n🎉 All tests passed! The game foundation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 