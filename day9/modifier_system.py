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
class AdjacentModifier(Modifier):
    """Base class for all adjacent cell modifiers"""
    
    def __init__(self, name: str, description: str, chance: float = 1.0):
        super().__init__(name, description, "Move")
        self.chance = chance  # Probability of triggering
        
    def can_apply(self, game_state, board) -> bool:
        return True
        
    def apply(self, game_state, board) -> bool:
        print(f"{self.name} modifier applied - {self.description}")
        return True
        
    def on_move_made(self, game_state, board, last_move):
        """Called after a move to place an additional mark"""
        if not last_move or not board.last_move:
            return
            
        # Check if we should trigger based on chance
        if random.random() > self.chance:
            return
            
        row, col = board.last_move
        adjacent_cells = self._get_adjacent_cells(row, col, board.size)
        empty_adjacent = [cell for cell in adjacent_cells if board.is_valid_move(cell[0], cell[1])]
        
        if empty_adjacent:
            self._apply_adjacent_effect(board, empty_adjacent, game_state.current_player)
    
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
    
    @abstractmethod
    def _apply_adjacent_effect(self, board, empty_adjacent, current_player):
        """Apply the specific adjacent effect - to be implemented by subclasses"""
        pass

class ExtraMoveModifier(Modifier):
    def __init__(self):
        super().__init__(
            "+1 Extra Move per turn",
            "Each player takes one extra move per turn",
            "Move"
        )
        
    def can_apply(self, game_state, board) -> bool:
        return True
        
    def apply(self, game_state, board) -> bool:
        # This modifier affects the turn logic, so we'll track it
        # The actual implementation will be in the game logic
        print("+1 Extra Move per turn modifier applied - each player gets 1 extra move per turn")
        return True

class RandomAdjacentModifier(AdjacentModifier):
    def __init__(self):
        super().__init__(
            "Random Adjacent",
            "After each move, place an additional mark in a random adjacent cell",
            chance=1.0
        )
        
    def _apply_adjacent_effect(self, board, empty_adjacent, current_player):
        # Place a random mark in an adjacent cell (only if it's empty)
        random_row, random_col = random.choice(empty_adjacent)
        if board.get_cell(random_row, random_col) is None:  # Double-check it's empty
            board.make_move(random_row, random_col, current_player)
            print(f"Random adjacent mark placed at ({random_row}, {random_col})")
        else:
            print(f"Random adjacent cell ({random_row}, {random_col}) was already occupied, skipping")

class RandomAdjacentChanceModifier(AdjacentModifier):
    """Chance-based random adjacent placement"""
    
    def __init__(self):
        super().__init__(
            "Random Adjacent Chance",
            "After each move, 50% chance to place an additional mark in a random adjacent cell",
            chance=0.5
        )
    
    def _apply_adjacent_effect(self, board, empty_adjacent, current_player):
        random_row, random_col = random.choice(empty_adjacent)
        if board.get_cell(random_row, random_col) is None:
            board.make_move(random_row, random_col, current_player)
            print(f"Random adjacent chance mark placed at ({random_row}, {random_col})")

class RandomAdjacentFlipModifier(AdjacentModifier):
    """Flip adjacent enemy pieces to friendly"""
    
    def __init__(self):
        super().__init__(
            "Random Adjacent Flip",
            "After each move, flip an adjacent enemy piece to your side",
            chance=1.0
        )
    
    def _apply_adjacent_effect(self, board, empty_adjacent, current_player):
        # Get all adjacent cells (not just empty ones)
        row, col = board.last_move
        all_adjacent = self._get_adjacent_cells(row, col, board.size)
        
        # Find enemy pieces adjacent
        enemy_adjacent = []
        for adj_row, adj_col in all_adjacent:
            cell_content = board.get_cell(adj_row, adj_col)
            if cell_content and cell_content != current_player:
                enemy_adjacent.append((adj_row, adj_col))
        
        if enemy_adjacent:
            flip_row, flip_col = random.choice(enemy_adjacent)
            board.grid[flip_row][flip_col] = current_player
            print(f"Flipped enemy piece at ({flip_row}, {flip_col}) to {current_player.value}")
        else:
            # If no enemies, place in empty cell like regular adjacent
            if empty_adjacent:
                random_row, random_col = random.choice(empty_adjacent)
                board.make_move(random_row, random_col, current_player)
                print(f"Random adjacent flip placed at ({random_row}, {random_col})")

