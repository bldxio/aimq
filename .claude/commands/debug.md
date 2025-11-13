---
description: Troubleshoot build and test issues
---

# Debug Helper

Systematically troubleshoot and debug issues in the codebase.

## Overview

This command helps debug problems by:
1. Running builds and tests to identify issues
2. Analyzing error messages and stack traces
3. Investigating root causes
4. Suggesting or implementing fixes
5. Verifying solutions work

## Usage

### Without Arguments
```
/debug
```
Runs builds and tests to discover any issues, then troubleshoots them.

### With Arguments
```
/debug <error or description>
```
Debugs the specific error or issue described.

## Task List

### 1. Identify the Issue

**If no arguments provided**:
1. Run the build process (if applicable)
2. Run the test suite
3. Check for linting/type errors
4. Look for runtime warnings
5. Identify all issues found

**If arguments provided**:
1. Parse the error message or description
2. Identify the type of error (syntax, runtime, logic, etc.)
3. Locate where the error occurs
4. Run relevant tests/builds to reproduce

### 2. Run Diagnostics

Based on project type, run appropriate checks:

**Python projects**:
```bash
# Type checking
mypy src/
# or
pyright

# Linting
flake8 src/
# or
ruff check src/

# Tests
pytest -v

# Build (if applicable)
python -m build
```

**JavaScript/TypeScript**:
```bash
# Type checking
tsc --noEmit

# Linting
eslint src/
# or
npm run lint

# Tests
npm test

# Build
npm run build
```

**Other languages**:
- Use language-specific diagnostic tools
- Check compiler output
- Run static analysis tools

### 3. Analyze Error Messages

For each error found:

**Parse the error**:
- Error type (SyntaxError, TypeError, ImportError, etc.)
- Error message
- File and line number
- Stack trace

**Categorize the issue**:
- **Syntax error**: Code doesn't parse
- **Type error**: Type mismatch
- **Import error**: Missing or incorrect imports
- **Runtime error**: Crashes during execution
- **Logic error**: Wrong behavior, no crash
- **Configuration error**: Build/test setup issue
- **Dependency error**: Missing or incompatible packages

### 4. Investigate Root Cause

Use a systematic approach:

**Step 1: Locate the code**
- Find the file and line number from the error
- Read the surrounding code for context
- Check recent changes (git log, git blame)

**Step 2: Understand the intent**
- What is this code supposed to do?
- What are the inputs and outputs?
- What are the assumptions?

**Step 3: Identify the mismatch**
- What's different between expected and actual?
- What changed recently?
- Are there related issues?

**Step 4: Form hypotheses**
- List possible causes
- Rank by likelihood
- Test each hypothesis

### 5. Gather More Information

If the root cause isn't clear:

**Add debug output**:
```python
# Python
print(f"Debug: variable = {variable}")
import pdb; pdb.set_trace()  # Breakpoint

# JavaScript
console.log('Debug:', variable);
debugger;  // Breakpoint
```

**Check logs**:
- Application logs
- Test output
- Build logs
- System logs

**Verify assumptions**:
- Check variable values
- Verify function inputs/outputs
- Confirm environment setup
- Test edge cases

**Search for similar issues**:
- Check project issues/PRs
- Search error message online
- Look in knowledge garden
- Check documentation

### 6. Propose Solutions

Before making changes:

**Explain the issue**:
```
I found the problem! Here's what's happening:

**Error**: TypeError: 'NoneType' object is not iterable

**Root cause**:
- The function get_items() returns None when the database is empty
- The code tries to iterate over the result without checking for None

**Why it's happening**:
- Recent change in commit abc123 changed the return value
- Tests didn't catch this because they mock the database
```

**Suggest solutions**:
```
I see 3 possible fixes:

1. **Add None check** (Quick fix)
   - Check if result is None before iterating
   - Pros: Simple, safe
   - Cons: Defensive coding, doesn't fix root cause

2. **Return empty list** (Better fix)
   - Change get_items() to return [] instead of None
   - Pros: More consistent, cleaner code
   - Cons: Changes function contract

3. **Use Optional type** (Best fix)
   - Make return type Optional[List[Item]]
   - Add None checks where needed
   - Update tests to cover None case
   - Pros: Type-safe, explicit
   - Cons: More changes needed

I recommend option 2. What do you think?
```

### 7. Implement Fix (If Approved)

Make the necessary changes:
- Fix the code
- Update tests
- Add error handling
- Update documentation

**Important**:
- Make focused changes
- Don't introduce new issues
- Follow project conventions
- Add tests for the fix

### 8. Verify the Fix

After implementing:

**Run diagnostics again**:
```bash
# Run the same checks as step 2
# Verify the error is gone
# Check for new errors
```

