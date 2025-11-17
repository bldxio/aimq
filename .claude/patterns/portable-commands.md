# Portable Commands Pattern

## What Happened

Commands contained project-specific tooling and hardcoded paths that made them non-portable to other projects.

**Examples of non-portable elements:**
- `just test` (project uses justfile)
- `uv run pytest` (project uses uv)
- Hardcoded file paths
- Project-specific conventions
- Tool-specific commands

**Problem:** Commands couldn't be reused in other projects without significant modification.

## What We Learned

Using @ syntax to reference project files (like @CONSTITUTION.md, @PLAN.md) keeps commands generic while allowing project-specific customization. The commands become templates that adapt to each project's context.

**Key insight:** Separate the "what to do" (generic) from the "how to do it" (project-specific). Commands define the workflow, project files define the implementation.

## Why It Matters

### Reusability Benefits
- Commands work across projects
- One place to improve commands (benefits all projects)
- Easier to onboard new projects
- Consistent workflow across teams

### Maintenance Benefits
- Project-specific details live in project files
- Update once, applies everywhere
- Clearer separation of concerns
- Less duplication

### Flexibility Benefits
- Projects can customize without forking commands
- Different tools, same workflow
- Adapt to project constraints
- Scale across organization

## How to Apply

### Use @ Syntax for File References

```markdown
See @CONSTITUTION.md for project conventions
See @.claude/GARDENING.md for knowledge garden structure
See @PLAN.md for current priorities
```

**Why it works:**
- Clear that it's a file reference
- Works with Claude's import system
- Self-documenting
- Easy to update

### Reference Concepts, Not Tools

❌ **Don't:**
```markdown
1. Run `just test`
2. Run `uv run pytest`
3. Check `.flake8` config
```

✅ **Do:**
```markdown
1. **Run tests** - Use project test runner
2. **Run linter** - Use project linter
3. **Check style** - Follow project conventions in @CONSTITUTION.md
```

### Let Project Files Provide Specifics

**Command file (generic):**
```markdown
## 📋 STEPS
1. **Run formatter** - Format code per project standards
2. **Run linter** - Check code quality
3. **Run tests** - Verify all tests pass
```

**Project file (specific):**
```markdown
# CONSTITUTION.md

## Development Workflow

**Formatting:** `just format` (uses black)
**Linting:** `just lint` (uses flake8)
**Testing:** `just test` (uses pytest)
```

### Create Project-Specific Adapters

For complex workflows, create adapter files:

```markdown
# .claude/quick-references/common-tasks.md

## Running Tests
```bash
just test              # Run all tests
just test-cov          # Run with coverage
uv run pytest -k NAME  # Run specific test
```

## Formatting Code
```bash
just format            # Format all code
just lint              # Check style
```
```

Commands reference the adapter, adapter contains specifics.

## Example

### ❌ Before (Non-Portable)

```markdown
# 🎯 ACTION: Run Tests

## 📋 STEPS
1. Install dependencies with `uv sync --group dev`
2. Run tests with `just test`
3. Check coverage with `just test-cov`
4. Verify 79%+ coverage per pyproject.toml
5. Fix any failures in tests/aimq/
```

**Problems:**
- Hardcoded to uv
- Hardcoded to just
- Hardcoded to pytest
- Hardcoded coverage target
- Hardcoded test directory

### ✅ After (Portable)

```markdown
# 🎯 ACTION: Run Tests

Run project test suite and verify coverage meets standards.

See @CONSTITUTION.md for testing standards and @.claude/quick-references/testing.md for commands.

## 📋 STEPS
1. **Install dependencies** - Ensure dev dependencies installed
2. **Run tests** - Execute full test suite
3. **Check coverage** - Verify meets project standards
4. **Fix failures** - Address any failing tests
5. **Review output** - Check for warnings or issues

## 💡 CONTEXT

**Testing principles:**
- All tests should pass before committing
- Coverage should meet project standards
- Tests should run quickly (< 30s for unit tests)
- Flaky tests should be fixed or skipped

## 🔗 Follow-up Commands
- `/fix` - Fix failing tests
- `/commit` - Commit passing changes
```

**Benefits:**
- Works with any test runner
- Works with any coverage tool
- Adapts to project standards
- Reusable across projects

## Real-World Application

### AIMQ Project Files

**CONSTITUTION.md** contains:
- Testing standards (79%+ coverage)
- Tool choices (pytest, black, flake8)
- Workflow commands (just commands)
- Code style rules

**Commands reference it:**
```markdown
See @CONSTITUTION.md for project conventions
```

### Portability to Other Projects

Same commands work for:
- **Project A:** Uses pytest + black + flake8 + just
- **Project B:** Uses unittest + autopep8 + pylint + make
- **Project C:** Uses pytest + ruff + poetry

Each project's CONSTITUTION.md defines the specifics.

## Pattern Variations

### Minimal Portability
Reference project files for conventions:
```markdown
See @CONSTITUTION.md for standards
```

### Medium Portability
Create quick-reference adapters:
```markdown
See @.claude/quick-references/common-tasks.md for commands
```

### Maximum Portability
Use generic language only:
```markdown
1. **Format code** - Apply project code style
2. **Check quality** - Run static analysis
3. **Run tests** - Execute test suite
```

Choose based on your needs. More portable = more generic = more flexible.

## Related

- [@.claude/patterns/documentation-as-interface.md](./documentation-as-interface.md) - Command structure
- [@.claude/patterns/command-composition.md](./command-composition.md) - How commands work together
- [@.claude/standards/command-structure.md](../standards/command-structure.md) - Standard format
- [@CONSTITUTION.md](../../CONSTITUTION.md) - Project-specific conventions

## Common Pitfalls

### ❌ Over-Abstraction
```markdown
1. Execute the code quality verification subprocess
2. Initiate the automated test execution framework
```
**Problem:** Too generic, unclear what to actually do.

### ❌ Under-Abstraction
```markdown
1. Run `uv run pytest tests/ --cov=src --cov-report=term-missing`
2. Check that coverage is >= 79% in pyproject.toml [tool.coverage.report]
```
**Problem:** Too specific, won't work in other projects.

### ✅ Just Right
```markdown
1. **Run tests** - Execute test suite with coverage
2. **Verify coverage** - Check meets project standards in @CONSTITUTION.md
```
**Solution:** Clear action, reference for specifics.

## Key Takeaway

**Commands should be portable templates, not hardcoded scripts.** Reference project files for specifics, keep commands generic. This makes them reusable, maintainable, and flexible across projects and teams.
