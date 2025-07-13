import pygame
from typing import List, Optional, Tuple
from settings import *
from game_state import GameState, GamePhase, Player
from board import Board
from modifier_system import ModifierSystem, Modifier

class UIManager:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.fonts = {
            'large': pygame.font.Font(None, FONT_SIZE_LARGE),
            'medium': pygame.font.Font(None, FONT_SIZE_MEDIUM),
            'small': pygame.font.Font(None, FONT_SIZE_SMALL)
        }
        
    def draw_title_screen(self):
        """Draw the title screen"""
        self.screen.fill(BLACK)
        
        # Title
        title_text = self.fonts['large'].render("Tic Tac Toe Evolution", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "Click anywhere to start a new game",
            "Two players take turns placing X and O",
            "After each round, vote on game modifiers!",
            "First to win 6 rounds wins the game"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.fonts['small'].render(instruction, True, LIGHT_GRAY)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 30))
            self.screen.blit(text, rect)
            
    def draw_board(self, board: Board, winning_line: Optional[List[Tuple[int, int]]] = None, highlight_alpha: int = 255):
        """Draw the tic-tac-toe board with optional winning line highlight"""
        # Calculate dynamic board position based on board size
        board_width = board.size * CELL_SIZE
        board_height = board.size * CELL_SIZE
        board_offset_x = (WINDOW_WIDTH - board_width) // 2
        board_offset_y = (WINDOW_HEIGHT - board_height) // 2
        
        # Draw grid lines with better contrast
        for i in range(board.size + 1):
            # Vertical lines
            pygame.draw.line(self.screen, DARK_GRAY,
                           (board_offset_x + i * CELL_SIZE, board_offset_y),
                           (board_offset_x + i * CELL_SIZE, board_offset_y + board_height), 3)
            # Horizontal lines
            pygame.draw.line(self.screen, DARK_GRAY,
                           (board_offset_x, board_offset_y + i * CELL_SIZE),
                           (board_offset_x + board_width, board_offset_y + i * CELL_SIZE), 3)
        
        # Draw winning line highlight if provided
        if winning_line and highlight_alpha > 0:
            self._draw_winning_highlight(board, winning_line, board_offset_x, board_offset_y, highlight_alpha)
        
        # Draw X's and O's
        for row in range(board.size):
            for col in range(board.size):
                player = board.get_cell(row, col)
                if player:
                    cell_center = (
                        board_offset_x + col * CELL_SIZE + CELL_SIZE // 2,
                        board_offset_y + row * CELL_SIZE + CELL_SIZE // 2
                    )
                    self._draw_player_symbol(player, cell_center)
    
    def _draw_winning_highlight(self, board: Board, winning_line: List[Tuple[int, int]], 
                              board_offset_x: int, board_offset_y: int, alpha: int):
        """Draw a visual highlight over the winning line"""
        # Create a highlight surface with transparency
        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        highlight_surface.set_alpha(alpha)
        
        # Use a bright color for the highlight (yellow/cyan for cyberpunk theme)
        highlight_color = YELLOW if 'cyberpunk' not in str(CURRENT_THEME) else (0, 255, 255)
        highlight_surface.fill(highlight_color)
        
        # Draw highlight over each winning cell
        for row, col in winning_line:
            highlight_rect = pygame.Rect(
                board_offset_x + col * CELL_SIZE,
                board_offset_y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            self.screen.blit(highlight_surface, highlight_rect)
            
            # Draw a border around the highlighted cell
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, 3)
            
    def _draw_player_symbol(self, player: Player, center: Tuple[int, int]):
        """Draw X or O symbol"""
        if player == Player.X:
            # Draw X
            size = CELL_SIZE // 3
            pygame.draw.line(self.screen, RED,
                           (center[0] - size, center[1] - size),
                           (center[0] + size, center[1] + size), 5)
            pygame.draw.line(self.screen, RED,
                           (center[0] + size, center[1] - size),
                           (center[0] - size, center[1] + size), 5)
        else:
            # Draw O
            radius = CELL_SIZE // 3
            pygame.draw.circle(self.screen, BLUE, center, radius, 5)
            
    def draw_game_info(self, game_state: GameState):
        """Draw game information (scores, current player, round)"""
        # Scores
        x_score = self.fonts['medium'].render(f"X: {game_state.scores[Player.X]}", True, RED)
        o_score = self.fonts['medium'].render(f"O: {game_state.scores[Player.O]}", True, BLUE)
        
        self.screen.blit(x_score, (20, 20))
        self.screen.blit(o_score, (20, 60))
        
        # Current player indicator
        current_text = self.fonts['medium'].render(f"Current: {game_state.current_player.value}", True, WHITE)
        self.screen.blit(current_text, (WINDOW_WIDTH - 200, 20))
        
        # Round number
        round_text = self.fonts['medium'].render(f"Round {game_state.current_round}/10", True, WHITE)
        self.screen.blit(round_text, (WINDOW_WIDTH - 200, 60))
        
        # Active modifiers
        if game_state.active_modifiers:
            modifier_text = self.fonts['small'].render("Active Modifiers:", True, WHITE)
            self.screen.blit(modifier_text, (20, WINDOW_HEIGHT - 100))
            
            # Get modifier counts and display
            modifier_counts = game_state.get_modifier_counts()
            
            for i, (modifier, count) in enumerate(list(modifier_counts.items())[:3]):  # Show first 3
                if count > 1:
                    mod_text = self.fonts['small'].render(f"• {modifier} ({count})", True, YELLOW)
                else:
                    mod_text = self.fonts['small'].render(f"• {modifier}", True, LIGHT_GRAY)
                self.screen.blit(mod_text, (20, WINDOW_HEIGHT - 80 + i * 20))
                
    def draw_winning_message(self, game_state: GameState):
        """Draw the winning message during the winning display phase"""
        if game_state.round_winner:
            # Draw a semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Draw the winning message
            winner_text = self.fonts['large'].render(f"{game_state.round_winner.value} WINS!", True, GREEN)
            winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
            self.screen.blit(winner_text, winner_rect)
            
            # Draw instruction to continue
            continue_text = self.fonts['medium'].render("Click to continue to modifier voting", True, LIGHT_GRAY)
            continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
            self.screen.blit(continue_text, continue_rect)
            
    def draw_round_end_screen(self, game_state: GameState):
        """Draw the round end screen"""
        self.screen.fill(BLACK)
        
        if game_state.round_winner:
            winner_text = self.fonts['large'].render(f"{game_state.round_winner.value} wins the round!", True, WHITE)
        else:
            winner_text = self.fonts['large'].render("It's a tie!", True, WHITE)
            
        winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(winner_text, winner_rect)
        
        # Continue instruction
        continue_text = self.fonts['medium'].render("Click to continue to modifier voting", True, LIGHT_GRAY)
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(continue_text, continue_rect)
        
    def draw_modifier_vote_screen(self, modifier_system: ModifierSystem):
        """Draw the modifier voting screen"""
        self.screen.fill(BLACK)
        
        # Title
        title_text = self.fonts['large'].render("Vote for Next Modifier", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Display modifier options
        for i, modifier in enumerate(modifier_system.vote_options):
            y_pos = 150 + i * 120
            
            # Modifier box with dark theme
            box_rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 100)
            pygame.draw.rect(self.screen, DARK_GRAY, box_rect)
            pygame.draw.rect(self.screen, LIGHT_GRAY, box_rect, 2)
            
            # Modifier name
            name_text = self.fonts['medium'].render(modifier.name, True, WHITE)
            self.screen.blit(name_text, (70, y_pos + 10))
            
            # Modifier description
            desc_text = self.fonts['small'].render(modifier.description, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (70, y_pos + 40))
            
            # Vote count
            vote_text = self.fonts['small'].render(f"Votes: {modifier_system.votes[modifier.name]}", True, YELLOW)
            self.screen.blit(vote_text, (70, y_pos + 70))
            
            # Click instruction
            click_text = self.fonts['small'].render(f"Click to vote for {modifier.name}", True, BLUE)
            self.screen.blit(click_text, (WINDOW_WIDTH - 300, y_pos + 40))
            
    def draw_game_end_screen(self, game_state: GameState):
        """Draw the game end screen"""
        self.screen.fill(BLACK)
        
        if game_state.game_winner:
            winner_text = self.fonts['large'].render(f"{game_state.game_winner.value} wins the game!", True, GREEN)
        else:
            winner_text = self.fonts['large'].render("Game ended in a tie!", True, WHITE)
            
        winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(winner_text, winner_rect)
        
        # Final scores
        final_score = self.fonts['medium'].render(
            f"Final Score - X: {game_state.scores[Player.X]} | O: {game_state.scores[Player.O]}", 
            True, WHITE
        )
        final_rect = final_score.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(final_score, final_rect)
        
        # Restart instruction
        restart_text = self.fonts['medium'].render("Click to play again", True, LIGHT_GRAY)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
        self.screen.blit(restart_text, restart_rect)
        
    def get_board_cell_from_mouse(self, mouse_pos: Tuple[int, int], board: Board) -> Optional[Tuple[int, int]]:
        """Convert mouse position to board cell coordinates"""
        x, y = mouse_pos
        
        # Calculate dynamic board position based on board size
        board_width = board.size * CELL_SIZE
        board_height = board.size * CELL_SIZE
        board_offset_x = (WINDOW_WIDTH - board_width) // 2
        board_offset_y = (WINDOW_HEIGHT - board_height) // 2
        
        # Check if click is within board bounds
        if (board_offset_x <= x <= board_offset_x + board_width and
            board_offset_y <= y <= board_offset_y + board_height):
            
            col = (x - board_offset_x) // CELL_SIZE
            row = (y - board_offset_y) // CELL_SIZE
            
            return (row, col)
        return None
        
    def get_modifier_vote_from_mouse(self, mouse_pos: Tuple[int, int], modifier_system: ModifierSystem) -> Optional[str]:
        """Convert mouse position to modifier vote"""
        x, y = mouse_pos
        
        for i, modifier in enumerate(modifier_system.vote_options):
            y_pos = 150 + i * 120
            box_rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 100)
            
            if box_rect.collidepoint(x, y):
                return modifier.name
        return None 