---
description: Suggest or write tests for the codebase
---

# Test Helper

Help create comprehensive tests for better code quality and confidence.

## Overview

This command helps with testing by:
1. Suggesting what to test when no input is provided
2. Writing tests when given a description
3. Identifying untested code
4. Improving test coverage
5. Following testing best practices

## Usage

### Without Arguments
```
/test
```
Analyzes the codebase and suggests what needs testing.

### With Arguments
```
/test <description>
```
Writes tests for the described functionality.

## Task List

### Mode 1: Suggest Tests (No Arguments)

When called without arguments, analyze the project and suggest tests:

#### Step 1: Check Current Coverage

Run coverage analysis:

**Python**:
```bash
pytest --cov=src --cov-report=term-missing
# or
coverage run -m pytest
coverage report --show-missing
```

**JavaScript**:
```bash
npm test -- --coverage
# or
jest --coverage
```

#### Step 2: Identify Gaps

Look for:
- **Untested files**: Files with 0% coverage
- **Low coverage**: Files below 80% coverage
- **Missing edge cases**: Functions with partial coverage
- **Critical paths**: Important code without tests
- **Recent changes**: New code without tests

#### Step 3: Prioritize Suggestions

Rank by importance:

**Priority 1: Critical & Untested**
- Core business logic
- Security-sensitive code
- Data processing functions
- API endpoints
- Error handling

**Priority 2: Low Coverage**
- Functions below 80% coverage
- Missing edge cases
- Error paths not tested
- Boundary conditions

**Priority 3: Nice to Have**
- Utility functions
- Helper methods
- UI components
- Documentation examples

#### Step 4: Present Suggestions

Format suggestions clearly:

```
📊 Test Coverage Analysis

**Overall Coverage**: 75% (Target: 90%+)

**Priority 1: Critical Untested Code**
1. src/auth/login.py (0% coverage)
   - Test successful login
   - Test invalid credentials
   - Test account lockout
   - Test session management

2. src/payments/process.py (0% coverage)
   - Test successful payment
   - Test payment failure
   - Test refund handling
   - Test edge cases (zero amount, negative, etc.)

**Priority 2: Low Coverage Areas**
3. src/api/users.py (45% coverage)
   - Missing: Error handling tests
   - Missing: Validation tests
   - Missing: Edge cases

4. src/utils/parser.py (60% coverage)
   - Missing: Malformed input tests
   - Missing: Empty input tests

**Priority 3: Improvements**
5. Add integration tests for user workflow
6. Add performance tests for data processing
7. Add security tests for authentication

Which would you like me to tackle first?
```

### Mode 2: Write Tests (With Arguments)

When given a description, write appropriate tests:

#### Step 1: Understand What to Test

Parse the description to identify:
- **What**: Function, class, module, or feature
- **Where**: File location
- **Type**: Unit, integration, or end-to-end test
- **Scenarios**: What cases to cover

#### Step 2: Locate the Code

Find the code to test:
```bash
# Search for the function/class
rg "def function_name" src/
rg "class ClassName" src/
```

Read and understand:
- Function signature
- Parameters and types
- Return values
- Side effects
- Dependencies

#### Step 3: Identify Test Cases

For each function/feature, test:

**Happy path**:
- Normal, expected inputs
- Typical use cases
- Common scenarios

**Edge cases**:
- Empty inputs
- Null/None values
- Boundary values (min, max)
- Zero, negative numbers
- Empty strings, lists, dicts

**Error cases**:
- Invalid inputs
- Type errors
- Missing required parameters
- Exceptions that should be raised

**Integration**:
- Interaction with dependencies
- Side effects
- State changes
- External calls

#### Step 4: Write the Tests

Follow project conventions:

**Python (pytest)**:
```python
import pytest
from module import function_to_test


def test_function_happy_path():
    """Test normal operation."""
    result = function_to_test("valid input")
    assert result == "expected output"


def test_function_edge_case_empty():
    """Test with empty input."""
    result = function_to_test("")
    assert result == ""


def test_function_error_invalid_input():
    """Test error handling."""
    with pytest.raises(ValueError):
        function_to_test(None)


@pytest.mark.parametrize("input,expected", [
    ("a", "A"),
    ("hello", "HELLO"),
    ("", ""),
])
def test_function_multiple_cases(input, expected):
    """Test multiple cases."""
    assert function_to_test(input) == expected
```

**JavaScript (Jest)**:
```javascript
import { functionToTest } from './module';

describe('functionToTest', () => {
  test('should handle normal input', () => {
    const result = functionToTest('valid input');
    expect(result).toBe('expected output');
  });

  test('should handle empty input', () => {
    const result = functionToTest('');
    expect(result).toBe('');
  });

  test('should throw error for invalid input', () => {
    expect(() => functionToTest(null)).toThrow(ValueError);
  });

  test.each([
    ['a', 'A'],
    ['hello', 'HELLO'],
    ['', ''],
  ])('should convert %s to %s', (input, expected) => {
    expect(functionToTest(input)).toBe(expected);
  });
});
```

#### Step 5: Handle Dependencies

Mock external dependencies:

