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

        # Additional dynamic settings introduced by new mods
        self.gravity: bool = False  # marks fall to the lowest available row in a column
        self.wild_card_active: bool = False  # whether a wild cell exists on the board
        self.wild_cell: Optional[Tuple[int, int]] = None  # coordinates of the wild cell
        self.double_turn: bool = False  # whether a player gets multiple moves per turn
        self.double_turn_moves: int = 2  # number of moves per turn when double_turn is active
        self.turn_moves_left: int = 1  # moves remaining in the current turn
        self.remove_opponent: bool = False  # whether players can remove an opponent's mark
        self.remove_remaining: dict[str, int] = {'X': 0, 'O': 0}
        self.diagonal_only: bool = False  # only diagonal lines count towards a win
        self.teleport: bool = False  # mark teleports to a random empty cell after placement

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
            # Board enlargement mod
            Mod(
                name="Add Row & Column",
                description="Increase board size by 1 (max 5).",
                apply_func=self.mod_add_row_col,
            ),
            # Timer mod
            Mod(
                name="Time Pressure",
                description="Players must move within a time limit.",
                apply_func=self.mod_time_pressure,
            ),
            # Random blockers mod
            Mod(
                name="Random Blockers",
                description="Add blocked squares to the board.",
                apply_func=self.mod_random_blockers,
            ),
            # Swap symbols mod
            Mod(
                name="Swap Symbols",
                description="Swap X and O after each move.",
                apply_func=self.mod_swap_symbols,
            ),
            # Gravity mod
            Mod(
                name="Gravity",
                description="Marks fall to the bottom of the column.",
                apply_func=self.mod_gravity,
            ),
            # Wild card mod
            Mod(
                name="Wild Card",
                description="One cell counts for both players.",
                apply_func=self.mod_wild_card,
            ),
            # Double turn mod
            Mod(
                name="Double Move",
                description="Take more than one move each turn.",
                apply_func=self.mod_double_turn,
            ),
            # Remove opponent mod
            Mod(
                name="Remove Opponent",
                description="Remove one opponent mark each game.",
                apply_func=self.mod_remove_opponent,
            ),
            # Diagonal only mod
            Mod(
                name="Diagonal Only",
                description="Win only on diagonals.",
                apply_func=self.mod_diagonal_only,
            ),
            # Teleport mod
            Mod(
                name="Teleport",
                description="Your mark teleports to a random cell.",
                apply_func=self.mod_teleport,
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
            # Randomise the timer between 5 and 15 seconds to vary difficulty
            self.time_limit = random.uniform(5.0, 15.0)
            self.active_mods.append(f"Timer({self.time_limit:.0f}s)")

    def mod_random_blockers(self) -> None:
        """Introduce random blocked squares equal to the board size."""
        # Increase the number of blocked tiles for each application
        # Randomise the number of blockers between 1 and board_size
        self.random_blockers += random.randint(1, max(1, self.board_size))
        self.active_mods.append("Blocks")

    def mod_swap_symbols(self) -> None:
        """Make players swap their symbols after every move."""
        if not self.swap_symbols:
            self.swap_symbols = True
            self.active_mods.append("Swap")

    def mod_gravity(self) -> None:
        """Enable gravity so pieces fall to the lowest available row."""
        if not self.gravity:
            self.gravity = True
            self.active_mods.append("Gravity")

    def mod_wild_card(self) -> None:
        """Activate a wild card cell that counts for both players."""
        if not self.wild_card_active:
            self.wild_card_active = True
            self.active_mods.append("Wild")

    def mod_double_turn(self) -> None:
        """Allow players to make multiple moves per turn."""
        if not self.double_turn:
            self.double_turn = True
            # Randomise number of moves per turn between 2 and 3
            self.double_turn_moves = random.randint(2, 3)
            self.active_mods.append(f"2x({self.double_turn_moves})")

    def mod_remove_opponent(self) -> None:
        """Permit each player to remove one opponent mark per game."""
        if not self.remove_opponent:
            self.remove_opponent = True
            self.active_mods.append("Remove")

    def mod_diagonal_only(self) -> None:
        """Only diagonal lines count towards a win."""
        if not self.diagonal_only:
            self.diagonal_only = True
            self.active_mods.append("Diag")

    def mod_teleport(self) -> None:
        """Make placed marks teleport to a random empty cell."""
        if not self.teleport:
            self.teleport = True
            self.active_mods.append("Teleport")

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
        # Reset per-turn moves left based on double-turn mod
        self.turn_moves_left = self.double_turn_moves if self.double_turn else 1
        # Reset removal counters each round
        if self.remove_opponent:
            # each player gets one removal per game
            self.remove_remaining = {'X': 1, 'O': 1}
        # Assign wild card cell on new round
        self.wild_cell = None
        if self.wild_card_active:
            # choose a random empty cell not blocked
            free = [(r, c) for r in range(self.board_size) for c in range(self.board_size)
                    if self.board[r][c] is None]
            if free:
                self.wild_cell = random.choice(free)
        # If wild cell exists, mark as None for drawing; board cell remains None until used

    def check_winner(self, row: int, col: int, symbol: str) -> bool:
        """Check whether placing ``symbol`` at (row, col) wins the game.

        This checks all directions: horizontal, vertical and the two
        diagonals.  It counts consecutive symbols including the newly
        placed one.  If the longest run in any direction meets or
        exceeds ``win_length``, the player wins.
        """
        # Determine which directions to check
        if self.diagonal_only:
            directions = [
                (1, 1),  # main diagonal
                (1, -1),  # anti diagonal
            ]
        else:
            directions = [
                (1, 0),  # vertical
                (0, 1),  # horizontal
                (1, 1),  # main diagonal
                (1, -1),  # anti diagonal
            ]
        # Helper to decide if a cell counts as matching the symbol
        def matches(r: int, c: int) -> bool:
            val = self.board[r][c]
            if self.wild_card_active and self.wild_cell == (r, c):
                return True
            return val == symbol

        for dr, dc in directions:
            count = 1  # include the placed symbol
            # Check in the positive direction
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and matches(r, c):
                count += 1
                r += dr
                c += dc
            # Check in the negative direction
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and matches(r, c):
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
        # Return early if round finished
        if self.game_over:
            return
        x, y = pos
        cell_size = self.calculate_cell_size()
        col = x // cell_size
        row = y // cell_size
        # Disallow clicks outside the board
        if col < 0 or col >= self.board_size or row < 0 or row >= self.board_size:
            return

        # Determine target row and column based on gravity
        target_row, target_col = row, col
        if self.gravity:
            # With gravity, find the lowest available row in this column
            for r in reversed(range(self.board_size)):
                if self.board[r][col] is None or (self.wild_card_active and self.wild_cell == (r, col)):
                    target_row = r
                    target_col = col
                    break
            else:
                # column is full
                return
        # Determine if removing opponent mark is possible
        target_value = self.board[target_row][target_col]
        if target_value is not None and target_value != '#' and not (self.wild_card_active and self.wild_cell == (target_row, target_col)):
            # Cell contains a mark (X or O).  Allow removal if remove_opponent is active and the mark belongs to the opponent.
            if self.remove_opponent and target_value != self.current_player and self.remove_remaining.get(self.current_player, 0) > 0:
                # Remove opponent mark and place current player's mark
                self.remove_remaining[self.current_player] -= 1
                self.board[target_row][target_col] = self.current_player
            else:
                # Cannot place on opponent mark
                return
        else:
            # Check for blocker (#) on cell
            if target_value == '#':
                return
            # Otherwise place mark normally
            self.board[target_row][target_col] = self.current_player

        # Teleport the mark if teleport mod is active
        new_row, new_col = target_row, target_col
        if self.teleport:
            # Determine all free cells (excluding blockers and existing marks)
            free_cells = [
                (r, c)
                for r in range(self.board_size)
                for c in range(self.board_size)
                if (self.board[r][c] is None or (self.wild_card_active and self.wild_cell == (r, c)))
            ]
            # Remove the original cell from free list to avoid teleporting to the same place
            if (new_row, new_col) in free_cells:
                free_cells.remove((new_row, new_col))
            if free_cells:
                # Clear original cell except keep wild cell placeholder
                if not (self.wild_card_active and self.wild_cell == (new_row, new_col)):
                    self.board[new_row][new_col] = None
                dest_row, dest_col = random.choice(free_cells)
                self.board[dest_row][dest_col] = self.current_player
                new_row, new_col = dest_row, dest_col

        # Update move counter (we count only actual placements)
        self.moves_made += 1

        # Check for a winner using the final location of the mark
        if self.check_winner(new_row, new_col, self.current_player):
            self.winner = self.current_player
            self.game_over = True
        elif self.moves_made >= self.board_size * self.board_size - len(self.blocked):
            # Game is a draw
            self.game_over = True
        else:
            # Update current player based on mods
            # First handle double-turn mod: decrement moves left and determine if we keep the same player
            if self.double_turn:
                self.turn_moves_left -= 1
                if self.turn_moves_left <= 0:
                    # reset the moves counter for the next player's turn
                    self.turn_moves_left = self.double_turn_moves
                    # After finishing turn, decide next player
                    self.current_player = 'O' if self.current_player == 'X' else 'X'
                # If moves still left, player remains the same
            else:
                # Normal toggling
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            # If swap_symbols mod is active and double_turn is not active (to avoid conflict), flip symbol regardless of turn logic
            if self.swap_symbols and not self.double_turn:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
        # Reset the timer for the next move (or next turn)
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

        # Draw marks, blockers and special markers
        for r in range(self.board_size):
            for c in range(self.board_size):
                value = self.board[r][c]
                x = c * cell_size
                y = r * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)
                if value == 'X':
                    pygame.draw.line(self.screen, self.X_COLOR, rect.topleft, rect.bottomright, 6)
                    pygame.draw.line(self.screen, self.X_COLOR, rect.topright, rect.bottomleft, 6)
                elif value == 'O':
                    pygame.draw.circle(
                        self.screen,
                        self.O_COLOR,
                        rect.center,
                        cell_size // 2 - 10,
                        6,
                    )
                elif value == '#':
                    pygame.draw.rect(self.screen, self.BLOCK_COLOR, rect)
                # Draw wild card marker if cell is designated wild and currently empty
                if self.wild_card_active and self.wild_cell == (r, c) and (value is None or value == '#'):
                    pygame.draw.circle(
                        self.screen,
                        (255, 215, 0),  # gold color
                        rect.center,
                        cell_size // 6,
                        0,
                    )

        # Draw status text at bottom
        width, height = self.screen.get_size()
        status_area = pygame.Rect(0, height - 100, width, 100)
        pygame.draw.rect(self.screen, self.BG_COLOR, status_area)
        # Compose status and mods text into multiple lines to avoid overflow
        lines: List[str] = []
        if not self.game_over:
            line = f"{self.current_player}'s turn"
            # Show remaining moves for double-turn mod
            if self.double_turn:
                line += f" ({self.turn_moves_left}/{self.double_turn_moves})"
            # Show timer if active
            if self.time_limit is not None:
                elapsed = time.time() - self.turn_start_time
                remaining = max(0, self.time_limit - elapsed)
                line += f"  Time: {remaining:0.1f}s"
            lines.append(line)
        else:
            if self.winner:
                lines.append(f"{self.winner} wins!")
            else:
                lines.append("It's a draw!")
        # Prepare mods string and wrap if necessary
        if self.active_mods:
            mods_str = " · ".join(self.active_mods)
            import textwrap
            wrapped = textwrap.wrap(mods_str, width=40)
            lines.extend(wrapped)
        # Render each line with proper spacing
        y_offset = height - 90
        for line in lines:
            surf = self.font_small.render(line, True, self.TEXT_COLOR)
            rect = surf.get_rect()
            rect.midleft = (10, y_offset)
            # If line is too long, truncate with ellipsis
            max_width = width - 20
            if rect.width > max_width:
                # reduce length until fits
                shortened = line
                while True:
                    shortened = shortened[:-1]
                    trial = shortened + '…'
                    surf_trial = self.font_small.render(trial, True, self.TEXT_COLOR)
                    if surf_trial.get_width() <= max_width or len(shortened) == 0:
                        surf = surf_trial
                        rect = surf.get_rect()
                        rect.midleft = (10, y_offset)
                        break
                self.screen.blit(surf, rect)
            else:
                self.screen.blit(surf, rect)
            y_offset += surf.get_height() + 2

        pygame.display.flip()

    # --- Mod selection interface ----------------------------------------
    def choose_mod(self) -> None:
        """Display the mod selection screen and wait for the player choice.

        Players are shown a random subset of up to three available mods.  Use
        the arrow keys to change selection and press Enter or click to
        apply.  Press Esc to skip selecting a mod.
        """
        # Determine which mods are currently available
        avail = [m for m in self.mods if self.is_mod_available(m)]
        if not avail:
            return
        # Choose a random subset of up to three mods
        random.shuffle(avail)
        options = avail[: min(3, len(avail))]
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
                        selected_index = (selected_index + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        options[selected_index].apply_func()
                        selecting = False
                    elif event.key == pygame.K_ESCAPE:
                        selecting = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for idx, mod in enumerate(options):
                        rect = self.get_mod_rect(idx)
                        if rect.collidepoint(mx, my):
                            mod.apply_func()
                            selecting = False
                            selected_index = idx
                            break
            # Draw selection screen
            self.screen.fill(self.BG_COLOR)
            title = self.font_large.render("Choose a Mod", True, self.TEXT_COLOR)
            title_rect = title.get_rect(center=(width // 2, 60))
            self.screen.blit(title, title_rect)
            # Draw each mod with highlight
            for i, mod in enumerate(options):
                rect = self.get_mod_rect(i)
                if i == selected_index:
                    pygame.draw.rect(self.screen, self.ACTIVE_MOD_COLOR, rect)
                # Mod name
                name_surf = self.font_small.render(mod.name, True, self.TEXT_COLOR)
                name_rect = name_surf.get_rect(midleft=(rect.x + 10, rect.centery - 10))
                self.screen.blit(name_surf, name_rect)
                # Wrap description text into multiple lines if necessary
                import textwrap
                desc_lines = textwrap.wrap(mod.description, width=35)
                for j, dl in enumerate(desc_lines[:2]):
                    desc_surf = self.font_small.render(dl, True, self.TEXT_COLOR)
                    desc_rect = desc_surf.get_rect(midleft=(rect.x + 10, rect.centery + 10 + j * 18))
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

    def is_mod_available(self, mod: Mod) -> bool:
        """Return True if the mod can still have an effect given current state.

        Some mods only make sense to apply once (e.g. time pressure) or
        up to a limit (e.g. board enlargement).  This method prevents
        offering mods that are already active or cannot have further
        effect.  Random blockers can always be applied again.
        """
        if mod.apply_func is self.mod_add_row_col:
            return self.board_size < self.MAX_SIZE
        if mod.apply_func is self.mod_time_pressure:
            return self.time_limit is None
        if mod.apply_func is self.mod_swap_symbols:
            # Do not allow swap_symbols if already active or double-turn is active to avoid conflict
            return (not self.swap_symbols) and (not self.double_turn)
        if mod.apply_func is self.mod_gravity:
            return not self.gravity
        if mod.apply_func is self.mod_wild_card:
            return not self.wild_card_active
        if mod.apply_func is self.mod_double_turn:
            # Do not allow double-turn if already active or swap_symbols is active to avoid conflict
            return (not self.double_turn) and (not self.swap_symbols)
        if mod.apply_func is self.mod_remove_opponent:
            return not self.remove_opponent
        if mod.apply_func is self.mod_diagonal_only:
            return not self.diagonal_only
        if mod.apply_func is self.mod_teleport:
            return not self.teleport
        # random blockers can always be applied
        return True

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