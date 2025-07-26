import pygame
from typing import Dict, List, Tuple
from utils.helpers import draw_circle, draw_triangle, draw_square, grid_to_pixel
from utils.constants import *

class Renderer:
    def __init__(self, screen: pygame.Surface, settings: Dict):
        self.screen = screen
        self.settings = settings
        self.colors = settings['colors']
        self.grid_size = settings['gameplay']['grid_size']
        
        # Font for text
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def render(self, game_state, menu_system):
        """Main render function"""
        self.screen.fill(self.colors['background'])
        
        if game_state.state == MENU:
            self.render_menu(menu_system)
        elif game_state.state in [PLAYING, PAUSED]:
            self.render_game(game_state)
        elif game_state.state == GAME_OVER:
            self.render_game_over(game_state)
        elif game_state.state == VICTORY:
            self.render_victory(game_state)
    
    def render_menu(self, menu_system):
        """Render main menu"""
        # Title
        title = self.font.render("Abstract Tower Defense", True, self.colors['text'])
        title_rect = title.get_rect(center=(self.screen.get_width()//2, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions - moved up and spaced better
        instructions = [
            "Press 1, 2, 3 to select tower type",
            "Click to place towers",
            "Click towers to upgrade",
            "Press SPACE to start waves",
            "Press ESC to cancel selection",
            "Hover to see tower range preview",
            "Complete levels to progress automatically",
            "Press N during victory to skip timer",
            "",
            "Debug Keys (Ctrl + key):",
            "Ctrl+9: Skip to next level",
            "Ctrl+M: Add money",
            "Ctrl+K: Kill all enemies"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.colors['text'])
            text_rect = text.get_rect(center=(self.screen.get_width()//2, 220 + i * 25))
            self.screen.blit(text, text_rect)
    
    def render_game(self, game_state):
        """Render game elements"""
        # Draw grid
        self.draw_grid()
        
        # Draw path
        self.draw_path(game_state.path_waypoints)
        
        # Draw goal
        self.draw_goal(game_state.path_waypoints[-1] if game_state.path_waypoints else (0, 0))
        
        # Draw placeable tiles
        self.draw_placeable_tiles(game_state.placeable_tiles, game_state.selected_tower_type)
        
        # Draw towers
        for tower in game_state.towers:
            self.draw_tower(tower)
        
        # Draw enemies
        for enemy in game_state.enemies:
            self.draw_enemy(enemy)
        
        # Draw tower projectiles
        self.draw_projectiles(game_state.towers)
        
        # Draw UI
        self.draw_hud(game_state)
        
        # Draw tower selection preview
        if game_state.selected_tower_type and game_state.hovered_grid_pos:
            self.draw_tower_preview(game_state.hovered_grid_pos, game_state.selected_tower_type)
    
    def draw_grid(self):
        """Draw grid lines"""
        for x in range(0, self.screen.get_width(), self.grid_size):
            pygame.draw.line(self.screen, self.colors['grid'], (x, 0), (x, self.screen.get_height()))
        for y in range(0, self.screen.get_height(), self.grid_size):
            pygame.draw.line(self.screen, self.colors['grid'], (0, y), (self.screen.get_width(), y))
    
    def draw_path(self, waypoints: List[Tuple[int, int]]):
        """Draw enemy path"""
        if len(waypoints) < 2:
            return
        
        # Convert waypoints to pixel positions
        pixel_waypoints = [grid_to_pixel(wp, self.grid_size) for wp in waypoints]
        
        # Draw path lines
        for i in range(len(pixel_waypoints) - 1):
            pygame.draw.line(self.screen, self.colors['path'], 
                           pixel_waypoints[i], pixel_waypoints[i + 1], 3)
        
        # Draw waypoint markers
        for wp in pixel_waypoints:
            draw_circle(self.screen, self.colors['path'], wp, 5)
    
    def draw_goal(self, goal_pos: Tuple[int, int]):
        """Draw goal area"""
        pixel_pos = grid_to_pixel(goal_pos, self.grid_size)
        draw_circle(self.screen, self.colors['goal'], pixel_pos, self.grid_size // 2)
    
    def draw_placeable_tiles(self, placeable_tiles: set, selected_tower_type: str):
        """Draw placeable tile indicators"""
        for tile in placeable_tiles:
            pixel_pos = grid_to_pixel(tile, self.grid_size)
            color = self.colors['ui_button_hover'] if selected_tower_type else self.colors['ui_button']
            draw_circle(self.screen, color, pixel_pos, self.grid_size // 3, 2)
    
    def draw_tower(self, tower):
        """Draw tower"""
        pixel_pos = grid_to_pixel(tower.grid_pos, self.grid_size)
        color = self.colors[f'tower_{tower.tower_type}']
        
        if tower.tower_type == TOWER_RED:
            draw_circle(self.screen, color, pixel_pos, self.grid_size // 3)
        elif tower.tower_type == TOWER_BLUE:
            draw_triangle(self.screen, color, pixel_pos, self.grid_size // 3)
        elif tower.tower_type == TOWER_GREEN:
            draw_square(self.screen, color, pixel_pos, self.grid_size // 2)
        
        # Draw range indicator if enabled
        if self.settings['gameplay']['tower_range_visual']:
            range_surface = pygame.Surface((tower.range * 2, tower.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (*color, 50), (tower.range, tower.range), tower.range)
            self.screen.blit(range_surface, (pixel_pos[0] - tower.range, pixel_pos[1] - tower.range))
    
    def draw_enemy(self, enemy):
        """Draw enemy"""
        pixel_pos = (int(enemy.x), int(enemy.y))
        color = self.colors[f'enemy_{enemy.enemy_type}']
        
        # Check if enemy reached goal
        if enemy.reached_goal():
            # Show goal color for enemies that reached the end
            color = self.colors['goal']
        else:
            # Adjust color based on health
            health_ratio = enemy.health / enemy.max_health
            color = tuple(int(c * health_ratio) for c in color)
        
        if enemy.enemy_type == ENEMY_SMALL:
            draw_circle(self.screen, color, pixel_pos, enemy.size)
        elif enemy.enemy_type == ENEMY_MEDIUM:
            draw_triangle(self.screen, color, pixel_pos, enemy.size)
        elif enemy.enemy_type == ENEMY_LARGE:
            draw_square(self.screen, color, pixel_pos, enemy.size)
        elif enemy.enemy_type == ENEMY_FAST:
            # Fast enemies are small diamonds
            draw_triangle(self.screen, color, pixel_pos, enemy.size)
            # Add a second triangle rotated 180 degrees for diamond effect
            draw_triangle(self.screen, color, pixel_pos, enemy.size, rotation=180)
        elif enemy.enemy_type == ENEMY_TANK:
            # Tank enemies are large squares with extra visual weight
            draw_square(self.screen, color, pixel_pos, enemy.size)
            # Add a border to make them look more armored
            border_color = tuple(max(0, c - 50) for c in color)
            draw_square(self.screen, border_color, pixel_pos, enemy.size, filled=False, thickness=2)
    
    def draw_projectiles(self, towers):
        """Draw tower projectiles"""
        for tower in towers:
            for projectile in tower.get_projectiles():
                # Draw line from tower to target
                start_pos = projectile['start_pos']
                end_pos = projectile['end_pos']
                color = projectile['color']
                
                # Make the line thicker and more visible
                pygame.draw.line(self.screen, color, start_pos, end_pos, 3)
                
                # Add a small glow effect at the target end
                pygame.draw.circle(self.screen, color, (int(end_pos[0]), int(end_pos[1])), 5)
    
    def draw_tower_preview(self, grid_pos: Tuple[int, int], tower_type: str):
        """Draw tower preview when hovering"""
        pixel_pos = grid_to_pixel(grid_pos, self.grid_size)
        color = (*self.colors[f'tower_{tower_type}'], 128)  # Semi-transparent
        
        # Get tower range from settings
        tower_range = self.settings['towers'][tower_type]['range']
        
        # Draw range indicator (more transparent than placed towers)
        range_surface = pygame.Surface((tower_range * 2, tower_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*self.colors[f'tower_{tower_type}'], 30), (tower_range, tower_range), tower_range)
        self.screen.blit(range_surface, (pixel_pos[0] - tower_range, pixel_pos[1] - tower_range))
        
        # Draw tower preview
        if tower_type == TOWER_RED:
            draw_circle(self.screen, color, pixel_pos, self.grid_size // 3)
        elif tower_type == TOWER_BLUE:
            draw_triangle(self.screen, color, pixel_pos, self.grid_size // 3)
        elif tower_type == TOWER_GREEN:
            draw_square(self.screen, color, pixel_pos, self.grid_size // 2)
    
    def draw_hud(self, game_state):
        """Draw heads-up display"""
        # Money
        money_text = self.font.render(f"Money: {game_state.economy.money}", True, self.colors['text'])
        self.screen.blit(money_text, (10, 10))
        
        # Lives
        lives_text = self.font.render(f"Lives: {game_state.economy.lives}", True, self.colors['text'])
        self.screen.blit(lives_text, (10, 40))
        
        # Debug: Print HUD values occasionally
        if pygame.time.get_ticks() % 1000 < 16:
            print(f"HUD DISPLAY: Money={game_state.economy.money}, Lives={game_state.economy.lives}")
        
        # Level
        level_text = self.font.render(f"Level: {game_state.current_level}", True, self.colors['text'])
        self.screen.blit(level_text, (10, 70))
        
        # Wave info
        wave_text = self.font.render(f"Wave: {game_state.wave_manager.current_wave}/{game_state.wave_manager.total_waves}", 
                                   True, self.colors['text'])
        self.screen.blit(wave_text, (10, 100))
        
        # Selected tower
        if game_state.selected_tower_type:
            tower_name = self.settings['towers'][game_state.selected_tower_type]['name']
            tower_cost = self.settings['towers'][game_state.selected_tower_type]['cost']
            selected_text = self.font.render(f"Selected: {tower_name} (${tower_cost})", True, self.colors['text'])
            self.screen.blit(selected_text, (10, 130))
    
    def render_game_over(self, game_state):
        """Render game over screen"""
        self.render_game(game_state)  # Show game state in background
        
        # Overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        text = self.font.render("GAME OVER", True, (255, 100, 100))
        text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(text, text_rect)
    
    def render_victory(self, game_state):
        """Render victory screen"""
        self.render_game(game_state)  # Show game state in background
        
        # Overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        text = self.font.render("LEVEL COMPLETE!", True, (100, 255, 100))
        text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 50))
        self.screen.blit(text, text_rect)
        
        # Level info
        if game_state.current_level < game_state.max_level:
            next_level_text = self.font.render(f"Next Level: {game_state.current_level + 1}", True, (255, 255, 255))
            next_level_rect = next_level_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(next_level_text, next_level_rect)
            
            # Instructions
            instruction_text = self.small_font.render("Press N to continue or wait for auto-progression", True, (200, 200, 200))
            instruction_rect = instruction_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
            self.screen.blit(instruction_text, instruction_rect)
            
            # Timer
            remaining_time = max(0, game_state.victory_delay - game_state.victory_timer)
            timer_text = self.small_font.render(f"Auto-progress in {remaining_time:.1f}s", True, (150, 150, 150))
            timer_rect = timer_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 80))
            self.screen.blit(timer_text, timer_rect)
        else:
            # Game complete
            complete_text = self.font.render("GAME COMPLETE!", True, (255, 255, 100))
            complete_rect = complete_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(complete_text, complete_rect)
            
            instruction_text = self.small_font.render("Press N to return to menu", True, (200, 200, 200))
            instruction_rect = instruction_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
            self.screen.blit(instruction_text, instruction_rect) 