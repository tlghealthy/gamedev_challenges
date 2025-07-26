"""
Base state class for the game state manager.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pygame


class BaseState(ABC):
    """Abstract base class for all game states."""
    
    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__
        self._manager: Optional['GameStateManager'] = None
        self._initialized = False
    
    def init(self) -> None:
        """Initialize state resources. Called once when state is created."""
        self._initialized = True
    
    def enter(self, data: Dict[str, Any]) -> None:
        """Called when entering the state. Override for custom logic."""
        pass
    
    def update(self, dt: float) -> None:
        """Update state logic. Called every frame."""
        pass
    
    def render(self, surface: pygame.Surface) -> None:
        """Render state to surface. Called every frame."""
        pass
    
    def exit(self) -> None:
        """Called when exiting the state. Override for custom logic."""
        pass
    
    def cleanup(self) -> None:
        """Clean up state resources. Called when state is destroyed."""
        pass
    
    @property
    def manager(self) -> Optional['GameStateManager']:
        """Get the state manager instance."""
        return self._manager
    
    def set_manager(self, manager: 'GameStateManager') -> None:
        """Set the state manager reference."""
        self._manager = manager 