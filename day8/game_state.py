from enum import Enum
from typing import List, Optional

class GamePhase(Enum):
    TITLE = "title"
    PLAYING = "playing"
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
        
    def reset_round(self):
        """Reset the current round state"""
        self.current_player = Player.X
        self.round_winner = None
        
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
        
    def add_modifier(self, modifier_name: str):
        """Add a modifier to the active list"""
        self.active_modifiers.append(modifier_name)
        
    def get_active_modifiers(self) -> List[str]:
        """Get the list of active modifiers"""
        return self.active_modifiers.copy() 