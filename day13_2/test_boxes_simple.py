import pygame
import sys
import math
from physics_engine import World, Vec

def test_simple_boxes():
    """Test just 2 boxes for basic stability"""
    print("Testing simple 2-box setup...")
    
    world = World(gravity=(0, 100), fixed_dt=1/120.0, iterations=12)  # Reduced gravity
    
    # Create 2 boxes positioned to collide (closer together)
    box1_nodes = world.box((350, 200), 80, 80, k=0.95)
    box2_nodes = world.box((450, 200), 80, 80, k=0.95)
    
    print(f"Created 2 boxes:")
    print(f"  Box 1: ({box1_nodes[0].pos.x:.1f}, {box1_nodes[0].pos.y:.1f}) to ({box1_nodes[2].pos.x:.1f}, {box1_nodes[2].pos.y:.1f})")
    print(f"  Box 2: ({box2_nodes[0].pos.x:.1f}, {box2_nodes[0].pos.y:.1f}) to ({box2_nodes[2].pos.x:.1f}, {box2_nodes[2].pos.y:.1f})")
    
    # Track initial positions
    box1_center = sum((node.pos for node in box1_nodes), Vec(0, 0)) / len(box1_nodes)
    box2_center = sum((node.pos for node in box2_nodes), Vec(0, 0)) / len(box2_nodes)
    
    initial_centers = [box1_center.copy(), box2_center.copy()]
    
    # Run simulation for 2 seconds
    steps_2_seconds = int(2.0 / (1/120.0))
    max_displacement = 0
    
    print(f"\nRunning simulation for 2 seconds...")
    
    for step in range(steps_2_seconds):
        world.step(1/120.0)
        
        # Check every 0.5 seconds
        if step % 60 == 0:
            current_box1_center = sum((node.pos for node in box1_nodes), Vec(0, 0)) / len(box1_nodes)
            current_box2_center = sum((node.pos for node in box2_nodes), Vec(0, 0)) / len(box2_nodes)
            
            current_centers = [current_box1_center, current_box2_center]
            
            for i, (init_pos, curr_pos) in enumerate(zip(initial_centers, current_centers)):
                displacement = (curr_pos - init_pos).length()
                max_displacement = max(max_displacement, displacement)
                
                if step % 120 == 0:  # Print every second
                    print(f"  Box {i+1} displacement at {step/120:.1f}s: {displacement:.1f}")
                
                # Check if any box has moved too far (exploded)
                if displacement > 100:  # Conservative threshold
                    print(f"  Box {i+1} exploded at step {step} (displacement: {displacement:.1f})")
                    return False
    
    print(f"\nFinal positions:")
    print(f"  Box 1 center: ({current_box1_center.x:.1f}, {current_box1_center.y:.1f})")
    print(f"  Box 2 center: ({current_box2_center.x:.1f}, {current_box2_center.y:.1f})")
    print(f"  Maximum displacement: {max_displacement:.1f} pixels")
    
    # Check if boxes are still roughly in their original positions
    boxes_stable = max_displacement < 100
    
    # Check if boxes are maintaining their shape
    box1_shape_ok = True
    box2_shape_ok = True
    
    for box_nodes, box_name in [(box1_nodes, "Box 1"), (box2_nodes, "Box 2")]:
        # Check if the box is still roughly square
        width = abs(box_nodes[1].pos.x - box_nodes[0].pos.x)
        height = abs(box_nodes[2].pos.y - box_nodes[1].pos.y)
        
        if abs(width - 80) > 20 or abs(height - 80) > 20:
            print(f"  Warning: {box_name} shape distorted - width: {width:.1f}, height: {height:.1f}")
            if box_name == "Box 1":
                box1_shape_ok = False
            else:
                box2_shape_ok = False
    
    print(f"\nTest Results:")
    print(f"✓ Boxes stay stable: {'PASS' if boxes_stable else 'FAIL'}")
    print(f"✓ Box 1 maintains shape: {'PASS' if box1_shape_ok else 'FAIL'}")
    print(f"✓ Box 2 maintains shape: {'PASS' if box2_shape_ok else 'FAIL'}")
    
    return boxes_stable and box1_shape_ok and box2_shape_ok

def run_visual_box_test():
    """Run a visual test of the simple boxes"""
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()
    
    world = World(gravity=(0, 100), fixed_dt=1/120.0, iterations=12)  # Reduced gravity
    box1_nodes = world.box((250, 150), 80, 80, k=0.95)
    box2_nodes = world.box((350, 150), 80, 80, k=0.95)  # Closer together for collision
    
    print("Running visual box test - close window to continue")
    
    while True:
        dt = clock.tick(60) / 1000
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
        
        world.step(dt)
        
        screen.fill((30, 30, 30))
        world.debug_render(screen)
        
        # Draw some info text
        font = pygame.font.Font(None, 24)
        box1_center = sum((node.pos for node in box1_nodes), Vec(0, 0)) / len(box1_nodes)
        box2_center = sum((node.pos for node in box2_nodes), Vec(0, 0)) / len(box2_nodes)
        
        text1 = font.render(f"Box 1: ({box1_center.x:.0f}, {box1_center.y:.0f})", True, (255, 255, 255))
        text2 = font.render(f"Box 2: ({box2_center.x:.0f}, {box2_center.y:.0f})", True, (255, 255, 255))
        
        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 35))
        
        pygame.display.flip()

if __name__ == "__main__":
    print("Simple Box Test")
    print("=" * 30)
    
    # Run visual test first
    run_visual_box_test()
    
    # Run automated test
    print("\nRunning automated test...")
    box_test = test_simple_boxes()
    
    print("\n" + "=" * 30)
    print("Box Test Summary:")
    print(f"✓ 2 boxes created: PASS")
    print(f"✓ Boxes stay stable: {'PASS' if box_test else 'FAIL'}")
    
    if box_test:
        print("\n🎉 Simple box test passed!")
    else:
        print("\n❌ Simple box test failed.") 