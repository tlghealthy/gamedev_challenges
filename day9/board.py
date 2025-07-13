from typing import List, Optional, Tuple
from game_state import Player

class Board:
    def __init__(self, size: int = 3):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.last_move: Optional[Tuple[int, int]] = None
        # Win condition modifiers
        self.diagonal_win_reduction = 0  # Reduce diagonal wins by this amount
        self.horizontal_win_reduction = 0  # Reduce horizontal wins by this amount
        self.vertical_win_reduction = 0  # Reduce vertical wins by this amount
        
    def reset(self):
        """Reset the board to empty state"""
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.last_move = None
        # Reset win condition modifiers
        self.diagonal_win_reduction = 0
        self.horizontal_win_reduction = 0
        self.vertical_win_reduction = 0
        
    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid (within bounds and cell is empty)"""
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        return self.grid[row][col] is None
        
    def make_move(self, row: int, col: int, player: Player) -> bool:
        """Make a move and return True if successful"""
        if not self.is_valid_move(row, col):
            return False
            
        self.grid[row][col] = player
        self.last_move = (row, col)
        return True
        
    def get_cell(self, row: int, col: int) -> Optional[Player]:
        """Get the player at a specific cell"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return None
        
    def is_full(self) -> bool:
        """Check if the board is full"""
        return all(self.grid[row][col] is not None 
                  for row in range(self.size) 
                  for col in range(self.size))
                  
    def check_winner(self) -> Optional[Player]:
        """Check for a winner and return the player or None"""
        win_reqs = self.get_win_requirements()
        directions = [
            (0, 1, win_reqs['horizontal']),   # right
            (1, 0, win_reqs['vertical']),     # down
            (1, 1, win_reqs['diagonal']),     # down-right
            (1, -1, win_reqs['diagonal'])     # down-left
        ]
        for row in range(self.size):
            for col in range(self.size):
                player = self.grid[row][col]
                if player is None:
                    continue
                for dr, dc, req in directions:
                    if self._can_win_from(row, col, dr, dc, req):
                        if self._is_winning_line(row, col, dr, dc, req, player):
                            return player
        return None

    def get_winning_line(self) -> Optional[list[tuple[int, int]]]:
        """Get the coordinates of the winning line, or None if no winner"""
        win_reqs = self.get_win_requirements()
        directions = [
            (0, 1, win_reqs['horizontal']),   # right
            (1, 0, win_reqs['vertical']),     # down
            (1, 1, win_reqs['diagonal']),     # down-right
            (1, -1, win_reqs['diagonal'])     # down-left
        ]
        for row in range(self.size):
            for col in range(self.size):
                player = self.grid[row][col]
                if player is None:
                    continue
                for dr, dc, req in directions:
                    if self._can_win_from(row, col, dr, dc, req):
                        if self._is_winning_line(row, col, dr, dc, req, player):
                            return [(row + i * dr, col + i * dc) for i in range(req)]
        return None

    def _can_win_from(self, row, col, dr, dc, req):
        """Check if there is enough space from (row, col) in direction (dr, dc) for a win"""
        end_row = row + (req - 1) * dr
        end_col = col + (req - 1) * dc
        return 0 <= end_row < self.size and 0 <= end_col < self.size

    def _is_winning_line(self, row, col, dr, dc, req, player):
        """Check if all cells from (row, col) in direction (dr, dc) for req length are the same player"""
        for i in range(req):
            r, c = row + i * dr, col + i * dc
            if self.grid[r][c] != player:
                return False
        return True
    
    def _check_line(self, line: List[Optional[Player]]) -> bool:
        """Check if a line has all the same player"""
        if not line or line[0] is None:
            return False
        return all(cell == line[0] for cell in line)

    def _check_line_with_length(self, line: List[Optional[Player]], required_length: int) -> bool:
        """Check if a line has consecutive pieces of the required length"""
        if not line or required_length <= 0:
            return False
            
        # Check for consecutive pieces of the required length
        for i in range(len(line) - required_length + 1):
            segment = line[i:i + required_length]
            if all(cell is not None and cell == segment[0] for cell in segment):
                return True
        return False
    
    def _get_winning_segment(self, line: List[Optional[Player]], required_length: int) -> Optional[List[int]]:
        """Get the indices of the winning segment in a line"""
        if not line or required_length <= 0:
            return None
            
        # Check for consecutive pieces of the required length
        for i in range(len(line) - required_length + 1):
            segment = line[i:i + required_length]
            if all(cell is not None and cell == segment[0] for cell in segment):
                return list(range(i, i + required_length))
        return None
        
    def get_board_state(self) -> List[List[Optional[Player]]]:
        """Get a copy of the current board state"""
        return [row[:] for row in self.grid]
        
    def set_board_state(self, state: List[List[Optional[Player]]]):
        """Set the board to a specific state (for modifiers)"""
        if len(state) == self.size and all(len(row) == self.size for row in state):
            self.grid = [row[:] for row in state]
            
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cell positions"""
        empty = []
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] is None:
                    empty.append((row, col))
        return empty
    
    def reduce_diagonal_win_requirement(self, reduction: int = 1):
        """Reduce the number of pieces needed for diagonal wins"""
        self.diagonal_win_reduction += reduction
        print(f"Diagonal win requirement reduced by {reduction} (now need {self.size - self.diagonal_win_reduction} pieces)")
    
    def reduce_horizontal_win_requirement(self, reduction: int = 1):
        """Reduce the number of pieces needed for horizontal wins"""
        self.horizontal_win_reduction += reduction
        print(f"Horizontal win requirement reduced by {reduction} (now need {self.size - self.horizontal_win_reduction} pieces)")
    
    def reduce_vertical_win_requirement(self, reduction: int = 1):
        """Reduce the number of pieces needed for vertical wins"""
        self.vertical_win_reduction += reduction
        print(f"Vertical win requirement reduced by {reduction} (now need {self.size - self.vertical_win_reduction} pieces)")
    
    def get_win_requirements(self) -> dict:
        """Get current win requirements for each type"""
        return {
            'horizontal': self.size - self.horizontal_win_reduction,
            'vertical': self.size - self.vertical_win_reduction,
            'diagonal': self.size - self.diagonal_win_reduction
        } 