class BoardExpansionModifier(Modifier):
    def __init__(self):
        super().__init__(
            "Board Expansion",
            "Increase board size by 1 in both directions",
            "Board"
        )
        self.applied_to_size = None  # Track what size we've already applied to
        
    def can_apply(self, game_state, board) -> bool:
        return board.size < 10  # Limit maximum size, but allow multiple expansions
        
    def apply(self, game_state, board) -> bool:
        # Only apply if we haven't already applied to this board size
        if self.applied_to_size == board.size:
            return True  # Already applied to this size
            
        # Expand the board by adding one row and one column
        old_size = board.size
        new_size = old_size + 1
        
        # Create new board with expanded size
        new_board = Board(new_size)
        
        # Copy existing board state to new board
        for row in range(old_size):
            for col in range(old_size):
                new_board.grid[row][col] = board.grid[row][col]
        
        # Copy win condition modifiers
        new_board.diagonal_win_reduction = board.diagonal_win_reduction
        new_board.horizontal_win_reduction = board.horizontal_win_reduction
        new_board.vertical_win_reduction = board.vertical_win_reduction
        
        # Replace the old board with the new one
        board.size = new_size
        board.grid = new_board.grid
        board.last_move = None
        board.diagonal_win_reduction = new_board.diagonal_win_reduction
        board.horizontal_win_reduction = new_board.horizontal_win_reduction
        board.vertical_win_reduction = new_board.vertical_win_reduction
        
        # Mark that we've applied to the new size
        self.applied_to_size = new_size
        
        print(f"Board expanded from {old_size}x{old_size} to {new_size}x{new_size}")
        print(f"Win requirements increased: {board.get_win_requirements()}")
        return True

class DiagonalWinReductionModifier(Modifier):
    def __init__(self):
        super().__init__(
            "Diagonal Win Reduction",
            "Reduce diagonal win requirement by 1 piece",
            "Win Condition"
        )
        self.reduction_applied = 0  # Track how much reduction this instance has applied

    def can_apply(self, game_state, board) -> bool:
        # Can't reduce below 2 pieces needed, and can't apply if already fully applied
        return board.size - board.diagonal_win_reduction > 2 and self.reduction_applied < 1

    def apply(self, game_state, board) -> bool:
        needed = 1 - self.reduction_applied
        if needed > 0:
            max_allowed = board.size - board.diagonal_win_reduction - 2
            to_apply = min(needed, max_allowed)
            if to_apply > 0:
                board.reduce_diagonal_win_requirement(to_apply)
                self.reduction_applied += to_apply
        return True

class HorizontalWinReductionModifier(Modifier):
    def __init__(self):
        super().__init__(
            "Horizontal Win Reduction",
            "Reduce horizontal win requirement by 1 piece",
            "Win Condition"
        )
        self.reduction_applied = 0  # Track how much reduction this instance has applied

    def can_apply(self, game_state, board) -> bool:
        # Can't reduce below 2 pieces needed, and can't apply if already fully applied
        return board.size - board.horizontal_win_reduction > 2 and self.reduction_applied < 1

    def apply(self, game_state, board) -> bool:
        needed = 1 - self.reduction_applied
        if needed > 0:
            max_allowed = board.size - board.horizontal_win_reduction - 2
            to_apply = min(needed, max_allowed)
            if to_apply > 0:
                board.reduce_horizontal_win_requirement(to_apply)
                self.reduction_applied += to_apply
        return True 