---
description: Suggest or write tests for the codebase
---

# 🎯 ACTION: Analyze Coverage and Write Tests

Run coverage analysis, identify gaps, and write comprehensive tests to improve code quality.

See @CONSTITUTION.md for project-specific testing conventions and frameworks.

## 📋 STEPS

1. **Run coverage analysis** - Execute project's coverage command to get current metrics
2. **Identify gaps** - Find untested files, low coverage areas, missing edge cases
3. **Prioritize** - Rank by importance (critical untested → low coverage → improvements)
4. **Present suggestions** - Show coverage analysis with prioritized recommendations
5. **Locate code** - Search for the function/class/module to test
6. **Identify test cases** - Determine happy path, edge cases, error cases, integration scenarios
7. **Write tests** - Follow project conventions and AAA pattern (Arrange, Act, Assert)
8. **Mock dependencies** - Mock external services, databases, APIs, file system
9. **Run and verify** - Execute tests, check coverage improvement, ensure no regressions
10. **Report results** - Show tests created, coverage change, and suggest next steps

## 💡 CONTEXT

**Test case categories:**
- Happy path (normal, expected inputs)
- Edge cases (empty, null, boundaries, zero, negative)
- Error cases (invalid inputs, exceptions)
- Integration (dependencies, side effects, state changes)

**Test structure (AAA pattern):**
```
def test_something():
    # Arrange: Set up test data
    # Act: Execute the code
    # Assert: Verify the result
```

**Coverage goals:**
- Critical code: 100%
- Business logic: 90%+
- Utilities: 80%+
- Overall: 80%+

**What to test:**
- Business logic, edge cases, error handling, public APIs, integration points

**What NOT to test:**
- Third-party libraries, framework internals, trivial getters/setters, generated code

**Mock external dependencies:**
- Database calls, API requests, file system, time-dependent code, random generation

## 🔗 Follow-up Commands

- `/fix` - Fix any failing tests
- `/commit` - Commit the new tests
- `/learn` - Extract testing patterns

## Related

- [@.claude/standards/testing.md](../standards/testing.md) - Testing standards
- [@.claude/patterns/testing-strategy.md](../patterns/testing-strategy.md) - Testing patterns
- [@.claude/quick-references/testing.md](../quick-references/testing.md) - Testing commands
- [@.claude/commands/fix.md](./fix.md) - Fix failing tests
- [@.claude/commands/commit.md](./commit.md) - Commit changes
- [@.claude/INDEX.md](../INDEX.md) - Command directory
