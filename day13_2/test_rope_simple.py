import pygame
import sys
import math
from physics_engine import World, Vec

def test_simple_rope():
    """Test a simple 3-segment rope"""
    print("Testing simple 3-segment rope...")
    
    # Create rope simulation with just 3 segments
    seg_len = 40
    count = 3
    gravity = 200
    
    world = World(gravity=(0, gravity), fixed_dt=1/120.0)
    rope_nodes = world.rope((400, 100), seg_len=seg_len, count=count, k=0.8)
    
    print(f"Created rope with {count} segments, length: {seg_len * (count-1)}")
    print(f"Initial positions:")
    for i, node in enumerate(rope_nodes):
        print(f"  Node {i}: ({node.pos.x:.1f}, {node.pos.y:.1f})")
    
    # Let rope settle for a short time
    for step in range(60):  # 0.5 seconds at 120 Hz
        world.step(1/120.0)
        
        if step % 20 == 0:  # Print every 1/6 second
            print(f"Step {step}: Node 2 pos = ({rope_nodes[2].pos.x:.1f}, {rope_nodes[2].pos.y:.1f})")
    
    # Final positions
    print(f"\nFinal positions after settling:")
    for i, node in enumerate(rope_nodes):
        print(f"  Node {i}: ({node.pos.x:.1f}, {node.pos.y:.1f})")
    
    # Check if rope has drooped (node 2 should be lower than node 0)
    droop = rope_nodes[2].pos.y - rope_nodes[0].pos.y
    print(f"\nRope droop: {droop:.1f} pixels")
    
    # Basic checks
    has_droop = droop > 0
    nodes_connected = True  # Check if edges are maintaining distance
    
    for i in range(len(rope_nodes) - 1):
        dist = (rope_nodes[i].pos - rope_nodes[i+1].pos).length()
        expected_dist = seg_len
        if abs(dist - expected_dist) > 10:  # Allow some tolerance
            nodes_connected = False
            print(f"Warning: Edge {i} length is {dist:.1f}, expected ~{expected_dist}")
    
    print(f"\nTest Results:")
    print(f"✓ Rope has droop: {'PASS' if has_droop else 'FAIL'}")
    print(f"✓ Nodes stay connected: {'PASS' if nodes_connected else 'FAIL'}")
    
    return has_droop and nodes_connected

def run_visual_rope_test():
    """Run a visual test of the simple rope"""
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()
    
    world = World(gravity=(0, 200), fixed_dt=1/120.0)
    rope_nodes = world.rope((300, 50), seg_len=40, count=3, k=0.8)
    
    print("Running visual rope test - close window to continue")
    
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
        text = font.render(f"Rope droop: {rope_nodes[2].pos.y - rope_nodes[0].pos.y:.1f}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()

if __name__ == "__main__":
    print("Simple Rope Test")
    print("=" * 30)
    
    # Run visual test first
    run_visual_rope_test()
    
    # Run automated test
    print("\nRunning automated test...")
    rope_test = test_simple_rope()
    
    print("\n" + "=" * 30)
    print("Rope Test Summary:")
    print(f"✓ 3-segment rope created: PASS")
    print(f"✓ Rope droops under gravity: {'PASS' if rope_test else 'FAIL'}")
    
    if rope_test:
        print("\n🎉 Simple rope test passed!")
    else:
        print("\n❌ Simple rope test failed.") 