from enum import Enum
from typing import List, Optional, Dict, Tuple

class GamePhase(Enum):
    TITLE = "title"
    PLAYING = "playing"
    WINNING_DISPLAY = "winning_display"  # New phase to show winning state
    ROUND_END = "round_end"
    MODIFIER_VOTE = "modifier_vote"
    GAME_END = "game_end"

class Player(Enum):
    X = "X"
    O = "O"

class GameState:
    def __init__(self):
        self.phase = GamePhase.TITLE
        self.current_player = Player.X
        self.scores = {Player.X: 0, Player.O: 0}
        self.current_round = 1
        self.round_winner: Optional[Player] = None
        self.game_winner: Optional[Player] = None
        self.active_modifiers: List[str] = []  # Will store modifier names
        self.moves_this_turn = 0  # Track moves for extra move modifiers
        self.winning_line: Optional[List[Tuple[int, int]]] = None  # Track winning combination
        self.winning_display_start_time: Optional[float] = None  # Track when winning display started
        
    def reset_round(self):
        """Reset the current round state"""
        self.current_player = Player.X
        self.round_winner = None
        self.moves_this_turn = 0
        self.winning_line = None
        self.winning_display_start_time = None
        
    def next_round(self):
        """Move to the next round"""
        self.current_round += 1
        self.reset_round()
        
    def add_score(self, player: Player):
        """Add a point to the specified player"""
        self.scores[player] += 1
        self.round_winner = player
        
        # Check if game is won
        if self.scores[player] >= 6:  # Best of 10 (6 wins)
            self.game_winner = player
            self.phase = GamePhase.GAME_END
        elif self.current_round >= 10:
            # Game ended in tie, determine winner
            if self.scores[Player.X] > self.scores[Player.O]:
                self.game_winner = Player.X
            elif self.scores[Player.O] > self.scores[Player.X]:
                self.game_winner = Player.O
            else:
                self.game_winner = None  # Tie
            self.phase = GamePhase.GAME_END
        else:
            self.phase = GamePhase.ROUND_END
            
    def switch_player(self):
        """Switch to the other player"""
        self.current_player = Player.O if self.current_player == Player.X else Player.X
        self.moves_this_turn = 0  # Reset move counter when switching players
        
    def add_modifier(self, modifier_name: str):
        """Add a modifier to the active list"""
        self.active_modifiers.append(modifier_name)
        
    def add_move(self):
        """Increment the move counter for the current player"""
        self.moves_this_turn += 1
        
    def get_active_modifiers(self) -> List[str]:
        """Get the list of active modifiers"""
        return self.active_modifiers.copy()
        
    def get_modifier_counts(self) -> Dict[str, int]:
        """Get a dictionary of modifier names and their counts"""
        counts = {}
        for modifier in self.active_modifiers:
            counts[modifier] = counts.get(modifier, 0) + 1
        return counts
        
    def get_moves_this_turn(self) -> int:
        """Get the number of moves made this turn"""
        return self.moves_this_turn 