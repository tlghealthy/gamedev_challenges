from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import random
from board import Board

class Modifier(ABC):
    """Base class for all game modifiers"""
    
    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category
        
    @abstractmethod
    def apply(self, game_state, board) -> bool:
        """Apply the modifier effect. Return True if successful."""
        pass
        
    @abstractmethod
    def can_apply(self, game_state, board) -> bool:
        """Check if this modifier can be applied"""
        pass

class ModifierSystem:
    def __init__(self):
        self.available_modifiers: List[Modifier] = []
        self.active_modifiers: List[Modifier] = []
        self.vote_options: List[Modifier] = []
        self.votes: Dict[str, int] = {}  # modifier_name -> vote_count
        
    def add_modifier(self, modifier: Modifier):
        """Add a modifier to the available pool"""
        self.available_modifiers.append(modifier)
        
    def generate_vote_options(self, count: int = 3) -> List[Modifier]:
        """Generate random modifier options for voting"""
        if len(self.available_modifiers) < count:
            return self.available_modifiers.copy()
            
        self.vote_options = random.sample(self.available_modifiers, count)
        self.votes = {mod.name: 0 for mod in self.vote_options}
        return self.vote_options
        
    def vote_for_modifier(self, modifier_name: str):
        """Vote for a specific modifier"""
        if modifier_name in self.votes:
            self.votes[modifier_name] += 1
            
    def get_winner(self) -> Optional[Modifier]:
        """Get the modifier with the most votes, or random if tied"""
        if not self.vote_options:
            return None
            
        max_votes = max(self.votes.values())
        winners = [mod for mod in self.vote_options if self.votes[mod.name] == max_votes]
        
        if len(winners) == 1:
            return winners[0]
        elif len(winners) > 1:
            # Tie - randomly select one
            return random.choice(winners)
        else:
            return None
            
    def apply_winner(self, game_state, board) -> bool:
        """Apply the winning modifier"""
        winner = self.get_winner()
        if winner and winner.can_apply(game_state, board):
            success = winner.apply(game_state, board)
            if success:
                self.active_modifiers.append(winner)
                game_state.add_modifier(winner.name)
            return success
        return False
        
    def apply_all_active_modifiers(self, game_state, board):
        """Apply all currently active modifiers"""
        # This method is deprecated - modifiers are applied once when voted for
        pass
            
    def clear_votes(self):
        """Clear current vote state"""
        self.vote_options = []
        self.votes = {}
        
    def get_active_modifiers(self) -> List[Modifier]:
        """Get list of currently active modifiers"""
        return self.active_modifiers.copy()

# Example modifier implementations (for future use)
class DoubleMoveModifier(Modifier):
    def __init__(self):
        super().__init__(
            "Double Move",
            "Each player takes two moves per turn",
            "Move"
        )
        self.moves_this_turn = 0
        
    def can_apply(self, game_state, board) -> bool:
        return True
        
    def apply(self, game_state, board) -> bool:
        # This modifier affects the turn logic, so we'll track it
        # The actual implementation will be in the game logic
        print("Double Move modifier applied - each player gets 2 moves per turn")
        return True
        
    def on_move_made(self, game_state, board):
        """Called when a move is made to track double moves"""
        self.moves_this_turn += 1
        if self.moves_this_turn >= 2:
            # Switch players after 2 moves
            game_state.switch_player()
            self.moves_this_turn = 0
            return True  # Indicates player should switch
        return False  # Indicates player should continue
        
    def reset_turn(self):
        """Reset the turn counter (called when a new turn starts)"""
        self.moves_this_turn = 0

class BoardExpansionModifier(Modifier):
    def __init__(self):
        super().__init__(
            "Board Expansion",
            "Increase board size by 1 in both directions",
            "Board"
        )
        
    def can_apply(self, game_state, board) -> bool:
        return board.size < 10  # Limit maximum size, but allow multiple expansions
        
    def apply(self, game_state, board) -> bool:
        # Expand the board by adding one row and one column
        old_size = board.size
        new_size = old_size + 1
        
        # Create new board with expanded size
        new_board = Board(new_size)
        
        # Copy existing board state to new board
        for row in range(old_size):
            for col in range(old_size):
                new_board.grid[row][col] = board.grid[row][col]
        
        # Replace the old board with the new one
        board.size = new_size
        board.grid = new_board.grid
        board.last_move = None
        
        print(f"Board expanded from {old_size}x{old_size} to {new_size}x{new_size}")
        return True

class RandomAdjacentModifier(Modifier):
    def __init__(self):
        super().__init__(
            "Random Adjacent",
            "After each move, place an additional mark in a random adjacent cell",
            "Move"
        )
        
    def can_apply(self, game_state, board) -> bool:
        return True
        
    def apply(self, game_state, board) -> bool:
        print("Random Adjacent modifier applied - additional marks will be placed after each move")
        return True
        
    def on_move_made(self, game_state, board, last_move):
        """Called after a move to place an additional mark"""
        if last_move and board.last_move:
            row, col = board.last_move
            adjacent_cells = self._get_adjacent_cells(row, col, board.size)
            empty_adjacent = [cell for cell in adjacent_cells if board.is_valid_move(cell[0], cell[1])]
            
            if empty_adjacent:
                # Place a random mark in an adjacent cell (only if it's empty)
                random_row, random_col = random.choice(empty_adjacent)
                if board.get_cell(random_row, random_col) is None:  # Double-check it's empty
                    board.make_move(random_row, random_col, game_state.current_player)
                    print(f"Random adjacent mark placed at ({random_row}, {random_col})")
                else:
                    print(f"Random adjacent cell ({random_row}, {random_col}) was already occupied, skipping")
            else:
                print("No empty adjacent cells available for random placement")
                
    def _get_adjacent_cells(self, row, col, board_size):
        """Get all adjacent cells to a given position"""
        adjacent = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the cell itself
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < board_size and 0 <= new_col < board_size:
                    adjacent.append((new_row, new_col))
        return adjacent

class DiagonalOnlyModifier(Modifier):
    def __init__(self):
        super().__init__(
            "Diagonal Only",
            "Only diagonal wins count (no horizontal/vertical wins)",
            "Win Condition"
        )
        
    def can_apply(self, game_state, board) -> bool:
        return True
        
    def apply(self, game_state, board) -> bool:
        print("Diagonal Only modifier applied - only diagonal wins count")
        return True
        
    def check_win_condition(self, board, player):
        """Override win condition to only check diagonals"""
        # Check main diagonal (top-left to bottom-right)
        if all(board.get_cell(i, i) == player for i in range(board.size)):
            return True
            
        # Check anti-diagonal (top-right to bottom-left)
        if all(board.get_cell(i, board.size - 1 - i) == player for i in range(board.size)):
            return True
            
        return False 