import pygame
import random
import sys

# --- Game Configurations ---
WINDOW_SIZE = (640, 480)
GRID_SIZE = 20
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE[1] // GRID_SIZE
FPS = 12

# Colors
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]
BG_COLOR = (30, 30, 30)
SNAKE_OUTLINE = (200, 200, 200)
BLOCK_OUTLINE = (80, 80, 80)
ORB_OUTLINE = (255, 255, 255)

# --- Game Entities ---
class Snake:
    def __init__(self, pos, color):
        self.body = [pos]
        self.direction = (1, 0)
        self.grow = False
        self.color = color

    def head(self):
        return self.body[0]

    def move(self):
        new_head = (self.head()[0] + self.direction[0], self.head()[1] + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def set_direction(self, dir):
        # Prevent reversing
        if (dir[0] == -self.direction[0] and dir[1] == -self.direction[1]):
            return
        self.direction = dir

    def grow_snake(self):
        self.grow = True

    def collides_with_self(self):
        return self.head() in self.body[1:]

class Block:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

class Orb:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

# --- Game Functions ---
def random_empty_cell(occupied):
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if pos not in occupied:
            return pos

def place_blocks(num_blocks, occupied):
    blocks = []
    for _ in range(num_blocks):
        color = random.choice(COLORS)
        pos = random_empty_cell(occupied)
        blocks.append(Block(pos, color))
        occupied.add(pos)
    return blocks

def place_orb(occupied):
    color = random.choice(COLORS)
    pos = random_empty_cell(occupied)
    return Orb(pos, color)

def draw_grid(surface):
    for x in range(0, WINDOW_SIZE[0], GRID_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, WINDOW_SIZE[1]))
    for y in range(0, WINDOW_SIZE[1], GRID_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (WINDOW_SIZE[0], y))

def draw_snake(surface, snake):
    for i, segment in enumerate(snake.body):
        rect = pygame.Rect(segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, snake.color, rect)
        pygame.draw.rect(surface, SNAKE_OUTLINE, rect, 2)

def draw_blocks(surface, blocks):
    for block in blocks:
        rect = pygame.Rect(block.pos[0]*GRID_SIZE, block.pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, block.color, rect)
        pygame.draw.rect(surface, BLOCK_OUTLINE, rect, 2)

def draw_orb(surface, orb):
    center = (orb.pos[0]*GRID_SIZE + GRID_SIZE//2, orb.pos[1]*GRID_SIZE + GRID_SIZE//2)
    pygame.draw.circle(surface, orb.color, center, GRID_SIZE//2 - 2)
    pygame.draw.circle(surface, ORB_OUTLINE, center, GRID_SIZE//2 - 2, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Color Serpent Breakout")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    def reset_game():
        occupied = set()
        snake = Snake((GRID_WIDTH//2, GRID_HEIGHT//2), random.choice(COLORS))
        occupied.add(snake.head())
        blocks = place_blocks(18, occupied)
        orb = place_orb(occupied | {b.pos for b in blocks} | set(snake.body))
        return snake, blocks, orb, False, False

    snake, blocks, orb, game_over, win = reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    snake, blocks, orb, game_over, win = reset_game()
                if not game_over and not win:
                    if event.key == pygame.K_UP:
                        snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.set_direction((1, 0))

        if not game_over and not win:
            snake.move()
            head = snake.head()
            # Check self collision
            if snake.collides_with_self():
                game_over = True
            # Check block collision
            for block in blocks:
                if head == block.pos:
                    if block.color == snake.color:
                        blocks.remove(block)
                        break
                    else:
                        game_over = True
                        break
            # Check orb collision
            if head == orb.pos:
                snake.grow_snake()
                snake.color = orb.color
                occupied = set(snake.body) | {b.pos for b in blocks}
                if len(occupied) < GRID_WIDTH * GRID_HEIGHT:
                    orb = place_orb(occupied)
                else:
                    orb = None
            # Win condition
            if not blocks:
                win = True

        # Draw everything
        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_blocks(screen, blocks)
        if orb:
            draw_orb(screen, orb)
        draw_snake(screen, snake)

        if game_over:
            text = font.render("Game Over! Press R to restart.", True, (255, 255, 255))
            screen.blit(text, (WINDOW_SIZE[0]//2 - text.get_width()//2, WINDOW_SIZE[1]//2 - 20))
        elif win:
            text = font.render("You Win! Press R to play again.", True, (255, 255, 0))
            screen.blit(text, (WINDOW_SIZE[0]//2 - text.get_width()//2, WINDOW_SIZE[1]//2 - 20))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main() 