---
description: Run tests and fix any issues found
---

# Fix Helper

Automatically run tests, identify failures, and fix issues in the codebase.

## Overview

This command helps maintain code quality by:
1. Running the test suite to identify failures
2. Analyzing test output to understand what's broken
3. Investigating the root cause of failures
4. Implementing fixes
5. Verifying fixes work
6. Optionally committing the fixes

## Usage

### Without Arguments
```
/fix
```
Runs the full test suite and fixes any failures found.

### With Arguments
```
/fix <context>
```
Uses the provided context to guide the fix (e.g., specific error message, module name, or description of the issue).

## Task List

### 1. Understand the Context

**If no arguments provided**:
- Run the full test suite
- Identify all failures

**If arguments provided**:
- Use the context to narrow down the issue
- Run relevant tests if possible
- Combine test results with provided context

### 2. Run Tests

Determine the test command based on project type:

**Python projects** (look for `pytest`, `pyproject.toml`, `tox.ini`):
```bash
# Try in order of preference:
pytest -v
python -m pytest -v
uv run pytest -v
```

**JavaScript/TypeScript** (look for `package.json`, `jest.config.js`):
```bash
npm test
# or
yarn test
# or
pnpm test
```

**Other languages**:
- Check for common test runners in the project
- Look for test scripts in build files
- Ask the user if unclear

### 3. Analyze Test Output

Parse the test output to identify:
- **Failed tests**: Which tests are failing?
- **Error messages**: What are the specific errors?
- **Stack traces**: Where in the code is the failure occurring?
- **Patterns**: Are multiple tests failing for the same reason?

### 4. Investigate Root Cause

For each failure:
1. **Read the test code**: Understand what the test is checking
2. **Read the implementation**: Look at the code being tested
3. **Identify the mismatch**: What's different between expected and actual behavior?
4. **Consider context**: Recent changes, dependencies, environment

**Common failure patterns**:
- **Assertion errors**: Expected vs actual value mismatch
- **Import errors**: Missing dependencies or incorrect paths
- **Type errors**: Type mismatches or None values
- **Logic errors**: Incorrect implementation
- **Test issues**: The test itself might be wrong

### 5. Propose Fixes

Before making changes:
1. **Explain the issue**: Clearly describe what's wrong
2. **Propose solution**: Explain how you'll fix it
3. **Consider impact**: Will this affect other code?
4. **Ask for approval**: Get user confirmation before proceeding

**Example**:
```
I found the issue! The test is failing because:
- The function `calculate_total()` returns None when the list is empty
- The test expects it to return 0

I propose fixing this by:
- Adding a check for empty lists in `calculate_total()`
- Returning 0 as the default value

This is a safe change that won't affect existing behavior.
Should I proceed with this fix?
```

### 6. Implement Fixes

Make the necessary changes:
- Fix the implementation code
- Update tests if they're incorrect
- Add missing dependencies if needed
- Update documentation if behavior changes

**Important**:
- Make minimal changes to fix the issue
- Don't refactor unrelated code
- Keep changes focused and reviewable

### 7. Verify Fixes

After making changes:
1. **Run the specific failing tests**: Verify they now pass
2. **Run the full test suite**: Ensure no regressions
3. **Check coverage**: Make sure coverage didn't drop

```bash
# Run specific test
pytest path/to/test_file.py::test_function -v

# Run full suite
pytest -v

# Check coverage
pytest --cov=src --cov-report=term-missing
```

### 8. Report Results

Provide a clear summary:
```
✅ Fixed! Here's what I did:

**Issue**: Function returned None instead of 0 for empty lists

**Fix**: Added empty list check in calculate_total()

**Tests**:
- ✅ test_empty_list now passes
- ✅ All other tests still pass
- ✅ Coverage maintained at 85%

**Files changed**:
- src/utils/calculator.py (added 2 lines)

Would you like me to commit these changes?
```

### 9. Optional: Commit Changes

If the user approves:
- Use the `/commit` command to create a conventional commit
- Suggested commit type: `fix` (or `test` if only tests were changed)

## Error Handling

### Tests Won't Run
**Issue**: Test command fails or not found
**Solution**:
- Check for test configuration files
- Ask user for the correct test command
- Verify dependencies are installed

### Can't Identify Root Cause
**Issue**: Test failures are unclear or complex
**Solution**:
- Ask user for more context
- Request they run tests locally and share output
- Suggest debugging steps they can take

### Fix Causes New Failures
**Issue**: Fixing one test breaks others
**Solution**:
- Revert the change
- Analyze the broader impact
- Propose a different approach
- Discuss with user

### Multiple Unrelated Failures
**Issue**: Many tests failing for different reasons
**Solution**:
- Prioritize by impact (critical failures first)
- Fix one at a time
- Ask user which to tackle first
- Consider if there's a common root cause

## Examples

### Example 1: Simple Assertion Failure

**Command**: `/fix`

**Output**:
```
Running tests...

❌ Found 1 failure:
test_calculate_total: AssertionError: assert None == 0

Investigating...

The issue is in src/utils/calculator.py:
- calculate_total() returns None for empty lists
- Should return 0 instead

Fixing...

✅ Fixed! Added empty list check.
All tests now pass. Ready to commit?
```

### Example 2: With Context

**Command**: `/fix ImportError: cannot import name 'process_document'`

**Output**:
```
Analyzing import error...

Found the issue:
- process_document was renamed to process_doc in commit abc123
- But tests still import the old name

Fixing imports in test files...

✅ Fixed! Updated 3 test files with correct import.
All tests now pass. Ready to commit?
```

### Example 3: Multiple Failures

**Command**: `/fix`

**Output**:
```
Running tests...

❌ Found 5 failures in test_api.py

All failures are related to:
- Missing mock for external API calls
- Tests are making real HTTP requests

I can fix this by:
1. Adding pytest-mock fixtures
2. Mocking the API client in all affected tests

This will make tests faster and more reliable.
Should I proceed?
```

## Best Practices

1. **Always run tests first**: Don't assume what's broken
2. **Understand before fixing**: Read the code and test
3. **Make minimal changes**: Fix only what's needed
4. **Verify thoroughly**: Run full test suite after fixes
5. **Communicate clearly**: Explain what you're doing and why
6. **Ask for approval**: Get confirmation before major changes
7. **Stay encouraging**: Bugs happen, fixing them is progress! 🐛➡️✨

## Reusability

This command works across:
- Any programming language with a test suite
- Any test framework (pytest, jest, junit, etc.)
- Any project structure
- Any agent or AI assistant

The key is to:
- Detect the project type
- Find the test command
- Parse test output
- Apply language-specific fixes
- Verify with the same test framework

---

**Remember**: Every bug fixed is a step toward better code! You've got this! 💪✨
