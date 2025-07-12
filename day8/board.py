from typing import List, Optional, Tuple
from game_state import Player

class Board:
    def __init__(self, size: int = 3):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.last_move: Optional[Tuple[int, int]] = None
        
    def reset(self):
        """Reset the board to empty state"""
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.last_move = None
        
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
        # Check rows
        for row in range(self.size):
            if self._check_line([self.grid[row][col] for col in range(self.size)]):
                return self.grid[row][0]
                
        # Check columns
        for col in range(self.size):
            if self._check_line([self.grid[row][col] for row in range(self.size)]):
                return self.grid[0][col]
                
        # Check diagonals
        if self._check_line([self.grid[i][i] for i in range(self.size)]):
            return self.grid[0][0]
            
        if self._check_line([self.grid[i][self.size - 1 - i] for i in range(self.size)]):
            return self.grid[0][self.size - 1]
            
        return None
        
    def _check_line(self, line: List[Optional[Player]]) -> bool:
        """Check if a line has all the same player"""
        if not line or line[0] is None:
            return False
        return all(cell == line[0] for cell in line)
        
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