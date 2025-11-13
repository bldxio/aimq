# Patterns

Established patterns for consistency across the AIMQ codebase.

> 📖 **See [INDEX.md](../INDEX.md) for complete knowledge base navigation**

## Available Patterns

### Code Organization
- **[module-organization.md](module-organization.md)** - How to organize code into modules (agents, workflows, common, memory)
- **[composable-tools.md](composable-tools.md)** - Build small, focused tools that compose into workflows

### Error Handling
- **[error-handling.md](error-handling.md)** - General error handling patterns and best practices
- **[worker-error-handling.md](worker-error-handling.md)** - Worker-specific error handling (never crash on job errors)
- **[queue-error-handling.md](queue-error-handling.md)** - Queue error handling with DLQ and retry logic

### Testing
- **[testing-strategy.md](testing-strategy.md)** - Systematic testing approach for maximum coverage

### Development Process
- **[demo-driven-development.md](demo-driven-development.md)** - Use demo deadlines to focus and deliver quickly

## Guidelines

When documenting a new pattern:

1. **Identify the pattern**: What problem does it solve?
2. **Show examples**: Good and bad examples
3. **Explain benefits**: Why use this pattern?
4. **Keep it actionable**: Focus on "how-to"
5. **Keep it concise**: Under 400 lines
6. **Link to related docs**: Cross-reference other files

## When to Add a Pattern

Add a pattern when:
- You've solved the same problem multiple times
- A convention has emerged naturally
- You want to ensure consistency going forward
- New team members need guidance

## Related

- See `standards/` for best practices
- See `architecture/` for system design
- See `CONSTITUTION.md` for non-negotiable patterns
