import pygame
import sys
import random
import time
import math
from enum import Enum
from typing import List, Optional, Tuple

# Enums and constants
class Player(Enum): 
    X = "X"
    O = "O"

class Phase(Enum): 
    TITLE = "title"
    PLAYING = "playing"
    WINNING_DISPLAY = "winning_display"
    VOTING = "voting"
    END = "end"

# Settings
WINDOW_SIZE = (800, 600)
CELL_SIZE = 80
FPS = 60

# Simplified theme system
THEMES = {
    'dark': {
        'bg': (0, 0, 0), 'text': (255, 255, 255), 'text_secondary': (200, 200, 200),
        'x': (255, 100, 100), 'o': (100, 150, 255), 'highlight': (255, 255, 100),
        'success': (100, 255, 100), 'grid': (40, 40, 40)
    },
    'light': {
        'bg': (255, 255, 255), 'text': (0, 0, 0), 'text_secondary': (64, 64, 64),
        'x': (255, 0, 0), 'o': (0, 0, 255), 'highlight': (255, 200, 0),
        'success': (0, 200, 0), 'grid': (200, 200, 200)
    },
    'cyber': {
        'bg': (10, 10, 20), 'text': (0, 255, 255), 'text_secondary': (200, 200, 255),
        'x': (255, 50, 100), 'o': (50, 200, 255), 'highlight': (255, 255, 0),
        'success': (0, 255, 100), 'grid': (50, 50, 80)
    }
}

# Simplified modifier definitions
MODIFIERS = {
    'extra_move': {'name': '+1 Extra Move', 'desc': 'Each player gets an extra move per turn'},
    'random_adjacent': {'name': 'Random Adjacent', 'desc': '50% chance to place mark in adjacent cell'},
    'board_expansion': {'name': 'Board Expansion', 'desc': 'Expand board to 4x4'},
    'diagonal_reduction': {'name': 'Diagonal Reduction', 'desc': 'Need only 2 pieces for diagonal win'},
    'horizontal_reduction': {'name': 'Horizontal Reduction', 'desc': 'Need only 2 pieces for horizontal win'}
}

