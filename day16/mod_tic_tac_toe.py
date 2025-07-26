"""
Tic‑Tac‑Toe Variant with Rule Modifiers
=======================================

This module implements a two‑player Tic‑Tac‑Toe variant using the
``pygame`` library. After each completed game the players are
presented with a list of “mods” – small rule changes that alter
subsequent rounds.  Examples of mods include increasing the size of
the board, introducing a time limit for each move, blocking a few
random squares at the start of a round and swapping player symbols
after every move.  The goal of the design is to provide a fresh
challenge after each game while still feeling familiar to fans of
classic Tic‑Tac‑Toe.

The code is organised as a single ``TicTacToeVariant`` class that
encapsulates the game state, drawing routines and event loop.  See
the ``run()`` method for the main loop.  Because ``pygame`` cannot
currently be imported in this environment the code is untested here,
however it follows common patterns documented in articles about
building games with Pygame【20656953666544†L66-L152】.  For example
``pygame.display.set_mode`` is used to create a window and
``pygame.draw.line`` draws the grid on screen【20656953666544†L136-L153】.

To run the game locally you will need Python 3 with ``pygame`` or
``pygame‑ce`` installed.  Install the dependency using::

    pip install pygame

or

    pip install pygame‑ce

Then execute this script with ``python mod_tic_tac_toe.py``.  The
game will open a window.  After each game ends you will see a
modifier selection screen.  Use the arrow keys or click on a mod to
apply it, then press *Enter* to start the next round.

This file should be placed in the same directory as any images you
wish to use for X and O marks.  By default the game draws simple
circles and crosses using vector primitives and does not depend on
external assets.
"""

import sys
import random
import time
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

# Import Pygame here.  If pygame is not installed this import will
# raise an ImportError; install pygame before running this script.
try:
    import pygame  # type: ignore
except ImportError as exc:
    raise ImportError(
        "Pygame is required to run this program.\n"
        "Install it with `pip install pygame` or `pip install pygame-ce`."
    ) from exc


@dataclass
class Mod:
    """Represents a rule modification that can be applied to the game.

    Attributes
    ----------
    name: str
        Human‑readable name of the mod.
    description: str
        A brief explanation of what the mod does.
    apply_func: Callable[["TicTacToeVariant"], None]
        A function that mutates the ``TicTacToeVariant`` instance to
        apply the effect of the mod.  See ``apply_mods`` for examples.
    """

    name: str
    description: str
    apply_func: Callable[["TicTacToeVariant"], None]


