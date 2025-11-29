---
description: Run tests and fix any issues found
---

# 🎯 ACTION: Fix Test Failures

Run the test suite, identify failures, implement fixes, and verify all tests pass.

See @CONSTITUTION.md for project-specific testing commands and conventions.

## 📋 STEPS

1. **Run the test suite** - Execute the project's test command
2. **Analyze failures** - Parse test output to identify what's broken and why
3. **Investigate root cause** - Read test code and implementation to understand the issue
4. **Propose fix** - Explain the issue and solution, get user approval before proceeding
5. **Implement fix** - Make minimal changes to fix the issue
6. **Verify fix** - Re-run tests to ensure they pass and no regressions
7. **Report results** - Summarize what was fixed and files changed
8. **Suggest next step** - Recommend `/commit` if all tests pass

## 💡 CONTEXT

**Common failure patterns:**
- Assertion errors (expected vs actual mismatch)
- Import errors (missing dependencies or incorrect paths)
- Type errors (None values, type mismatches)
- Logic errors (incorrect implementation)

**Fix principles:**
- Make minimal changes to fix the issue
- Don't refactor unrelated code
- Verify with full test suite, not just failing tests
- Ask for approval before major changes

**If multiple failures:**
- Look for common root cause first
- Fix one at a time if unrelated
- Ask user which to prioritize

**If fix causes new failures:**
- Revert the change
- Analyze broader impact
- Propose different approach

## 🔗 Follow-up Commands

- `/commit` - Commit the fixes
- `/learn` - Extract lessons from the failures
- `/test` - Run tests again to verify

## Related

- [@.claude/commands/test.md](./test.md) - Run test suite
- [@.claude/commands/debug.md](./debug.md) - Debug issues
- [@.claude/patterns/error-handling.md](../patterns/error-handling.md) - Error handling patterns
- [@.claude/quick-references/common-pitfalls.md](../quick-references/common-pitfalls.md) - Common mistakes
- [@.claude/commands/commit.md](./commit.md) - Commit fixes
- [@.claude/INDEX.md](../INDEX.md) - Command directory