class TicTacToe:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Tic Tac Toe Evolution - Correctly Fixed")
        self.clock = pygame.time.Clock()
        self.theme = THEMES['cyber']
        self.fonts = {
            'large': pygame.font.Font(None, 48),
            'medium': pygame.font.Font(None, 32),
            'small': pygame.font.Font(None, 24)
        }
        self.reset_game()
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = [[None]*3 for _ in range(3)]
        self.board_size = 3
        self.scores = {Player.X: 0, Player.O: 0}
        self.current_player = Player.X
        self.phase = Phase.TITLE
        self.round = 1
        self.active_modifiers = []
        self.vote_options = []
        self.winning_line = None
        self.winning_start_time = None
        self.moves_this_turn = 0
        self.win_requirements = {'horizontal': 3, 'vertical': 3, 'diagonal': 3}
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                    
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
        
    def handle_click(self, pos):
        """Handle mouse clicks based on current phase"""
        if self.phase == Phase.TITLE:
            self.phase = Phase.PLAYING
        elif self.phase == Phase.PLAYING:
            self.handle_game_click(pos)
        elif self.phase == Phase.WINNING_DISPLAY:
            self.start_voting()
        elif self.phase == Phase.VOTING:
            self.handle_vote_click(pos)
        elif self.phase == Phase.END:
            self.reset_game()
            
    def handle_game_click(self, pos):
        """Handle clicks during gameplay"""
        cell = self.get_cell_from_mouse(pos)
        if cell:
            row, col = cell
            if self.board[row][col] is None:
                self.board[row][col] = self.current_player
                self.moves_this_turn += 1
                
                # Apply move-based modifiers
                self.apply_move_modifiers(row, col)
                
                # Check for winner
                winner = self.check_winner()
                if winner:
                    self.scores[winner] += 1
                    self.winning_line = self.get_winning_line()
                    self.winning_start_time = time.time()
                    self.phase = Phase.WINNING_DISPLAY
                elif self.is_board_full():
                    self.phase = Phase.VOTING
                else:
                    # Check if we should switch players
                    extra_moves = sum(1 for mod in self.active_modifiers if 'extra_move' in mod)
                    if self.moves_this_turn >= 1 + extra_moves:
                        self.current_player = Player.O if self.current_player == Player.X else Player.X
                        self.moves_this_turn = 0
                        
    def get_cell_from_mouse(self, pos):
        """Convert mouse position to board cell"""
        x, y = pos
        board_x = (WINDOW_SIZE[0] - self.board_size * CELL_SIZE) // 2
        board_y = (WINDOW_SIZE[1] - self.board_size * CELL_SIZE) // 2
        
        col = (x - board_x) // CELL_SIZE
        row = (y - board_y) // CELL_SIZE
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return (row, col)
        return None
        
    def apply_move_modifiers(self, row, col):
        """Apply modifiers that trigger after a move"""
        for modifier in self.active_modifiers:
            if 'random_adjacent' in modifier and random.random() < 0.5:
                self.place_random_adjacent(row, col)
                
    def place_random_adjacent(self, row, col):
        """Place a random mark in an adjacent cell"""
        adjacent = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if (0 <= new_row < self.board_size and 
                    0 <= new_col < self.board_size and 
                    self.board[new_row][new_col] is None):
                    adjacent.append((new_row, new_col))
                    
        if adjacent:
            r, c = random.choice(adjacent)
            self.board[r][c] = self.current_player
            
    def check_winner(self):
        """Check for a winner considering modifier effects - CORRECTLY FIXED"""
        for player in [Player.X, Player.O]:
            # Check rows
            for row in range(self.board_size):
                if self.count_consecutive_for_player(self.board[row], player) >= self.win_requirements['horizontal']:
                    return player
                    
            # Check columns
            for col in range(self.board_size):
                column = [self.board[row][col] for row in range(self.board_size)]
                if self.count_consecutive_for_player(column, player) >= self.win_requirements['vertical']:
                    return player
                    
            # Check diagonals
            diagonal1 = [self.board[i][i] for i in range(self.board_size)]
            diagonal2 = [self.board[i][self.board_size-1-i] for i in range(self.board_size)]
            
            if self.count_consecutive_for_player(diagonal1, player) >= self.win_requirements['diagonal']:
                return player
            if self.count_consecutive_for_player(diagonal2, player) >= self.win_requirements['diagonal']:
                return player
                
        return None
        
    def count_consecutive_for_player(self, line, player):
        """Count consecutive pieces of the specific player"""
        max_count = 0
        current_count = 0
        
        for cell in line:
            if cell == player:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
                
        return max_count
        
    def get_winning_line(self):
        """Get the coordinates of the winning line - CORRECTLY FIXED"""
        for player in [Player.X, Player.O]:
            # Check rows
            for row in range(self.board_size):
                if self.count_consecutive_for_player(self.board[row], player) >= self.win_requirements['horizontal']:
                    return [(row, col) for col in range(self.board_size)]
                    
            # Check columns
            for col in range(self.board_size):
                column = [self.board[row][col] for row in range(self.board_size)]
                if self.count_consecutive_for_player(column, player) >= self.win_requirements['vertical']:
                    return [(row, col) for row in range(self.board_size)]
                    
            # Check diagonals
            diagonal1 = [self.board[i][i] for i in range(self.board_size)]
            diagonal2 = [self.board[i][self.board_size-1-i] for i in range(self.board_size)]
            
            if self.count_consecutive_for_player(diagonal1, player) >= self.win_requirements['diagonal']:
                return [(i, i) for i in range(self.board_size)]
            if self.count_consecutive_for_player(diagonal2, player) >= self.win_requirements['diagonal']:
                return [(i, self.board_size-1-i) for i in range(self.board_size)]
                
        return None
        
    def is_board_full(self):
        """Check if the board is full"""
        return all(cell is not None for row in self.board for cell in row)
        
    def start_voting(self):
        """Start the modifier voting phase"""
        self.phase = Phase.VOTING
        self.winning_line = None
        self.winning_start_time = None
        self.generate_vote_options()
        
    def generate_vote_options(self):
        """Generate random modifier options for voting"""
        available = list(MODIFIERS.keys())
        self.vote_options = random.sample(available, min(3, len(available)))
        
    def handle_vote_click(self, pos):
        """Handle clicks during voting"""
        # Simplified voting - just apply a random modifier
        if self.vote_options:
            chosen = random.choice(self.vote_options)
            self.apply_modifier(chosen)
            self.next_round()
            
    def apply_modifier(self, modifier_type):
        """Apply a modifier to the game"""
        if modifier_type == 'board_expansion' and self.board_size < 5:
            self.board_size += 1
            self.board = [[None]*self.board_size for _ in range(self.board_size)]
        elif modifier_type == 'diagonal_reduction':
            self.win_requirements['diagonal'] = max(2, self.win_requirements['diagonal'] - 1)
        elif modifier_type == 'horizontal_reduction':
            self.win_requirements['horizontal'] = max(2, self.win_requirements['horizontal'] - 1)
            
        self.active_modifiers.append(modifier_type)
        
    def next_round(self):
        """Move to the next round"""
        self.round += 1
        self.board = [[None]*self.board_size for _ in range(self.board_size)]
        self.current_player = Player.X
        self.moves_this_turn = 0
        self.vote_options = []
        
        # Check if game is over
        if self.round > 10 or max(self.scores.values()) >= 6:
            self.phase = Phase.END
        else:
            self.phase = Phase.PLAYING
            
    def update(self):
        """Update game logic"""
        pass
        
    def draw(self):
        """Draw the current game state"""
        self.screen.fill(self.theme['bg'])
        
        if self.phase == Phase.TITLE:
            self.draw_title()
        elif self.phase == Phase.PLAYING:
            self.draw_board()
            self.draw_info()
        elif self.phase == Phase.WINNING_DISPLAY:
            self.draw_board()
            self.draw_info()
            self.draw_winning_message()
        elif self.phase == Phase.VOTING:
            self.draw_voting()
        elif self.phase == Phase.END:
            self.draw_end()
            
        pygame.display.flip()
        
    def draw_title(self):
        """Draw the title screen"""
        title = self.fonts['large'].render("Tic Tac Toe Evolution - Correctly Fixed", True, self.theme['text'])
        title_rect = title.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//3))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "Click anywhere to start a new game",
            "Two players take turns placing X and O",
            "After each round, vote on game modifiers!",
            "First to win 6 rounds wins the game"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.fonts['small'].render(instruction, True, self.theme['text_secondary'])
            rect = text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2 + i * 30))
            self.screen.blit(text, rect)
            
    def draw_board(self):
        """Draw the game board"""
        board_x = (WINDOW_SIZE[0] - self.board_size * CELL_SIZE) // 2
        board_y = (WINDOW_SIZE[1] - self.board_size * CELL_SIZE) // 2
        
        # Draw grid lines
        for i in range(self.board_size + 1):
            pygame.draw.line(self.screen, self.theme['grid'],
                           (board_x + i * CELL_SIZE, board_y),
                           (board_x + i * CELL_SIZE, board_y + self.board_size * CELL_SIZE), 3)
            pygame.draw.line(self.screen, self.theme['grid'],
                           (board_x, board_y + i * CELL_SIZE),
                           (board_x + self.board_size * CELL_SIZE, board_y + i * CELL_SIZE), 3)
        
        # Draw winning line highlight
        if self.winning_line and self.phase == Phase.WINNING_DISPLAY:
            self.draw_winning_highlight(board_x, board_y)
        
        # Draw pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col]:
                    center = (board_x + col * CELL_SIZE + CELL_SIZE // 2,
                             board_y + row * CELL_SIZE + CELL_SIZE // 2)
                    self.draw_piece(self.board[row][col], center)
                    
    def draw_winning_highlight(self, board_x, board_y):
        """Draw highlight over winning line"""
        if not self.winning_line:
            return
            
        elapsed = time.time() - self.winning_start_time
        alpha = int(128 + 127 * abs(math.sin(elapsed * 3)))
        
        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        highlight_surface.set_alpha(alpha)
        highlight_surface.fill(self.theme['highlight'])
        
        for row, col in self.winning_line:
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                rect = pygame.Rect(board_x + col * CELL_SIZE, board_y + row * CELL_SIZE,
                                 CELL_SIZE, CELL_SIZE)
                self.screen.blit(highlight_surface, rect)
                pygame.draw.rect(self.screen, self.theme['highlight'], rect, 3)
                
    def draw_piece(self, player, center):
        """Draw X or O piece"""
        color = self.theme['x'] if player == Player.X else self.theme['o']
        size = CELL_SIZE // 3
        
        if player == Player.X:
            pygame.draw.line(self.screen, color,
                           (center[0] - size, center[1] - size),
                           (center[0] + size, center[1] + size), 5)
            pygame.draw.line(self.screen, color,
                           (center[0] + size, center[1] - size),
                           (center[0] - size, center[1] + size), 5)
        else:
            pygame.draw.circle(self.screen, color, center, size, 5)
            
    def draw_info(self):
        """Draw game information"""
        # Scores
        x_score = self.fonts['medium'].render(f"X: {self.scores[Player.X]}", True, self.theme['x'])
        o_score = self.fonts['medium'].render(f"O: {self.scores[Player.O]}", True, self.theme['o'])
        
        self.screen.blit(x_score, (20, 20))
        self.screen.blit(o_score, (20, 60))
        
        # Current player
        current = self.fonts['medium'].render(f"Current: {self.current_player.value}", True, self.theme['text'])
        self.screen.blit(current, (WINDOW_SIZE[0] - 200, 20))
        
        # Round
        round_text = self.fonts['medium'].render(f"Round {self.round}/10", True, self.theme['text'])
        self.screen.blit(round_text, (WINDOW_SIZE[0] - 200, 60))
        
        # Active modifiers
        if self.active_modifiers:
            mod_text = self.fonts['small'].render("Active Modifiers:", True, self.theme['text'])
            self.screen.blit(mod_text, (20, WINDOW_SIZE[1] - 100))
            
            for i, modifier in enumerate(self.active_modifiers[:3]):
                name = MODIFIERS.get(modifier, {}).get('name', modifier)
                text = self.fonts['small'].render(f"• {name}", True, self.theme['highlight'])
                self.screen.blit(text, (20, WINDOW_SIZE[1] - 80 + i * 20))
                
    def draw_winning_message(self):
        """Draw winning message overlay"""
        if self.phase == Phase.WINNING_DISPLAY:
            # Semi-transparent overlay
            overlay = pygame.Surface(WINDOW_SIZE)
            overlay.set_alpha(100)
            overlay.fill(self.theme['bg'])
            self.screen.blit(overlay, (0, 0))
            
            # Winning message
            winner = max(self.scores, key=self.scores.get) if self.scores[Player.X] != self.scores[Player.O] else None
            if winner:
                text = self.fonts['large'].render(f"{winner.value} WINS!", True, self.theme['success'])
                rect = text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//3))
                self.screen.blit(text, rect)
                
            # Continue instruction
            continue_text = self.fonts['medium'].render("Click to continue to modifier voting", True, self.theme['text_secondary'])
            continue_rect = continue_text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1] * 2//3))
            self.screen.blit(continue_text, continue_rect)
            
    def draw_voting(self):
        """Draw the voting screen"""
        title = self.fonts['large'].render("Vote for Next Modifier", True, self.theme['text'])
        title_rect = title.get_rect(center=(WINDOW_SIZE[0]//2, 50))
        self.screen.blit(title, title_rect)
        
        if self.vote_options:
            for i, modifier_type in enumerate(self.vote_options):
                modifier = MODIFIERS.get(modifier_type, {})
                name = modifier.get('name', modifier_type)
                desc = modifier.get('desc', '')
                
                # Modifier box
                box_rect = pygame.Rect(50, 150 + i * 120, WINDOW_SIZE[0] - 100, 100)
                pygame.draw.rect(self.screen, self.theme['grid'], box_rect)
                pygame.draw.rect(self.screen, self.theme['text'], box_rect, 2)
                
                # Modifier name
                name_text = self.fonts['medium'].render(name, True, self.theme['text'])
                self.screen.blit(name_text, (70, 170 + i * 120))
                
                # Modifier description
                desc_text = self.fonts['small'].render(desc, True, self.theme['text_secondary'])
                self.screen.blit(desc_text, (70, 200 + i * 120))
                
    def draw_end(self):
        """Draw the game end screen"""
        winner = max(self.scores, key=self.scores.get) if self.scores[Player.X] != self.scores[Player.O] else None
        
        if winner:
            text = self.fonts['large'].render(f"{winner.value} Wins the Game!", True, self.theme['success'])
        else:
            text = self.fonts['large'].render("It's a Tie!", True, self.theme['text'])
            
        rect = text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))
        self.screen.blit(text, rect)
        
        # Final scores
        final_scores = self.fonts['medium'].render(
            f"Final Score - X: {self.scores[Player.X]} | O: {self.scores[Player.O]}", 
            True, self.theme['text_secondary'])
        scores_rect = final_scores.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2 + 60))
        self.screen.blit(final_scores, scores_rect)
        
        # Restart instruction
        restart_text = self.fonts['medium'].render("Click to start a new game", True, self.theme['text_secondary'])
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2 + 120))
        self.screen.blit(restart_text, restart_rect)

if __name__ == "__main__":
    game = TicTacToe()
    game.run() 