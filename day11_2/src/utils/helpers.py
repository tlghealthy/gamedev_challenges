import pygame
import math
from typing import Tuple, List

def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate distance between two points"""
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

def point_in_rect(point: Tuple[float, float], rect: pygame.Rect) -> bool:
    """Check if point is inside rectangle"""
    return rect.left <= point[0] <= rect.right and rect.top <= point[1] <= rect.bottom

def grid_to_pixel(grid_pos: Tuple[int, int], grid_size: int) -> Tuple[int, int]:
    """Convert grid position to pixel position"""
    return (grid_pos[0] * grid_size + grid_size // 2, grid_pos[1] * grid_size + grid_size // 2)

def pixel_to_grid(pixel_pos: Tuple[int, int], grid_size: int) -> Tuple[int, int]:
    """Convert pixel position to grid position"""
    return (pixel_pos[0] // grid_size, pixel_pos[1] // grid_size)

def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between start and end values"""
    return start + (end - start) * t

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))

def draw_circle(surface: pygame.Surface, color: Tuple[int, int, int], 
                center: Tuple[int, int], radius: int, width: int = 0):
    """Draw circle with optional border"""
    pygame.draw.circle(surface, color, center, radius, width)

def draw_triangle(surface: pygame.Surface, color: Tuple[int, int, int], 
                  center: Tuple[int, int], size: int, rotation: float = 0):
    """Draw equilateral triangle with optional rotation"""
    # Base triangle points
    points = [
        (center[0], center[1] - size),
        (center[0] - size * 0.866, center[1] + size * 0.5),
        (center[0] + size * 0.866, center[1] + size * 0.5)
    ]
    
    # Apply rotation if specified
    if rotation != 0:
        angle_rad = math.radians(rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        rotated_points = []
        for point in points:
            # Translate to origin
            dx = point[0] - center[0]
            dy = point[1] - center[1]
            
            # Rotate
            new_x = dx * cos_a - dy * sin_a
            new_y = dx * sin_a + dy * cos_a
            
            # Translate back
            rotated_points.append((center[0] + new_x, center[1] + new_y))
        
        points = rotated_points
    
    pygame.draw.polygon(surface, color, points)

def draw_square(surface: pygame.Surface, color: Tuple[int, int, int], 
                center: Tuple[int, int], size: int, filled: bool = True, thickness: int = 0):
    """Draw square centered on point with optional border"""
    rect = pygame.Rect(center[0] - size//2, center[1] - size//2, size, size)
    if filled:
        pygame.draw.rect(surface, color, rect)
    if thickness > 0:
        pygame.draw.rect(surface, color, rect, thickness) 