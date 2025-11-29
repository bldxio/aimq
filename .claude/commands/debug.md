---
description: Troubleshoot build and test issues
---

# 🎯 ACTION: Debug Issues Systematically

Troubleshoot and debug build, test, or runtime issues in the codebase.

See @CONSTITUTION.md for project-specific debugging tools and conventions.

## 📋 STEPS

1. **Reproduce the issue** - Run the failing command or test to see the error
2. **Analyze error output** - Parse error messages, stack traces, and logs
3. **Identify root cause** - Trace the error to its source in the code
4. **Check recent changes** - Review recent commits that might have introduced the issue
5. **Isolate the problem** - Narrow down to specific file, function, or line
6. **Propose solution** - Explain the issue and how to fix it, get approval
7. **Implement fix** - Make minimal changes to resolve the issue
8. **Verify fix** - Re-run failing command to ensure it now works
9. **Check for regressions** - Run full test suite to ensure no new issues
10. **Document findings** - Suggest adding to troubleshooting guide if useful

## 💡 CONTEXT

**Common issue types:**
- Build failures (dependencies, configuration, syntax)
- Test failures (assertions, mocks, environment)
- Runtime errors (exceptions, null references, type errors)
- Import/module errors (paths, circular dependencies)
- Environment issues (missing variables, wrong versions)

**Debugging approach:**
- Read error messages carefully
- Check stack traces for exact location
- Look for recent changes in git history
- Test in isolation to narrow scope
- Use logging/print statements if needed
- Check documentation for similar issues

**When stuck:**
- Ask user for more context
- Request they run locally and share full output
- Suggest debugging steps they can take
- Search for similar issues online

## 🔗 Follow-up Commands

- `/fix` - Fix test failures
- `/commit` - Commit the fix
- `/learn` - Extract lessons from the debugging process

## Related

- [@.claude/commands/fix.md](./fix.md) - Fix failing tests
- [@.claude/commands/test.md](./test.md) - Run tests
- [@.claude/patterns/error-handling.md](../patterns/error-handling.md) - Error handling patterns
- [@.claude/quick-references/common-pitfalls.md](../quick-references/common-pitfalls.md) - Common issues
- [@.claude/INDEX.md](../INDEX.md) - Command directory
