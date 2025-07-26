import pygame
import pymunk
import sys
import random
import math
import json

# Load settings
try:
    with open('settings.json', 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    print("settings.json not found, using default values")
    settings = {
        "physics": {
            "player": {"elasticity": 0.3, "friction": 0.8, "mass": 1, "radius": 25},
            "obstacles": {"elasticity": 0.3, "friction": 0.8, "mass": 2, "radius": 15},
            "boundaries": {"elasticity": 0.3, "friction": 0.9, "thickness": 20},
            "gravity": {"x": 0, "y": 900}
        },
        "launch": {"magnitude_multiplier": 0.3, "max_magnitude": 200, "velocity_threshold": 10},
        "display": {"width": 900, "height": 600, "fps": 60}
    }

# Load levels
try:
    with open('levels.json', 'r') as f:
        level_data = json.load(f)
except FileNotFoundError:
    print("levels.json not found, using default levels")
    level_data = {
        "levels": [
            {"name": "Level 1", "player_start": [225, 520], "goal": [675, 80], "walls": []},
            {"name": "Level 2", "player_start": [225, 520], "goal": [675, 80], "walls": []},
            {"name": "Level 3", "player_start": [225, 520], "goal": [675, 80], "walls": []}
        ]
    }

# Constants from settings
WIDTH = settings["display"]["width"]
HEIGHT = settings["display"]["height"]
FPS = settings["display"]["fps"]
BG_COLOR = (30, 30, 40)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Game Prototype")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 16)

# Physics
space = pymunk.Space()
space.gravity = (settings["physics"]["gravity"]["x"], settings["physics"]["gravity"]["y"])

# Boundaries
AABB_COLOR = (100, 100, 200)
def add_static_boundaries(space):
    thickness = settings["physics"]["boundaries"]["thickness"]
    static_lines = [
        pymunk.Segment(space.static_body, (0, HEIGHT-thickness), (WIDTH, HEIGHT-thickness), thickness),  # floor
        pymunk.Segment(space.static_body, (0, thickness), (WIDTH, thickness), thickness),  # ceiling
        pymunk.Segment(space.static_body, (thickness, 0), (thickness, HEIGHT), thickness),  # left wall
        pymunk.Segment(space.static_body, (WIDTH-thickness, 0), (WIDTH-thickness, HEIGHT), thickness),  # right wall
    ]
    for line in static_lines:
        line.elasticity = settings["physics"]["boundaries"]["elasticity"]
        line.friction = settings["physics"]["boundaries"]["friction"]
    space.add(*static_lines)
    return static_lines

static_boundaries = add_static_boundaries(space)

CIRCLE_COLORS = [(220, 80, 80), (80, 220, 120), (80, 120, 220), (220, 220, 80)]
CAPSULE_COLORS = [(200, 100, 200), (100, 200, 200), (200, 200, 100)]

def add_circle(space, pos, radius=None, mass=None):
    if radius is None:
        radius = settings["physics"]["player"]["radius"]
    if mass is None:
        mass = settings["physics"]["player"]["mass"]
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    # Prevent rotation for player
    body.angular_velocity = 0
    body.moment = float('inf')  # Infinite moment of inertia = no rotation
    shape = pymunk.Circle(body, radius)
    shape.elasticity = settings["physics"]["player"]["elasticity"]
    shape.friction = settings["physics"]["player"]["friction"]
    shape.color = random.choice(CIRCLE_COLORS)
    space.add(body, shape)
    return shape

def draw_circle(surface, shape):
    pos = int(shape.body.position.x), int(shape.body.position.y)
    pygame.draw.circle(surface, shape.color, pos, int(shape.radius))
    
    # Debug line to show rotation
    angle = shape.body.angle
    end_x = pos[0] + math.cos(angle) * shape.radius
    end_y = pos[1] + math.sin(angle) * shape.radius
    pygame.draw.line(surface, (255, 255, 255), pos, (int(end_x), int(end_y)), 3)

def add_capsule(space, pos, a_offset, b_offset, radius=None, mass=None):
    if radius is None:
        radius = settings["physics"]["obstacles"]["radius"]
    if mass is None:
        mass = settings["physics"]["obstacles"]["mass"]
    a = (pos[0] + a_offset[0], pos[1] + a_offset[1])
    b = (pos[0] + b_offset[0], pos[1] + b_offset[1])
    moment = pymunk.moment_for_segment(mass, a, b, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Segment(body, a_offset, b_offset, radius)
    shape.elasticity = settings["physics"]["obstacles"]["elasticity"]
    shape.friction = settings["physics"]["obstacles"]["friction"]
    shape.color = random.choice(CAPSULE_COLORS)
    space.add(body, shape)
    return shape

def draw_capsule(surface, shape):
    body = shape.body
    a = body.position + shape.a.rotated(body.angle)
    b = body.position + shape.b.rotated(body.angle)
    pygame.draw.line(surface, shape.color, a, b, int(shape.radius*2))
    pygame.draw.circle(surface, shape.color, (int(a.x), int(a.y)), int(shape.radius))
    pygame.draw.circle(surface, shape.color, (int(b.x), int(b.y)), int(shape.radius))

# Test shapes for visual confirmation
# shapes = []
# shapes.append(add_circle(space, (WIDTH//2, HEIGHT//2-100)))
# shapes.append(add_capsule(space, (WIDTH//2-100, HEIGHT//2-50), (-40,0), (40,0)))

def draw_boundaries(surface, boundaries):
    for seg in boundaries:
        body = seg.body
        pv1 = body.position + seg.a.rotated(body.angle)
        pv2 = body.position + seg.b.rotated(body.angle)
        pygame.draw.line(surface, AABB_COLOR, pv1, pv2, int(seg.radius*2))

def draw_text(surface, text, y, color=(255,255,255)):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        txt = font.render(line, True, color)
        rect = txt.get_rect(center=(WIDTH//2, y + i*40))
        surface.blit(txt, rect)

PLAYER_COLOR = (255, 200, 80)
GOAL_COLOR = (80, 255, 120)
NUM_LEVELS = len(level_data["levels"])

class Player:
    def __init__(self, space, pos):
        self.shape = add_circle(space, pos, radius=settings["physics"]["player"]["radius"], mass=settings["physics"]["player"]["mass"])
        self.shape.color = PLAYER_COLOR
        self.launched = False
        self.move_count = 0
    def reset(self, pos):
        self.shape.body.position = pos
        self.shape.body.velocity = (0,0)
        self.launched = False
        self.move_count = 0

class Goal:
    def __init__(self, pos, radius=30):
        self.pos = pos
        self.radius = radius
    def draw(self, surface):
        pygame.draw.circle(surface, GOAL_COLOR, (int(self.pos[0]), int(self.pos[1])), self.radius)

def check_goal(player, goal):
    dist = (player.shape.body.position - pymunk.Vec2d(*goal.pos)).length
    return dist < (player.shape.radius + goal.radius)

def add_static_wall(space, start_pos, end_pos, thickness=10):
    """Add a static wall segment to the space"""
    wall = pymunk.Segment(space.static_body, start_pos, end_pos, thickness)
    wall.elasticity = settings["physics"]["boundaries"]["elasticity"]
    wall.friction = settings["physics"]["boundaries"]["friction"]
    wall.color = (150, 150, 150)  # Gray color for walls
    space.add(wall)
    return wall

def draw_walls(surface, walls):
    """Draw all static walls"""
    for wall in walls:
        body = wall.body
        pv1 = body.position + wall.a.rotated(body.angle)
        pv2 = body.position + wall.b.rotated(body.angle)
        pygame.draw.line(surface, wall.color, pv1, pv2, int(wall.radius*2))

def setup_level(space, level):
    # Remove all non-boundary segments (walls) and all dynamic bodies
    for s in list(space.shapes):
        # Remove all segments that are not static boundaries
        if isinstance(s, pymunk.Segment) and s not in static_boundaries:
            space.remove(s)
        elif not isinstance(s, pymunk.Segment):
            space.remove(s, s.body)
    
    walls = []
    obstacles = []
    
    # Get level data
    level_info = level_data["levels"][level]
    player_start = level_info["player_start"]
    goal_pos = level_info["goal"]
    
    # Create player and goal
    player = Player(space, player_start)
    goal = Goal(goal_pos)
    
    # Add walls
    for wall_data in level_info["walls"]:
        walls.append(add_static_wall(space, wall_data["start"], wall_data["end"]))
    
    # Add obstacles if they exist
    if "obstacles" in level_info:
        for obs_data in level_info["obstacles"]:
            if obs_data["type"] == "circle":
                obstacles.append(add_circle(space, obs_data["pos"]))
            elif obs_data["type"] == "capsule":
                start = obs_data["pos"]
                end = obs_data["end"]
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                obstacles.append(add_capsule(space, start, (0, 0), (dx, dy)))
    
    gravity_zones = []
    
    return player, goal, obstacles, gravity_zones, walls

def draw_gravity_zones(surface, zones):
    for rect in zones:
        pygame.draw.rect(surface, (80, 120, 255), rect, border_radius=10)

def player_in_gravity_zone(player, zones):
    for rect in zones:
        if rect.collidepoint(int(player.shape.body.position.x), int(player.shape.body.position.y)):
            return True
    return False

def move_obstacles(obstacles, t):
    for i, obs in enumerate(obstacles):
        # Oscillate horizontally
        obs.body.position = (WIDTH//2 + 120 * (1 if i%2==0 else -1) * (0.5 * (1 + math.sin(t + i))), HEIGHT//2)
        obs.body.velocity = (0,0)

import math

class LevelEditor:
    def __init__(self):
        self.active = False
        self.dragging = None
        self.drag_offset = (0, 0)
        self.selected_object = None
        self.selected_point = None  # For wall endpoints
        self.placing_wall = False
        self.placing_circle = False
        self.placing_capsule = False
        self.placement_start = None
    
    def toggle(self):
        self.active = not self.active
        if self.active:
            print("Level Editor: ON - Drag objects with mouse, Ctrl+S to save")
            print("1: Add wall, 2: Add circle, 3: Add capsule")
        else:
            print("Level Editor: OFF")
    
    def handle_events(self, events, player, goal, walls, level):
        if not self.active:
            return
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.placing_wall = True
                    self.placing_circle = False
                    self.placing_capsule = False
                    print("Click to place wall start point")
                elif event.key == pygame.K_2:
                    self.placing_wall = False
                    self.placing_circle = True
                    self.placing_capsule = False
                    print("Click to place circle")
                elif event.key == pygame.K_3:
                    self.placing_wall = False
                    self.placing_circle = False
                    self.placing_capsule = True
                    print("Click to place capsule start point")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.placing_wall or self.placing_circle or self.placing_capsule:
                    self.handle_placement(mouse_pos, walls, level)
                else:
                    self.start_drag(mouse_pos, player, goal, walls)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.stop_drag()
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                self.update_drag(mouse_pos)
    
    def handle_placement(self, mouse_pos, walls, level):
        if self.placing_wall:
            if self.placement_start is None:
                self.placement_start = mouse_pos
                print("Click to place wall end point")
            else:
                # Create new wall
                new_wall = add_static_wall(space, self.placement_start, mouse_pos)
                walls.append(new_wall)
                # Add to level data
                level_data["levels"][level]["walls"].append({
                    "start": list(self.placement_start),
                    "end": list(mouse_pos)
                })
                self.placement_start = None
                self.placing_wall = False
                print("Wall added!")
        elif self.placing_circle:
            # Create new circle obstacle
            new_circle = add_circle(space, mouse_pos)
            # Add to level data (you might want to add an obstacles array to level_data)
            if "obstacles" not in level_data["levels"][level]:
                level_data["levels"][level]["obstacles"] = []
            level_data["levels"][level]["obstacles"].append({
                "type": "circle",
                "pos": list(mouse_pos)
            })
            self.placing_circle = False
            print("Circle added!")
        elif self.placing_capsule:
            if self.placement_start is None:
                self.placement_start = mouse_pos
                print("Click to place capsule end point")
            else:
                # Create new capsule
                dx = mouse_pos[0] - self.placement_start[0]
                dy = mouse_pos[1] - self.placement_start[1]
                new_capsule = add_capsule(space, self.placement_start, (0, 0), (dx, dy))
                # Add to level data
                if "obstacles" not in level_data["levels"][level]:
                    level_data["levels"][level]["obstacles"] = []
                level_data["levels"][level]["obstacles"].append({
                    "type": "capsule",
                    "pos": list(self.placement_start),
                    "end": list(mouse_pos)
                })
                self.placement_start = None
                self.placing_capsule = False
                print("Capsule added!")

    def start_drag(self, mouse_pos, player, goal, walls):
        # Check if clicking on player
        player_dist = math.sqrt((mouse_pos[0] - player.shape.body.position.x)**2 + 
                               (mouse_pos[1] - player.shape.body.position.y)**2)
        if player_dist < player.shape.radius:
            self.dragging = "player"
            self.drag_offset = (mouse_pos[0] - player.shape.body.position.x, 
                               mouse_pos[1] - player.shape.body.position.y)
            return
        
        # Check if clicking on goal
        goal_dist = math.sqrt((mouse_pos[0] - goal.pos[0])**2 + 
                             (mouse_pos[1] - goal.pos[1])**2)
        if goal_dist < goal.radius:
            self.dragging = "goal"
            self.drag_offset = (mouse_pos[0] - goal.pos[0], 
                               mouse_pos[1] - goal.pos[1])
            return
        
        # Check if clicking on wall endpoints
        for i, wall in enumerate(walls):
            body = wall.body
            start_pos = body.position + wall.a.rotated(body.angle)
            end_pos = body.position + wall.b.rotated(body.angle)
            
            start_dist = math.sqrt((mouse_pos[0] - start_pos.x)**2 + 
                                  (mouse_pos[1] - start_pos.y)**2)
            end_dist = math.sqrt((mouse_pos[0] - end_pos.x)**2 + 
                                (mouse_pos[1] - end_pos.y)**2)
            
            if start_dist < 15:
                self.dragging = f"wall_{i}_start"
                self.drag_offset = (mouse_pos[0] - start_pos.x, mouse_pos[1] - start_pos.y)
                return
            elif end_dist < 15:
                self.dragging = f"wall_{i}_end"
                self.drag_offset = (mouse_pos[0] - end_pos.x, mouse_pos[1] - end_pos.y)
                return
    
    def stop_drag(self):
        self.dragging = None
        self.drag_offset = (0, 0)
    
    def update_drag(self, mouse_pos):
        if not self.dragging:
            return
        
        new_x = mouse_pos[0] - self.drag_offset[0]
        new_y = mouse_pos[1] - self.drag_offset[1]
        
        if self.dragging == "player":
            self.dragging = "player"  # Keep reference
            # Update will be handled in main loop
        elif self.dragging == "goal":
            self.dragging = "goal"  # Keep reference
            # Update will be handled in main loop
        elif self.dragging.startswith("wall_"):
            parts = self.dragging.split("_")
            wall_index = int(parts[1])
            point_type = parts[2]
            # Update will be handled in main loop
    
    def draw_debug(self, surface, player, goal, walls):
        if not self.active:
            return
        
        # Draw drag handles
        pygame.draw.circle(surface, (255, 255, 0), 
                          (int(player.shape.body.position.x), int(player.shape.body.position.y)), 
                          int(player.shape.radius) + 5, 2)
        
        pygame.draw.circle(surface, (255, 255, 0), 
                          (int(goal.pos[0]), int(goal.pos[1])), 
                          goal.radius + 5, 2)
        
        for wall in walls:
            body = wall.body
            start_pos = body.position + wall.a.rotated(body.angle)
            end_pos = body.position + wall.b.rotated(body.angle)
            
            pygame.draw.circle(surface, (255, 255, 0), 
                              (int(start_pos.x), int(start_pos.y)), 5)
            pygame.draw.circle(surface, (255, 255, 0), 
                              (int(end_pos.x), int(end_pos.y)), 5)
        
        # Draw placement preview
        if self.placing_wall and self.placement_start:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(surface, (255, 255, 0), self.placement_start, mouse_pos, 2)
            pygame.draw.circle(surface, (255, 255, 0), self.placement_start, 3)
        elif self.placing_capsule and self.placement_start:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(surface, (255, 255, 0), self.placement_start, mouse_pos, 2)
            pygame.draw.circle(surface, (255, 255, 0), self.placement_start, 3)
        
        # Draw editor info
        info_text = "EDITOR MODE - Drag objects, Ctrl+S to save"
        if self.placing_wall:
            info_text += " | Placing wall..."
        elif self.placing_circle:
            info_text += " | Click to place circle"
        elif self.placing_capsule:
            info_text += " | Placing capsule..."
        info_surface = small_font.render(info_text, True, (255, 255, 0))
        surface.blit(info_surface, (10, HEIGHT - 30))
        
        # Draw controls info
        controls_text = "1: Add wall, 2: Add circle, 3: Add capsule"
        controls_surface = small_font.render(controls_text, True, (255, 255, 0))
        surface.blit(controls_surface, (10, HEIGHT - 50))

def save_levels_to_file():
    """Save current level data back to levels.json"""
    try:
        with open('levels.json', 'w') as f:
            json.dump(level_data, f, indent=4)
        print("Levels saved to levels.json")
    except Exception as e:
        print(f"Error saving levels: {e}")

def main():
    running = True
    level = 0
    show_level_intro = True
    intro_timer = 0
    intro_duration = 2.5  # seconds
    player, goal, obstacles, gravity_zones, walls = setup_level(space, level)
    mouse_down = False
    drag_start = None
    t = 0
    
    # Level editor
    editor = LevelEditor()
    
    while running:
        dt = clock.tick(FPS) / 1000
        t += dt
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and show_level_intro:
                    show_level_intro = False
                elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    editor.toggle()
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_levels_to_file()
            
            if not show_level_intro and not player.launched and not editor.active:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_down = True
                    drag_start = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and mouse_down:
                    drag_end = pygame.mouse.get_pos()
                    # Calculate direction vector from drag start to end
                    dx = drag_end[0] - drag_start[0]
                    dy = drag_end[1] - drag_start[1]
                    
                    # Calculate drag distance for magnitude
                    drag_distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Normalize direction and apply magnitude
                    if drag_distance > 0:
                        # Normalize the direction vector
                        dx = dx / drag_distance
                        dy = dy / drag_distance
                        
                        # Apply impulse with magnitude based on drag distance
                        impulse_magnitude = min(drag_distance * settings["launch"]["magnitude_multiplier"], settings["launch"]["max_magnitude"])
                        impulse_x = dx * impulse_magnitude
                        impulse_y = dy * impulse_magnitude
                        
                        player.shape.body.apply_impulse_at_local_point((impulse_x, impulse_y))
                        player.launched = True
                        player.move_count += 1
                    mouse_down = False
        
        # Handle editor events
        editor.handle_events(events, player, goal, walls, level)
        
        # Update editor drag
        if editor.dragging and editor.active:
            mouse_pos = pygame.mouse.get_pos()
            new_x = mouse_pos[0] - editor.drag_offset[0]
            new_y = mouse_pos[1] - editor.drag_offset[1]
            
            if editor.dragging == "player":
                player.shape.body.position = (new_x, new_y)
                # Update level data
                level_data["levels"][level]["player_start"] = [new_x, new_y]
            elif editor.dragging == "goal":
                goal.pos = [new_x, new_y]
                # Update level data
                level_data["levels"][level]["goal"] = [new_x, new_y]
            elif editor.dragging.startswith("wall_"):
                parts = editor.dragging.split("_")
                wall_index = int(parts[1])
                point_type = parts[2]
                
                # Remove old wall from space and list robustly
                old_wall = walls[wall_index]
                if old_wall in space.shapes:
                    space.remove(old_wall)
                wall_data = level_data["levels"][level]["walls"][wall_index]
                start = wall_data["start"]
                end = wall_data["end"]
                if point_type == "start":
                    start = [new_x, new_y]
                    wall_data["start"] = [new_x, new_y]
                elif point_type == "end":
                    end = [new_x, new_y]
                    wall_data["end"] = [new_x, new_y]
                # Create new wall and replace in list
                new_wall = add_static_wall(space, start, end)
                walls[wall_index] = new_wall
        
        screen.fill(BG_COLOR)
        if show_level_intro:
            level_name = level_data["levels"][level]["name"]
            intro_text = f"{level_name}\n\nPress SPACE to start."
            draw_text(screen, intro_text, HEIGHT//3)
            intro_timer += dt
            if intro_timer > intro_duration:
                show_level_intro = False
        else:
            draw_boundaries(screen, static_boundaries)
            draw_walls(screen, walls)
            goal.draw(screen)
            for obs in obstacles:
                draw_capsule(screen, obs)
            draw_gravity_zones(screen, gravity_zones)
            draw_circle(screen, player.shape)
            
            # Draw move counter
            move_text = f"Moves: {player.move_count}"
            move_surface = font.render(move_text, True, (255, 255, 255))
            screen.blit(move_surface, (10, 10))
            
            # Draw editor debug info
            editor.draw_debug(screen, player, goal, walls)
            
            # Draw drag line
            if mouse_down and drag_start and not editor.active:
                mouse_pos = pygame.mouse.get_pos()
                pygame.draw.line(screen, (255,255,255), drag_start, mouse_pos, 3)
            
            # Move obstacles
            if level >= 1:
                move_obstacles(obstacles, t)
            # Gravity zone effect
            if level == 2:
                if player_in_gravity_zone(player, gravity_zones):
                    space.gravity = (900, 0)
                else:
                    space.gravity = (settings["physics"]["gravity"]["x"], settings["physics"]["gravity"]["y"])
            # Reset launch ability when ball stops moving
            if player.launched:
                velocity = player.shape.body.velocity
                if abs(velocity.x) < settings["launch"]["velocity_threshold"] and abs(velocity.y) < settings["launch"]["velocity_threshold"]:
                    player.launched = False
            # Win condition
            if check_goal(player, goal):
                level += 1
                if level < NUM_LEVELS:
                    player, goal, obstacles, gravity_zones, walls = setup_level(space, level)
                    show_level_intro = True
                    intro_timer = 0
                    space.gravity = (settings["physics"]["gravity"]["x"], settings["physics"]["gravity"]["y"])
                else:
                    draw_text(screen, "Congratulations!\nYou completed all levels!", HEIGHT//2)
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    running = False
        pygame.display.flip()
        if not show_level_intro:
            space.step(dt)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 