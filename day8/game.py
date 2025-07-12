import pygame
import sys
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
            DoubleMoveModifier, 
            BoardExpansionModifier, 
            RandomAdjacentModifier, 
            DiagonalOnlyModifier
        )
        
        # Add all modifiers to the pool
        self.modifier_system.add_modifier(DoubleMoveModifier())
        self.modifier_system.add_modifier(BoardExpansionModifier())
        self.modifier_system.add_modifier(RandomAdjacentModifier())
        self.modifier_system.add_modifier(DiagonalOnlyModifier())
        
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
                # Apply modifier effects after the move
                self._apply_move_modifiers(row, col)
                
                # Check for winner (considering modifier effects)
                winner = self._check_winner_with_modifiers()
                if winner:
                    self.game_state.add_score(winner)
                elif self.board.is_full():
                    # It's a tie
                    self.game_state.phase = GamePhase.ROUND_END
                else:
                    # Check if we should switch players (considering double move)
                    self._handle_player_switching()
                    
    def _apply_move_modifiers(self, row, col):
        """Apply modifiers that trigger after a move"""
        # Count how many of each type of modifier we have
        random_adjacent_count = sum(1 for mod in self.modifier_system.active_modifiers if mod.name == "Random Adjacent")
        double_move_count = sum(1 for mod in self.modifier_system.active_modifiers if mod.name == "Double Move")
        
        # Apply Random Adjacent modifiers (stack by chance)
        if random_adjacent_count > 0:
            # For each Random Adjacent modifier, there's a chance to place an additional mark
            for i in range(random_adjacent_count):
                # Each modifier has a 100% chance to place a mark, but we only place one per modifier
                # This prevents infinite recursion while still allowing stacking
                modifier = next(mod for mod in self.modifier_system.active_modifiers if mod.name == "Random Adjacent")
                modifier.on_move_made(self.game_state, self.board, True)
        
        # Apply Double Move modifiers (only one should handle the turn logic)
        if double_move_count > 0:
            # Use the first Double Move modifier to handle turn logic
            double_move_modifier = next(mod for mod in self.modifier_system.active_modifiers if mod.name == "Double Move")
            should_switch = double_move_modifier.on_move_made(self.game_state, self.board)
            if should_switch:
                print(f"Double move completed for {self.game_state.current_player.value}")
                # Reset all Double Move modifiers when turn switches
                for modifier in self.modifier_system.active_modifiers:
                    if modifier.name == "Double Move" and hasattr(modifier, 'reset_turn'):
                        modifier.reset_turn()
                        
    def _check_winner_with_modifiers(self):
        """Check for winner considering modifier effects"""
        # Check if Diagonal Only modifier is active
        diagonal_only_active = any(mod.name == "Diagonal Only" for mod in self.modifier_system.active_modifiers)
        
        if diagonal_only_active:
            # Use diagonal-only win condition
            for modifier in self.modifier_system.active_modifiers:
                if modifier.name == "Diagonal Only" and hasattr(modifier, 'check_win_condition'):
                    for player in [Player.X, Player.O]:
                        if modifier.check_win_condition(self.board, player):
                            return player
            return None
        else:
            # Use normal win condition
            return self.board.check_winner()
            
    def _handle_player_switching(self):
        """Handle player switching considering modifiers"""
        # Check if Double Move modifier is active
        double_move_active = any(mod.name == "Double Move" for mod in self.modifier_system.active_modifiers)
        
        if double_move_active:
            # Double move handles switching internally
            pass
        else:
            # Normal switching
            self.game_state.switch_player()
            
    def _reset_double_move_modifiers(self):
        """Reset all Double Move modifiers when a new turn starts"""
        for modifier in self.modifier_system.active_modifiers:
            if modifier.name == "Double Move" and hasattr(modifier, 'reset_turn'):
                modifier.reset_turn()
                    
    def _start_modifier_voting(self):
        """Start the modifier voting phase"""
        self.game_state.phase = GamePhase.MODIFIER_VOTE
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
            self.screen.fill(WHITE)
            self.ui_manager.draw_board(self.board)
            self.ui_manager.draw_game_info(self.game_state)
            
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