**Test thoroughly**:
- Run affected tests
- Run full test suite
- Test edge cases
- Check coverage

**Manual testing** (if applicable):
- Test the feature manually
- Try to reproduce the original issue
- Verify expected behavior

### 9. Report Results

Provide a clear summary:

```
🎉 Issue resolved! Here's what I did:

**Problem**: TypeError when database returns empty result

**Root cause**: get_items() returned None instead of empty list

**Solution**: Changed return value to [] for empty results

**Changes**:
- src/database/queries.py: Updated get_items() return value
- tests/test_queries.py: Added test for empty result case

**Verification**:
- ✅ Original error is gone
- ✅ All tests pass
- ✅ Manual testing confirms fix
- ✅ No new issues introduced

Would you like me to commit these changes?
```

### 10. Document Learnings

If this was a tricky bug:
- Suggest adding to knowledge garden
- Document the pattern
- Update troubleshooting guides
- Add to common pitfalls

## Debugging Strategies

### Strategy 1: Binary Search
For "it worked before" issues:
1. Find the last working commit
2. Find the first broken commit
3. Use `git bisect` to narrow down
4. Identify the breaking change

### Strategy 2: Rubber Duck
For complex logic issues:
1. Explain the code line by line
2. Describe what each part does
3. Identify where behavior diverges
4. Often the explanation reveals the bug

### Strategy 3: Minimal Reproduction
For intermittent issues:
1. Create the smallest code that reproduces the bug
2. Remove everything unrelated
3. Isolate the exact conditions
4. Fix becomes obvious

### Strategy 4: Divide and Conquer
For large codebases:
1. Identify the subsystem with the issue
2. Narrow down to the module
3. Find the specific function
4. Locate the exact line

## Error Handling

### Can't Reproduce the Issue
**Solution**:
- Ask for more details
- Request environment info
- Check if it's environment-specific
- Try different inputs/conditions

### Multiple Interrelated Issues
**Solution**:
- Fix one at a time
- Start with the root cause
- Verify each fix independently
- Watch for cascading effects

### Issue Persists After Fix
**Solution**:
- Verify the fix was applied correctly
- Check for caching issues
- Restart services/processes
- Look for multiple causes

### No Clear Root Cause
**Solution**:
- Add more logging/debugging
- Simplify the reproduction case
- Ask for user's insights
- Research similar issues

## Examples

### Example 1: Import Error

**Command**: `/debug ImportError: cannot import name 'User'`

**Output**:
```
Analyzing import error...

**Error**: ImportError: cannot import name 'User' from 'models'

**Investigation**:
- Checking models/__init__.py...
- User class exists in models/user.py
- But it's not exported in __init__.py

**Root cause**: Missing export in models/__init__.py

**Fix**: Add 'User' to __all__ in models/__init__.py

Implementing fix...

✅ Fixed! Import now works. All tests pass.
```

### Example 2: Logic Bug

**Command**: `/debug`

**Output**:
```
Running diagnostics...

✅ Build: OK
✅ Linting: OK
❌ Tests: 2 failures in test_calculations.py

Investigating test failures...

**Issue**: calculate_discount() returns wrong values

**Root cause**:
- Discount calculation uses integer division (//)
- Should use float division (/)
- Example: 100 // 3 = 33, but should be 33.33

**Fix**: Change // to / in line 45

Should I implement this fix?
```

### Example 3: Type Error

**Command**: `/debug TypeError: unsupported operand type(s) for +: 'int' and 'str'`

**Output**:
```
Analyzing type error...

**Error location**: src/utils/formatter.py, line 23

**Code**:
```python
total = count + suffix  # Line 23
```

**Problem**:
- count is an int
- suffix is a str
- Can't add them directly

**Root cause**: Missing type conversion

**Solutions**:
1. Convert to string: f"{count}{suffix}"
2. Convert to int: count + int(suffix)

Based on context, option 1 makes sense (formatting output).

Should I implement this fix?
```

## Best Practices

1. **Stay systematic**: Follow the debugging process
2. **Don't guess**: Gather evidence before proposing fixes
3. **Test hypotheses**: Verify your understanding
4. **Document findings**: Help future debugging
5. **Stay calm**: Bugs are puzzles, not problems
6. **Ask for help**: User might have insights
7. **Learn from it**: Every bug teaches something

## Reusability

This command works across:
- Any programming language
- Any type of error
- Any project structure
- Any agent or AI assistant

The key is to:
- Adapt diagnostic tools to the language
- Use systematic investigation
- Communicate clearly
- Verify thoroughly

---

**Remember**: Every bug is an opportunity to understand the code better! 🐛🔍✨