class TicTacToeVariant:
    """A two‑player Tic‑Tac‑Toe game with optional rule modifiers.

    The game begins with a standard 3×3 grid where the first player
    places 'X' and the second places 'O'.  After each game ends the
    players select one of several mods to activate.  Mods stay active
    across rounds and can accumulate, so the board may grow larger,
    moves might be timed and some squares may start off blocked.  A
    running list of active modifiers is displayed at the bottom of
    the window.  The implementation strives for a clean user
    experience with simple controls and clear visual feedback.
    """

    # Default configuration constants
    BASE_SIZE = 3
    MAX_SIZE = 5
    BASE_WIN_LENGTH = 3

    # Colours
    BG_COLOR = (245, 245, 245)
    GRID_COLOR = (50, 50, 50)
    X_COLOR = (200, 50, 50)
    O_COLOR = (50, 50, 200)
    BLOCK_COLOR = (180, 180, 180)
    TEXT_COLOR = (30, 30, 30)
    ACTIVE_MOD_COLOR = (255, 165, 0)

    def __init__(self) -> None:
        # Dynamic settings influenced by mods
        self.board_size: int = self.BASE_SIZE
        self.win_length: int = self.BASE_WIN_LENGTH
        self.time_limit: Optional[float] = None  # seconds per move
        self.random_blockers: int = 0  # number of blocked squares at start
        self.swap_symbols: bool = False  # whether X and O swap after every move

        # Active mods list for display purposes
        self.active_mods: List[str] = []

        # Game state variables
        self.board: List[List[Optional[str]]] = []
        self.blocked: List[Tuple[int, int]] = []
        self.current_player: str = 'X'
        self.winner: Optional[str] = None
        self.moves_made: int = 0
        self.game_over: bool = False
        self.turn_start_time: float = time.time()

        # Pygame objects
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.font_large: Optional[pygame.font.Font] = None
        self.font_small: Optional[pygame.font.Font] = None

        # Define available mods
        self.mods: List[Mod] = [
            Mod(
                name="Add Row & Column",
                description="Increase the board size by 1 (max 5).",
                apply_func=self.mod_add_row_col,
            ),
            Mod(
                name="Time Pressure",
                description="Players must move within 10 seconds.",
                apply_func=self.mod_time_pressure,
            ),
            Mod(
                name="Random Blockers",
                description="Block a number of random squares at the start.",
                apply_func=self.mod_random_blockers,
            ),
            Mod(
                name="Swap Symbols",
                description="Players swap X and O after every move.",
                apply_func=self.mod_swap_symbols,
            ),
        ]

    # --- Mod functions ---------------------------------------------------
    def mod_add_row_col(self) -> None:
        """Increase the board size by one up to ``MAX_SIZE``.

        Also increases the number of marks in a row required to win
        proportionally.  For example a 4×4 board requires four in a
        row and a 5×5 board requires five.
        """
        if self.board_size < self.MAX_SIZE:
            self.board_size += 1
            self.win_length = self.board_size  # require full row to win
            self.active_mods.append("+Board")

    def mod_time_pressure(self) -> None:
        """Enable a ten second per move timer."""
        # Only set the time limit the first time this mod is applied
        if self.time_limit is None:
            self.time_limit = 10.0
            self.active_mods.append("Time")

    def mod_random_blockers(self) -> None:
        """Introduce random blocked squares equal to the board size."""
        # Increase the number of blocked tiles for each application
        self.random_blockers += max(1, self.board_size // 2)
        self.active_mods.append("Blocks")

    def mod_swap_symbols(self) -> None:
        """Make players swap their symbols after every move."""
        if not self.swap_symbols:
            self.swap_symbols = True
            self.active_mods.append("Swap")

    # --- Game logic functions -------------------------------------------
    def reset_board(self) -> None:
        """Initialise the board and blocked cells for a new round."""
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.blocked = []
        # Choose random blocked squares based on ``random_blockers``
        num_blocks = min(self.random_blockers, self.board_size * self.board_size // 2)
        if num_blocks > 0:
            coords = [(r, c) for r in range(self.board_size) for c in range(self.board_size)]
            random.shuffle(coords)
            self.blocked = coords[:num_blocks]
            for r, c in self.blocked:
                self.board[r][c] = '#'  # placeholder to mark blocked cell
        self.current_player = 'X'
        self.winner = None
        self.moves_made = 0
        self.game_over = False
        self.turn_start_time = time.time()

    def check_winner(self, row: int, col: int, symbol: str) -> bool:
        """Check whether placing ``symbol`` at (row, col) wins the game.

        This checks all directions: horizontal, vertical and the two
        diagonals.  It counts consecutive symbols including the newly
        placed one.  If the longest run in any direction meets or
        exceeds ``win_length``, the player wins.
        """
        directions = [
            (1, 0),  # vertical
            (0, 1),  # horizontal
            (1, 1),  # main diagonal
            (1, -1),  # anti diagonal
        ]
        for dr, dc in directions:
            count = 1  # include the placed symbol
            # Check in the positive direction
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == symbol:
                count += 1
                r += dr
                c += dc
            # Check in the negative direction
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == symbol:
                count += 1
                r -= dr
                c -= dc
            if count >= self.win_length:
                return True
        return False

    def handle_move(self, pos: Tuple[int, int]) -> None:
        """Place the current player's symbol at the grid cell for ``pos``.

        If the cell is empty and not blocked, record the move.  After a
        successful placement this function checks for a winner or a
        draw and updates the game state accordingly.  If the `swap_symbols`
        flag is set then the player symbols are swapped for the next
        move.  Resets the per‑turn timer.
        """
        if self.game_over:
            return
        x, y = pos
        cell_size = self.calculate_cell_size()
        row = y // cell_size
        col = x // cell_size
        if row >= self.board_size or col >= self.board_size:
            return
        # ignore blocked or taken cells
        if self.board[row][col] is not None:
            return
        # Mark the cell with the current player's symbol
        symbol = self.current_player
        self.board[row][col] = symbol
        self.moves_made += 1
        # Check for win
        if self.check_winner(row, col, symbol):
            self.winner = symbol
            self.game_over = True
        elif self.moves_made == self.board_size * self.board_size - len(self.blocked):
            # All cells filled -> draw
            self.game_over = True
        else:
            # Swap current player
            if self.swap_symbols:
                # flip the symbol for the next placement
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
        # Reset timer for next move
        self.turn_start_time = time.time()

    def calculate_cell_size(self) -> int:
        """Calculate the size (in pixels) of each cell based on the window."""
        # The board area uses the minimum of width and height minus a margin for the status area.
        width, height = self.screen.get_size()
        # Reserve 100 pixels at bottom for status/mod area
        board_height = height - 100
        return board_height // self.board_size

    def draw_board(self) -> None:
        """Draw the grid lines, marks, blocked cells and status text."""
        self.screen.fill(self.BG_COLOR)
        cell_size = self.calculate_cell_size()
        board_pixel_size = cell_size * self.board_size

        # Draw grid lines
        for i in range(1, self.board_size):
            # vertical lines
            start_pos = (i * cell_size, 0)
            end_pos = (i * cell_size, board_pixel_size)
            pygame.draw.line(self.screen, self.GRID_COLOR, start_pos, end_pos, 3)
            # horizontal lines
            start_pos = (0, i * cell_size)
            end_pos = (board_pixel_size, i * cell_size)
            pygame.draw.line(self.screen, self.GRID_COLOR, start_pos, end_pos, 3)

        # Draw marks and blockers
        for r in range(self.board_size):
            for c in range(self.board_size):
                value = self.board[r][c]
                x = c * cell_size
                y = r * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)
                if value == 'X':
                    # Draw an X as two crossing lines
                    pygame.draw.line(self.screen, self.X_COLOR, rect.topleft, rect.bottomright, 6)
                    pygame.draw.line(self.screen, self.X_COLOR, rect.topright, rect.bottomleft, 6)
                elif value == 'O':
                    # Draw an O as a circle
                    pygame.draw.circle(
                        self.screen,
                        self.O_COLOR,
                        rect.center,
                        cell_size // 2 - 10,
                        6,
                    )
                elif value == '#':
                    # Draw a blocked cell (shaded rectangle)
                    pygame.draw.rect(self.screen, self.BLOCK_COLOR, rect)

        # Draw status text at bottom
        width, height = self.screen.get_size()
        status_area = pygame.Rect(0, height - 100, width, 100)
        pygame.draw.rect(self.screen, self.BG_COLOR, status_area)
        status_text = ""
        if not self.game_over:
            status_text = f"{self.current_player}'s turn"
            # Show timer if time_limit is active
            if self.time_limit is not None:
                elapsed = time.time() - self.turn_start_time
                remaining = max(0, self.time_limit - elapsed)
                status_text += f" | Time: {remaining:0.1f}s"
        else:
            if self.winner:
                status_text = f"{self.winner} wins!"
            else:
                status_text = "It's a draw!"
        # Show active mods
        if self.active_mods:
            mods_str = " • ".join(self.active_mods)
            status_text += f" | Mods: {mods_str}"
        # Render text
        text_surf = self.font_small.render(status_text, True, self.TEXT_COLOR)
        text_rect = text_surf.get_rect()
        text_rect.midleft = (10, height - 50)
        self.screen.blit(text_surf, text_rect)

        pygame.display.flip()

    # --- Mod selection interface ----------------------------------------
    def choose_mod(self) -> None:
        """Display the mod selection screen and wait for the player choice."""
        selected_index = 0
        selecting = True
        width, height = self.screen.get_size()
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(self.mods)
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(self.mods)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Apply the selected mod and exit
                        self.mods[selected_index].apply_func()
                        selecting = False
                    elif event.key == pygame.K_ESCAPE:
                        # Skip mod selection
                        selecting = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # Determine if a mod name was clicked
                    for idx, mod in enumerate(self.mods):
                        rect = self.get_mod_rect(idx)
                        if rect.collidepoint(mx, my):
                            self.mods[idx].apply_func()
                            selecting = False
                            selected_index = idx
                            break

            # Draw selection screen
            self.screen.fill(self.BG_COLOR)
            title = self.font_large.render("Choose a Mod", True, self.TEXT_COLOR)
            title_rect = title.get_rect(center=(width // 2, 60))
            self.screen.blit(title, title_rect)

            # Draw each mod with highlight
            for i, mod in enumerate(self.mods):
                rect = self.get_mod_rect(i)
                # Background highlight for selected mod
                if i == selected_index:
                    pygame.draw.rect(self.screen, self.ACTIVE_MOD_COLOR, rect)
                # Draw mod name
                name_surf = self.font_small.render(mod.name, True, self.TEXT_COLOR)
                name_rect = name_surf.get_rect(midleft=(rect.x + 10, rect.centery))
                self.screen.blit(name_surf, name_rect)
                # Draw mod description in a smaller font
                desc_surf = self.font_small.render(mod.description, True, self.TEXT_COLOR)
                desc_rect = desc_surf.get_rect(midleft=(rect.x + 220, rect.centery))
                self.screen.blit(desc_surf, desc_rect)
                # Outline
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 2)

            pygame.display.flip()
            self.clock.tick(30)

    def get_mod_rect(self, index: int) -> pygame.Rect:
        """Return the rectangle area for a mod entry on the selection screen."""
        width, height = self.screen.get_size()
        # vertical spacing
        top = 120 + index * 60
        return pygame.Rect(50, top, width - 100, 50)

    # --- Main game loop -------------------------------------------------
    def run(self) -> None:
        """Run the game loop."""
        pygame.init()
        # Determine window size based on maximum expected board
        window_side = 600
        window_height = window_side + 100  # extra for status/mod area
        self.screen = pygame.display.set_mode((window_side, window_height))
        pygame.display.set_caption("Tic‑Tac‑Toe Variant")
        self.clock = pygame.time.Clock()
        # Fonts
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 28)

        self.reset_board()

        while True:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.game_over:
                        self.handle_move(event.pos)
                    else:
                        # When game over, clicking anywhere proceeds to mod selection
                        self.choose_mod()
                        # Reset board for next round
                        self.reset_board()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            # Enforce time limit if active
            if not self.game_over and self.time_limit is not None:
                elapsed = time.time() - self.turn_start_time
                if elapsed > self.time_limit:
                    # Current player loses on timeout
                    self.winner = 'O' if self.current_player == 'X' else 'X'
                    self.game_over = True

            # Draw the current state
            self.draw_board()

            self.clock.tick(60)


def main() -> None:
    """Entry point for running the game from the command line."""
    game = TicTacToeVariant()
    game.run()


if __name__ == '__main__':
    main()