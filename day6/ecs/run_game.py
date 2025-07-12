#!/usr/bin/env python3
"""
Standalone runner for the ECS-based Fighting Platformer
Run this file directly to start the game.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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