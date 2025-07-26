#!/usr/bin/env python3
"""
Simple run script for Abstract Tower Defense
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Run the game
if __name__ == "__main__":
    from main import main
    main() 