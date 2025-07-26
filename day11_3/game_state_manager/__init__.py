"""
Pygame-CE Game State Manager

A lightweight, drop-in game state manager for pygame-ce projects.
"""

from .manager import GameStateManager
from .state import BaseState

__version__ = "1.0.0"
__all__ = ["GameStateManager", "BaseState"] 