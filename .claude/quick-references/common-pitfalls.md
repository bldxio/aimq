# Common Pitfalls

## Overview

Common mistakes and how to avoid them. Learn from others' mistakes so you don't have to make them yourself!

This is an index of all pitfall guides. For specific topics, see:

- **[Python Pitfalls](./python-pitfalls.md)** - Python-specific issues (deprecations, mutable defaults, None errors)
- **[Development Pitfalls](./development-pitfalls.md)** - Testing, Git, module organization, performance, documentation
- **[AIMQ Pitfalls](./aimq-pitfalls.md)** - AIMQ-specific issues (message serialization, pgmq, regex edge cases)

## Quick Reference

### Python
- Deprecation warnings → Fix immediately
- Mutable defaults → Use None
- None errors → Check before accessing

### Testing
- Test behavior, not implementation
- Mock external services
- Use flexible assertions

### Error Handling
- Workers never crash on job errors
- Always log exceptions
- Use dead letter queues

### Git
- Test before committing
- Write descriptive messages
- Use feature branches

### Module Organization
- Group by domain, not type
- Avoid circular imports

### Performance
- Use connection pools
- Async I/O in async code

### Documentation
- Keep docs updated
- Document why, not what

### AIMQ-Specific
- Serialize messages at boundaries
- Test regex with edge cases
- Check pgmq function signatures

## Related

- [@.claude/patterns/error-handling.md](../patterns/error-handling.md) - Error handling patterns
- [@.claude/patterns/testing-strategy.md](../patterns/testing-strategy.md) - Testing best practices
- [@.claude/patterns/module-organization.md](../patterns/module-organization.md) - Code organization
- [@.claude/standards/git-workflow.md](../standards/git-workflow.md) - Git best practices
- [@.claude/quick-references/llm-api-differences.md](./llm-api-differences.md) - Provider API compatibility
- [@.claude/quick-references/python-pitfalls.md](./python-pitfalls.md) - Python-specific pitfalls
- [@.claude/quick-references/development-pitfalls.md](./development-pitfalls.md) - Development pitfalls
- [@.claude/quick-references/aimq-pitfalls.md](./aimq-pitfalls.md) - AIMQ-specific pitfalls

---

**Remember**: Learn from mistakes, but don't be afraid to make them! 🎓✨
