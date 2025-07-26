# Testing Strategy for Tic-Tac-Toe Evolution

## Overview

This document outlines the testing strategy to prevent win condition bugs and ensure the game works correctly with all modifier combinations.

## Test Files

### 1. `test_win_conditions.py` - Comprehensive Unit Tests
- **Purpose**: Thorough testing of all win condition scenarios
- **When to run**: Before any release, after major changes
- **Command**: `python test_win_conditions.py`

**Test Categories:**
- Standard 3x3 (3 in a row required)
- 3x3 with horizontal win reduction (2 in a row)
- 3x3 with vertical win reduction (2 in a row)
- 3x3 with diagonal win reduction (2 in a row)
- Multiple reductions combined
- 4x4 board scenarios
- Edge cases (minimum win requirements, mixed players, empty board)
- Winning line coordinate accuracy

### 2. `quick_test.py` - Fast Verification
- **Purpose**: Quick verification of critical win conditions
- **When to run**: After small changes, during development
- **Command**: `python quick_test.py`

**Tests:**
- Standard 3x3 win
- 3x3 with horizontal reduction
- 3x3 with diagonal reduction
- 4x4 with horizontal reduction
- No win with insufficient pieces

## Testing Best Practices

### 1. Test-Driven Development
- Write tests before implementing new features
- Ensure tests fail before the feature is implemented
- Verify tests pass after implementation

### 2. Test Coverage
Always test:
- **Standard scenarios**: 3x3 with no modifiers
- **Reduced win conditions**: Each type (horizontal, vertical, diagonal)
- **Multiple modifiers**: Combinations of reductions
- **Different board sizes**: 3x3, 4x4, etc.
- **Edge cases**: Minimum win requirements, mixed players
- **Winning line accuracy**: Correct coordinates returned

### 3. Test Scenarios to Add
When adding new features, consider testing:
- **New modifiers**: How they interact with win conditions
- **Board expansion**: Win conditions after board size changes
- **Modifier stacking**: Multiple instances of the same modifier
- **Game state transitions**: Win detection during different phases

## Common Bug Patterns to Test

### 1. Win Detection Issues
- **Problem**: Win not detected when it should be
- **Test**: Place exactly the required number of pieces in a row
- **Example**: 2 pieces in a row with horizontal reduction on 3x3

### 2. Wrong Player Returned
- **Problem**: Returns None or wrong player
- **Test**: Verify the correct player is returned for each win type
- **Example**: Check that Player.X wins when X places winning pieces

### 3. Winning Line Coordinates
- **Problem**: Wrong coordinates returned for highlighting
- **Test**: Verify winning line coordinates match the actual winning pieces
- **Example**: Check that [(0,0), (0,1)] is returned for 2 pieces in top row

### 4. Modifier Interactions
- **Problem**: Modifiers interfere with win detection
- **Test**: Apply modifiers and verify win detection still works
- **Example**: Test win detection with adjacent modifiers active

## Running Tests

### Quick Development Cycle
```bash
# After making changes
python quick_test.py

# If quick tests pass, run full suite
python test_win_conditions.py
```

### Before Committing
```bash
# Run all tests
python test_win_conditions.py
python quick_test.py

# Check for any failures
# Fix any issues before committing
```

### Continuous Integration
Consider adding these tests to your CI/CD pipeline:
- Run tests on every commit
- Fail the build if any tests fail
- Generate test coverage reports

## Debugging Failed Tests

### 1. Isolate the Problem
- Run individual test methods
- Add print statements to see board state
- Check win requirements vs. actual pieces placed

### 2. Common Debugging Steps
```python
# Add to failing test
print(f"Board state:")
for row in range(board.size):
    print([board.get_cell(row, col) for col in range(board.size)])

print(f"Win requirements: {board.get_win_requirements()}")
print(f"Expected winner: {expected_winner}")
print(f"Actual winner: {actual_winner}")
```

### 3. Visual Verification
- Use the visual tests in `test_win_conditions.py`
- Print board states and manually verify
- Check that winning line coordinates are correct

## Extending the Test Suite

### Adding New Tests
1. **Identify the scenario** you want to test
2. **Write a test method** in `TestWinConditions`
3. **Set up the board state** with the required pieces
4. **Apply any modifiers** needed
5. **Assert the expected result**
6. **Add to quick_test.py** if it's a critical scenario

### Example: Adding a New Test
```python
def test_new_scenario(self):
    """Test description of what this tests"""
    # Set up board
    self.board = Board(4)
    self.board.reduce_horizontal_win_requirement(2)  # Need 2 in a row
    
    # Place pieces
    self.board.make_move(0, 0, Player.X)
    self.board.make_move(0, 1, Player.X)
    
    # Assert result
    self.assertEqual(self.board.check_winner(), Player.X)
    self.assertEqual(self.board.get_winning_line(), [(0, 0), (0, 1)])
```

## Maintenance

### Regular Tasks
- **Weekly**: Run full test suite
- **Before releases**: Run all tests and verify coverage
- **After bug fixes**: Add tests to prevent regression
- **When adding features**: Extend test suite accordingly

### Test Maintenance
- Keep tests up to date with code changes
- Remove obsolete tests
- Refactor tests for clarity
- Add comments explaining complex test scenarios

This testing strategy should help prevent the win condition bugs we encountered and ensure the game remains stable as you add new features. 