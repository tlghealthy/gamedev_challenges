"""
Comprehensive tests for the game state manager.
"""

import unittest
import pygame
from unittest.mock import Mock, patch
from ..manager import GameStateManager
from ..state import BaseState


class TestState(BaseState):
    """Test state for unit testing."""
    
    def __init__(self, name="TestState"):
        super().__init__(name)
        self.enter_called = False
        self.exit_called = False
        self.update_called = False
        self.render_called = False
        self.cleanup_called = False
        self.enter_data = None
    
    def enter(self, data):
        self.enter_called = True
        self.enter_data = data
    
    def exit(self):
        self.exit_called = True
    
    def update(self, dt):
        self.update_called = True
    
    def render(self, surface):
        self.render_called = True
    
    def cleanup(self):
        self.cleanup_called = True


class TestGameStateManager(unittest.TestCase):
    """Test cases for GameStateManager."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.manager = GameStateManager()
        self.screen = pygame.Surface((800, 600))
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_initial_state(self):
        """Test initial manager state."""
        self.assertEqual(self.manager.state_count, 0)
        self.assertIsNone(self.manager.current_state)
    
    def test_push_state(self):
        """Test pushing a state onto the stack."""
        state = TestState("TestState1")
        self.manager.push_state(state)
        
        # Process transitions
        self.manager.update(0.016)
        
        self.assertEqual(self.manager.state_count, 1)
        self.assertEqual(self.manager.current_state, state)
        self.assertTrue(state.enter_called)
        self.assertEqual(state.enter_data, {})
    
    def test_push_state_with_data(self):
        """Test pushing a state with data."""
        state = TestState("TestState1")
        data = {"level": 1, "score": 100}
        self.manager.push_state(state, data)
        
        # Process transitions
        self.manager.update(0.016)
        
        self.assertEqual(state.enter_data, data)
    
    def test_pop_state(self):
        """Test popping a state from the stack."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        
        self.manager.push_state(state1)
        self.manager.push_state(state2)
        self.manager.update(0.016)  # Process first push
        
        self.manager.pop_state()
        self.manager.update(0.016)  # Process pop
        
        self.assertEqual(self.manager.state_count, 1)
        self.assertEqual(self.manager.current_state, state1)
        self.assertTrue(state2.exit_called)
        self.assertTrue(state2.cleanup_called)
    
    def test_pop_state_with_data(self):
        """Test popping a state with data passed to previous state."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        
        self.manager.push_state(state1)
        self.manager.push_state(state2)
        self.manager.update(0.016)  # Process first push
        
        data = {"result": "success"}
        self.manager.pop_state(data)
        self.manager.update(0.016)  # Process pop
        
        # State1 should receive the data when re-entering
        self.assertEqual(state1.enter_data, data)
    
    def test_switch_state(self):
        """Test switching to a new state."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        
        self.manager.push_state(state1)
        self.manager.update(0.016)  # Process first push
        
        self.manager.switch_state(state2)
        self.manager.update(0.016)  # Process switch
        
        self.assertEqual(self.manager.state_count, 1)
        self.assertEqual(self.manager.current_state, state2)
        self.assertTrue(state1.exit_called)
        self.assertTrue(state1.cleanup_called)
        self.assertTrue(state2.enter_called)
    
    def test_clear_states(self):
        """Test clearing all states."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        
        self.manager.push_state(state1)
        self.manager.push_state(state2)
        self.manager.update(0.016)  # Process pushes
        
        self.manager.clear_states()
        self.manager.update(0.016)  # Process clear
        
        self.assertEqual(self.manager.state_count, 0)
        self.assertIsNone(self.manager.current_state)
        self.assertTrue(state1.exit_called)
        self.assertTrue(state1.cleanup_called)
        self.assertTrue(state2.exit_called)
        self.assertTrue(state2.cleanup_called)
    
    def test_clear_states_with_new_state(self):
        """Test clearing states and setting a new one."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        new_state = TestState("NewState")
        
        self.manager.push_state(state1)
        self.manager.push_state(state2)
        self.manager.update(0.016)  # Process pushes
        
        data = {"fresh": True}
        self.manager.clear_states(new_state, data)
        self.manager.update(0.016)  # Process clear
        
        self.assertEqual(self.manager.state_count, 1)
        self.assertEqual(self.manager.current_state, new_state)
        self.assertEqual(new_state.enter_data, data)
    
    def test_update_and_render(self):
        """Test update and render methods."""
        state = TestState("TestState")
        self.manager.push_state(state)
        self.manager.update(0.016)  # Process push
        
        # Reset flags
        state.update_called = False
        state.render_called = False
        
        # Test update and render
        self.manager.update(0.016)
        self.manager.render(self.screen)
        
        self.assertTrue(state.update_called)
        self.assertTrue(state.render_called)
    
    def test_shared_data(self):
        """Test shared data functionality."""
        key = "test_key"
        value = "test_value"
        
        self.manager.set_shared_data(key, value)
        self.assertEqual(self.manager.get_shared_data(key), value)
        self.assertEqual(self.manager.get_shared_data("nonexistent", "default"), "default")
    
    def test_has_state(self):
        """Test checking if a state type exists in the stack."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        
        self.manager.push_state(state1)
        self.manager.push_state(state2)
        self.manager.update(0.016)  # Process pushes
        
        self.assertTrue(self.manager.has_state(TestState))
        # TestState inherits from BaseState, so this should be True
        self.assertTrue(self.manager.has_state(BaseState))
    
    def test_get_state(self):
        """Test getting a state of a specific type."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        
        self.manager.push_state(state1)
        self.manager.push_state(state2)
        self.manager.update(0.016)  # Process pushes
        
        # Should return the topmost state of the type
        found_state = self.manager.get_state(TestState)
        self.assertEqual(found_state, state2)
    
    def test_state_initialization(self):
        """Test that states are properly initialized."""
        state = TestState("TestState")
        self.assertFalse(state._initialized)
        
        self.manager.push_state(state)
        self.manager.update(0.016)  # Process push
        
        self.assertTrue(state._initialized)
    
    def test_manager_reference(self):
        """Test that states get the manager reference."""
        state = TestState("TestState")
        self.assertIsNone(state.manager)
        
        self.manager.push_state(state)
        self.manager.update(0.016)  # Process push
        
        self.assertEqual(state.manager, self.manager)
    
    def test_multiple_transitions(self):
        """Test handling multiple transitions in one frame."""
        state1 = TestState("TestState1")
        state2 = TestState("TestState2")
        state3 = TestState("TestState3")
        
        # Queue multiple transitions
        self.manager.push_state(state1)
        self.manager.push_state(state2)
        self.manager.pop_state()
        self.manager.switch_state(state3)
        
        # Process all transitions
        self.manager.update(0.016)
        
        # Debug: print the actual state count and current state
        print(f"State count: {self.manager.state_count}")
        print(f"Current state: {self.manager.current_state.name if self.manager.current_state else 'None'}")
        print(f"All states: {[s.name for s in self.manager._states]}")
        
        # After pop and switch, we should have state3 as the only state
        self.assertEqual(self.manager.state_count, 1)
        self.assertEqual(self.manager.current_state, state3)
    
    def test_empty_stack_operations(self):
        """Test operations on empty state stack."""
        state = TestState("TestState")
        
        # Pop on empty stack should do nothing
        self.manager.pop_state()
        self.manager.update(0.016)
        self.assertEqual(self.manager.state_count, 0)
        
        # Update and render on empty stack should not crash
        self.manager.update(0.016)
        self.manager.render(self.screen)


class TestBaseState(unittest.TestCase):
    """Test cases for BaseState."""
    
    def test_state_creation(self):
        """Test state creation with default and custom names."""
        state1 = TestState()
        self.assertEqual(state1.name, "TestState")
        
        state2 = TestState("CustomName")
        self.assertEqual(state2.name, "CustomName")
    
    def test_lifecycle_methods(self):
        """Test that lifecycle methods can be called without errors."""
        state = TestState()
        
        # These should not raise exceptions
        state.init()
        state.enter({"test": "data"})
        state.update(0.016)
        state.render(pygame.Surface((100, 100)))
        state.exit()
        state.cleanup()


if __name__ == "__main__":
    unittest.main() 