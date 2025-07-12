#!/usr/bin/env python3
"""
ECS-based 2-Player Fighting Platformer
A demonstration of Entity-Component-System architecture for game development.
"""

from game import Game

def main():
    """Main entry point for the game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 