**Python**:
```python
from unittest.mock import Mock, patch


def test_function_with_api_call(mocker):
    """Test function that calls external API."""
    mock_api = mocker.patch('module.api_client')
    mock_api.get.return_value = {'data': 'test'}

    result = function_to_test()

    assert result == 'processed test'
    mock_api.get.assert_called_once()
```

**JavaScript**:
```javascript
jest.mock('./apiClient');

test('should call API and process result', async () => {
  const mockGet = jest.fn().mockResolvedValue({ data: 'test' });
  apiClient.get = mockGet;

  const result = await functionToTest();

  expect(result).toBe('processed test');
  expect(mockGet).toHaveBeenCalledTimes(1);
});
```

#### Step 6: Run and Verify

After writing tests:
```bash
# Run the new tests
pytest path/to/test_file.py -v

# Check coverage
pytest path/to/test_file.py --cov=module --cov-report=term-missing

# Run all tests to ensure no regressions
pytest -v
```

#### Step 7: Present Results

Show what was created:

```
✅ Tests written! Here's what I created:

**File**: tests/test_calculator.py

**Tests added**:
1. test_add_positive_numbers - Happy path
2. test_add_negative_numbers - Edge case
3. test_add_zero - Edge case
4. test_add_floats - Type variation
5. test_add_invalid_type - Error handling

**Coverage**:
- Before: 60%
- After: 95%
- Missing: Error logging (line 45)

**Test results**:
- ✅ All 5 tests pass
- ✅ No regressions in other tests
- ✅ Coverage target met

Would you like me to:
1. Add more tests for the missing line?
2. Commit these changes?
3. Move on to another module?
```

## Testing Best Practices

### 1. Test Naming
- Use descriptive names
- Follow convention: `test_<function>_<scenario>_<expected>`
- Examples:
  - `test_login_valid_credentials_returns_token`
  - `test_parse_empty_string_returns_empty_list`
  - `test_divide_by_zero_raises_error`

### 2. Test Structure (AAA Pattern)
```python
def test_something():
    # Arrange: Set up test data
    user = User(name="Test")

    # Act: Execute the code
    result = user.get_display_name()

    # Assert: Verify the result
    assert result == "Test"
```

### 3. Test Independence
- Each test should run independently
- Don't rely on test execution order
- Clean up after tests (fixtures, teardown)
- Don't share state between tests

### 4. Test Coverage Goals
- **Critical code**: 100% coverage
- **Business logic**: 90%+ coverage
- **Utilities**: 80%+ coverage
- **Overall project**: 80%+ coverage

### 5. What to Test
**Do test**:
- Business logic
- Edge cases
- Error handling
- Public APIs
- Integration points

**Don't test**:
- Third-party libraries
- Framework internals
- Trivial getters/setters
- Generated code

### 6. Mock External Dependencies
- Database calls
- API requests
- File system operations
- Time-dependent code
- Random number generation

## Examples

### Example 1: Suggest Tests

**Command**: `/test`

**Output**:
```
📊 Analyzing test coverage...

**Current Coverage**: 72%

**Top Priority**:
1. src/auth/jwt.py (0% coverage) ⚠️ CRITICAL
   - Test token generation
   - Test token validation
   - Test expiration handling
   - Test invalid tokens

2. src/api/payments.py (30% coverage)
   - Missing: Refund tests
   - Missing: Failed payment tests
   - Missing: Webhook handling tests

Which should I tackle first?
```

### Example 2: Write Unit Tests

**Command**: `/test write tests for the calculate_discount function in src/pricing.py`

**Output**:
```
Writing tests for calculate_discount()...

Created: tests/test_pricing.py

**Tests added**:
- test_calculate_discount_percentage
- test_calculate_discount_fixed_amount
- test_calculate_discount_zero
- test_calculate_discount_negative_raises_error
- test_calculate_discount_exceeds_price_raises_error

✅ All 5 tests pass
✅ Coverage: 100% for calculate_discount()

Ready to commit?
```

### Example 3: Integration Tests

**Command**: `/test write integration tests for the user registration flow`

**Output**:
```
Writing integration tests for user registration...

Created: tests/integration/test_user_registration.py

**Test scenarios**:
1. Complete registration flow (email → verify → login)
2. Duplicate email handling
3. Invalid email format
4. Password requirements
5. Email verification timeout

**Setup**:
- Uses test database
- Mocks email service
- Cleans up after each test

✅ All 5 integration tests pass
✅ Tests run in 2.3 seconds

Ready to commit?
```

## Error Handling

### Can't Find Code to Test
**Solution**:
- Ask for more specific location
- Search the codebase
- List similar functions
- Request clarification

### Unclear What to Test
**Solution**:
- Ask about expected behavior
- Request examples
- Suggest common test cases
- Discuss with user

### Tests Fail After Writing
**Solution**:
- Debug the test
- Check if code has bugs
- Verify test logic
- Adjust expectations

### Coverage Not Improving
**Solution**:
- Check if tests are running
- Verify coverage configuration
- Look for excluded files
- Check for dead code

## Reusability

This command works across:
- Any programming language
- Any test framework
- Any project structure
- Any agent or AI assistant

The key is to:
- Detect the test framework
- Follow project conventions
- Write idiomatic tests
- Verify coverage improves

---

**Remember**: Good tests are an investment in confidence and velocity! 🧪✨
