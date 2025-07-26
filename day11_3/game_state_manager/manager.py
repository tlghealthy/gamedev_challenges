"""
Core game state manager for pygame-ce projects.
"""

from typing import Dict, Any, List, Optional, Type
import pygame
from .state import BaseState


class GameStateManager:
    """Manages game states with stack-based navigation."""
    
    def __init__(self):
        self._states: List[BaseState] = []
        self._shared_data: Dict[str, Any] = {}
        self._pending_transitions: List[Dict[str, Any]] = []
    
    def push_state(self, state: BaseState, data: Dict[str, Any] = None) -> None:
        """Push a new state onto the stack."""
        if not state._initialized:
            state.init()
        state.set_manager(self)
        self._pending_transitions.append({
            'action': 'push',
            'state': state,
            'data': data or {}
        })
    
    def pop_state(self, data: Dict[str, Any] = None) -> None:
        """Pop the current state from the stack."""
        if len(self._states) > 0:
            self._pending_transitions.append({
                'action': 'pop',
                'data': data or {}
            })
    
    def switch_state(self, state: BaseState, data: Dict[str, Any] = None) -> None:
        """Switch to a new state, replacing the current one."""
        if not state._initialized:
            state.init()
        state.set_manager(self)
        self._pending_transitions.append({
            'action': 'switch',
            'state': state,
            'data': data or {}
        })
    
    def clear_states(self, new_state: BaseState = None, data: Dict[str, Any] = None) -> None:
        """Clear all states and optionally set a new one."""
        if new_state and not new_state._initialized:
            new_state.init()
        if new_state:
            new_state.set_manager(self)
        self._pending_transitions.append({
            'action': 'clear',
            'state': new_state,
            'data': data or {}
        })
    
    def update(self, dt: float) -> None:
        """Update the current state and process transitions."""
        self._process_transitions()
        if self._states:
            self._states[-1].update(dt)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the current state."""
        if self._states:
            self._states[-1].render(surface)
    
    def _process_transitions(self) -> None:
        """Process pending state transitions."""
        for transition in self._pending_transitions:
            action = transition['action']
            
            if action == 'push':
                if self._states:
                    self._states[-1].exit()
                self._states.append(transition['state'])
                transition['state'].enter(transition['data'])
                
            elif action == 'pop':
                if self._states:
                    old_state = self._states.pop()
                    old_state.exit()
                    old_state.cleanup()
                if self._states:
                    self._states[-1].enter(transition['data'])
                
            elif action == 'switch':
                # Replace the entire stack with the new state
                for state in self._states:
                    state.exit()
                    state.cleanup()
                self._states.clear()
                self._states.append(transition['state'])
                transition['state'].enter(transition['data'])
                
            elif action == 'clear':
                for state in self._states:
                    state.exit()
                    state.cleanup()
                self._states.clear()
                if transition['state']:
                    self._states.append(transition['state'])
                    transition['state'].enter(transition['data'])
        
        self._pending_transitions.clear()
    
    @property
    def current_state(self) -> Optional[BaseState]:
        """Get the current active state."""
        return self._states[-1] if self._states else None
    
    @property
    def state_count(self) -> int:
        """Get the number of states in the stack."""
        return len(self._states)
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """Get shared data by key."""
        return self._shared_data.get(key, default)
    
    def set_shared_data(self, key: str, value: Any) -> None:
        """Set shared data by key."""
        self._shared_data[key] = value
    
    def has_state(self, state_type: Type[BaseState]) -> bool:
        """Check if a state of the given type exists in the stack."""
        return any(isinstance(state, state_type) for state in self._states)
    
    def get_state(self, state_type: Type[BaseState]) -> Optional[BaseState]:
        """Get the first state of the given type from the stack."""
        for state in reversed(self._states):
            if isinstance(state, state_type):
                return state
        return None 