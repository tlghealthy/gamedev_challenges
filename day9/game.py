import pygame
import sys
import time
import math
from settings import *
from game_state import GameState, GamePhase, Player
from board import Board
from modifier_system import ModifierSystem
from ui_manager import UIManager

class TicTacToeEvolution:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tic Tac Toe Evolution")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.game_state = GameState()
        self.board = Board(BOARD_SIZE)
        self.modifier_system = ModifierSystem()
        self.ui_manager = UIManager(self.screen)
        
        # Initialize some basic modifiers for testing
        self._initialize_modifiers()
        
    def _initialize_modifiers(self):
        """Initialize some basic modifiers for the prototype"""
        from modifier_system import (
            ExtraMoveModifier, 
            BoardExpansionModifier, 
            RandomAdjacentModifier,
            RandomAdjacentChanceModifier,
            RandomAdjacentFlipModifier,
            DiagonalWinReductionModifier,
            HorizontalWinReductionModifier
        )
        
        # Add all modifiers to the pool
        self.modifier_system.add_modifier(ExtraMoveModifier())
        self.modifier_system.add_modifier(BoardExpansionModifier())
        self.modifier_system.add_modifier(RandomAdjacentModifier())
        self.modifier_system.add_modifier(RandomAdjacentChanceModifier())
        self.modifier_system.add_modifier(RandomAdjacentFlipModifier())
        self.modifier_system.add_modifier(DiagonalWinReductionModifier())
        self.modifier_system.add_modifier(HorizontalWinReductionModifier())
        
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(event.pos)
                    
            # Update game state
            self._update()
            
            # Render
            self._render()
            
            # Cap the frame rate
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
        
    def _handle_mouse_click(self, pos):
        """Handle mouse click events based on current game phase"""
        print(f"Mouse click at {pos} in phase: {self.game_state.phase.value}")
        
        if self.game_state.phase == GamePhase.TITLE:
            print("Starting new game...")
            self._start_new_game()
            
        elif self.game_state.phase == GamePhase.PLAYING:
            self._handle_game_click(pos)
            
        elif self.game_state.phase == GamePhase.WINNING_DISPLAY:
            print("Moving to modifier voting...")
            self._start_modifier_voting()
            
        elif self.game_state.phase == GamePhase.ROUND_END:
            print("Starting modifier voting...")
            self._start_modifier_voting()
            
        elif self.game_state.phase == GamePhase.MODIFIER_VOTE:
            self._handle_vote_click(pos)
            
        elif self.game_state.phase == GamePhase.GAME_END:
            print("Starting new game from game end...")
            self._start_new_game()
            
    def _start_new_game(self):
        """Start a new game"""
        print("Initializing new game...")
        self.game_state = GameState()
        self.board = Board(BOARD_SIZE)
        self.modifier_system = ModifierSystem()
        self._initialize_modifiers()
        # Transition from TITLE to PLAYING phase
        self.game_state.phase = GamePhase.PLAYING
        print(f"Game phase set to: {self.game_state.phase.value}")
        
    def _handle_game_click(self, pos):
        """Handle click during gameplay"""
        cell = self.ui_manager.get_board_cell_from_mouse(pos, self.board)
        if cell:
            row, col = cell
            if self.board.make_move(row, col, self.game_state.current_player):
                # Increment move counter
                self.game_state.add_move()
                
                # Apply modifier effects after the move
                self._apply_move_modifiers(row, col)
                
                # Check for winner (considering modifier effects)
                winner = self._check_winner_with_modifiers()
                if winner:
                    # Get the winning line for visual highlighting
                    self.game_state.winning_line = self.board.get_winning_line()
                    self.game_state.winning_display_start_time = time.time()
                    self.game_state.add_score(winner)
                    self.game_state.phase = GamePhase.WINNING_DISPLAY
                    print(f"Player {winner.value} wins!")
                elif self.board.is_full():
                    # It's a tie
                    self.game_state.phase = GamePhase.ROUND_END
                else:
                    # Check if we should switch players (considering extra move modifiers)
                    self._handle_player_switching()
                    
    def _apply_move_modifiers(self, row, col):
        """Apply modifiers that trigger after a move"""
        # Get all adjacent modifiers (any modifier that inherits from AdjacentModifier)
        adjacent_modifiers = [
            mod for mod in self.modifier_system.active_modifiers 
            if hasattr(mod, 'on_move_made') and hasattr(mod, '_apply_adjacent_effect')
        ]
        
        # Apply each adjacent modifier
        for modifier in adjacent_modifiers:
            modifier.on_move_made(self.game_state, self.board, True)
        
    def _check_winner_with_modifiers(self):
        """Check for winner considering modifier effects"""
        # With the new flexible win condition system, we just use the board's check_winner
        # which automatically considers all active win condition modifiers
        return self.board.check_winner()
            
    def _handle_player_switching(self):
        """Handle player switching considering modifiers"""
        # Count extra move modifiers
        extra_move_count = sum(1 for mod in self.modifier_system.active_modifiers if mod.name == "+1 Extra Move per turn")
        
        # Calculate how many moves this player should get (1 base + extra moves)
        moves_per_turn = 1 + extra_move_count
        
        # Check if current player has made enough moves
        if self.game_state.get_moves_this_turn() >= moves_per_turn:
            print(f"Player {self.game_state.current_player.value} completed {moves_per_turn} moves, switching players")
            self.game_state.switch_player()
        else:
            print(f"Player {self.game_state.current_player.value} has {self.game_state.get_moves_this_turn()}/{moves_per_turn} moves")
                    
    def _start_modifier_voting(self):
        """Start the modifier voting phase"""
        self.game_state.phase = GamePhase.MODIFIER_VOTE
        self.game_state.winning_line = None  # Clear winning line
        self.game_state.winning_display_start_time = None  # Clear timing
        self.modifier_system.generate_vote_options(3)
        
    def _handle_vote_click(self, pos):
        """Handle click during modifier voting"""
        modifier_name = self.ui_manager.get_modifier_vote_from_mouse(pos, self.modifier_system)
        if modifier_name:
            self.modifier_system.vote_for_modifier(modifier_name)
            
            # For prototype: automatically apply winner after one vote
            # In full game, this would wait for both players to vote
            self._apply_vote_winner()
            
    def _apply_vote_winner(self):
        """Apply the winning modifier and continue to next round"""
        if self.modifier_system.apply_winner(self.game_state, self.board):
            print(f"Applied modifier: {self.modifier_system.get_winner().name}")
        
        # Move to next round
        self.game_state.next_round()
        self.board.reset()
        
        # Reapply all active modifiers to restore their effects after board reset
        for modifier in self.modifier_system.active_modifiers:
            modifier.apply(self.game_state, self.board)
        
        self.modifier_system.clear_votes()
        self.game_state.phase = GamePhase.PLAYING
        
    def _update(self):
        """Update game logic"""
        # Modifiers are applied once when voted for, not every frame
        pass
        
    def _render(self):
        """Render the current game state"""
        if self.game_state.phase == GamePhase.TITLE:
            self.ui_manager.draw_title_screen()
            
        elif self.game_state.phase == GamePhase.PLAYING:
            self.screen.fill(BLACK)
            self.ui_manager.draw_board(self.board)
            self.ui_manager.draw_game_info(self.game_state)
            
        elif self.game_state.phase == GamePhase.WINNING_DISPLAY:
            self.screen.fill(BLACK)
            # Calculate highlight alpha for pulsing effect
            elapsed_time = time.time() - self.game_state.winning_display_start_time
            pulse_alpha = int(128 + 127 * abs(math.sin(elapsed_time * 3)))  # Pulsing effect
            self.ui_manager.draw_board(self.board, self.game_state.winning_line, pulse_alpha)
            self.ui_manager.draw_game_info(self.game_state)
            self.ui_manager.draw_winning_message(self.game_state)
            
        elif self.game_state.phase == GamePhase.ROUND_END:
            self.ui_manager.draw_round_end_screen(self.game_state)
            
        elif self.game_state.phase == GamePhase.MODIFIER_VOTE:
            self.ui_manager.draw_modifier_vote_screen(self.modifier_system)
            
        elif self.game_state.phase == GamePhase.GAME_END:
            self.ui_manager.draw_game_end_screen(self.game_state)
            
        pygame.display.flip()

if __name__ == "__main__":
    game = TicTacToeEvolution()
    game.run() 