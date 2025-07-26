import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 4
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
FONT_SIZE = 48

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 100))
pygame.display.set_caption("Sliding Tile Puzzle")
font = pygame.font.Font(None, FONT_SIZE)
small_font = pygame.font.Font(None, 32)

class PuzzleGame:
    def __init__(self):
        self.grid = []
        self.empty_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.moves = 0
        self.solved = False
        self.initialize_grid()
        
    def initialize_grid(self):
        # Create solved grid
        self.grid = [[i + j * GRID_SIZE + 1 for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        self.grid[GRID_SIZE - 1][GRID_SIZE - 1] = 0  # Empty space
        
        # Shuffle the grid
        for _ in range(100):
            self.random_move()
            
        # Ensure puzzle is solvable
        if not self.is_solvable():
            # Make it solvable by swapping two tiles
            if self.grid[0][0] != 1:
                self.grid[0][0], self.grid[0][1] = self.grid[0][1], self.grid[0][0]
            else:
                self.grid[0][1], self.grid[0][2] = self.grid[0][2], self.grid[0][1]
    
    def random_move(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        valid_moves = []
        
        for dx, dy in directions:
            new_x, new_y = self.empty_pos[0] + dx, self.empty_pos[1] + dy
            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                valid_moves.append((new_x, new_y))
        
        if valid_moves:
            move_x, move_y = random.choice(valid_moves)
            self.grid[self.empty_pos[0]][self.empty_pos[1]] = self.grid[move_x][move_y]
            self.grid[move_x][move_y] = 0
            self.empty_pos = (move_x, move_y)
    
    def is_solvable(self):
        # Count inversions
        flat_grid = [self.grid[i][j] for i in range(GRID_SIZE) for j in range(GRID_SIZE) if self.grid[i][j] != 0]
        inversions = 0
        
        for i in range(len(flat_grid)):
            for j in range(i + 1, len(flat_grid)):
                if flat_grid[i] > flat_grid[j]:
                    inversions += 1
        
        # For 4x4 grid, puzzle is solvable if inversions + empty row from bottom is odd
        empty_row = GRID_SIZE - 1 - self.empty_pos[0]
        return (inversions + empty_row) % 2 == 1
    
    def move_tile(self, dx, dy):
        new_x, new_y = self.empty_pos[0] + dx, self.empty_pos[1] + dy
        
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            # Swap tiles
            self.grid[self.empty_pos[0]][self.empty_pos[1]] = self.grid[new_x][new_y]
            self.grid[new_x][new_y] = 0
            self.empty_pos = (new_x, new_y)
            self.moves += 1
            
            # Check if solved
            self.check_solved()
    
    def check_solved(self):
        expected = 1
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if i == GRID_SIZE - 1 and j == GRID_SIZE - 1:
                    if self.grid[i][j] != 0:
                        return
                else:
                    if self.grid[i][j] != expected:
                        return
                    expected += 1
        self.solved = True
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw grid
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x, y = j * CELL_SIZE, i * CELL_SIZE
                value = self.grid[i][j]
                
                if value == 0:  # Empty space
                    pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    pygame.draw.rect(screen, BLUE, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
                    
                    # Draw number
                    text = font.render(str(value), True, WHITE)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    screen.blit(text, text_rect)
        
        # Draw info
        info_y = WINDOW_SIZE + 10
        moves_text = small_font.render(f"Moves: {self.moves}", True, BLACK)
        screen.blit(moves_text, (10, info_y))
        
        if self.solved:
            solved_text = small_font.render("PUZZLE SOLVED!", True, GREEN)
            screen.blit(solved_text, (WINDOW_SIZE // 2 - 100, info_y))
        else:
            controls_text = small_font.render("Use arrow keys to move tiles", True, BLACK)
            screen.blit(controls_text, (WINDOW_SIZE // 2 - 150, info_y))

def main():
    game = PuzzleGame()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN and not game.solved:
                if event.key == pygame.K_UP:
                    game.move_tile(1, 0)
                elif event.key == pygame.K_DOWN:
                    game.move_tile(-1, 0)
                elif event.key == pygame.K_LEFT:
                    game.move_tile(0, 1)
                elif event.key == pygame.K_RIGHT:
                    game.move_tile(0, -1)
                elif event.key == pygame.K_r:
                    game = PuzzleGame()
        
        game.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 