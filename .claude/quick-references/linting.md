# Linting Quick Reference

## Run Linters

```bash
# Lint with flake8
just lint

# Format with black
just format

# Type check with mypy
just type-check

# Run all checks (lint + type + test)
just ci

# Pre-commit hooks (all checks)
just pre-commit
```

## Individual Commands

```bash
# Flake8
uv run flake8 src/aimq tests

# Black (check only)
uv run black --check src/aimq tests

# Black (format)
uv run black src/aimq tests

# Mypy
uv run mypy src/aimq tests

# isort (import sorting)
uv run isort src/aimq tests
```

## Fix Common Issues

### Line Too Long
```python
# ❌ Bad
result = some_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)

# ✅ Good
result = some_function(
    arg1, arg2, arg3, arg4,
    arg5, arg6, arg7, arg8
)
```

### Import Order
```python
# ❌ Bad
from aimq.config import config
import os
from langchain.schema import Runnable

# ✅ Good (run: just format)
import os

from langchain.schema import Runnable

from aimq.config import config
```

### Type Hints Missing
```python
# ❌ Bad
def process(data):
    return data

# ✅ Good
def process(data: dict) -> dict:
    return data
```

### Unused Imports
```python
# ❌ Bad
import os  # Not used
from aimq.config import config

# ✅ Good
from aimq.config import config
```

## Flake8 Rules

From `.flake8`:
```ini
max-line-length = 100
extend-ignore = E203, W503, E501
max-complexity = 10
```

**Ignored**:
- `E203`: Whitespace before ':' (black compatibility)
- `W503`: Line break before binary operator (black compatibility)
- `E501`: Line too long (black handles this)

## Black Configuration

From `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py311', 'py312', 'py313']
```

## Pre-commit Hooks

Install hooks:
```bash
uv run pre-commit install
```

Run manually:
```bash
just pre-commit
# OR
uv run pre-commit run --all-files
```

## CI Checks

Before pushing:
```bash
just ci
```

This runs:
1. `just lint` - Flake8
2. `just type-check` - Mypy
3. `just test` - pytest

## Pre-existing Issues Don't Block Commits

### The Scenario

You run linting and see errors, but they're in files you didn't change:

```bash
$ just lint
src/aimq/commands/chat.py:173:1: C901 'chat' is too complex (15)
src/aimq/realtime/chat.py:79:5: C901 '_handle_broadcast' is too complex (13)
error: Recipe `lint` failed

$ git status
M tests/test_realtime_chat.py  # Only this file is staged
```

### Key Insight

**Pre-commit hooks only check staged files.** Linting errors in unchanged files are pre-existing and won't block your commit.

### How to Verify

```bash
# Check what files are staged
git diff --cached --name-only

# If linting errors are in files NOT in this list,
# they're pre-existing and won't block the commit
```

### When to Fix Pre-existing Issues

**Don't fix immediately if:**
- Issues are in unrelated files
- You're in the middle of a feature
- Fixing would expand scope significantly

**Do fix in a separate commit:**
```bash
# Create a dedicated refactoring task
git checkout -b refactor/reduce-complexity
# Fix the issues
git commit -m "refactor: reduce complexity in chat command"
```

### Running Lint on Staged Files Only

```bash
# Lint only staged files
git diff --cached --name-only | grep '\.py$' | xargs uv run flake8

# Or use pre-commit (automatically checks staged files)
uv run pre-commit run flake8
```

## Related

- [@../standards/code-style.md](../standards/code-style.md) - Detailed style guide
- [@precommit-troubleshooting.md](./precommit-troubleshooting.md) - Pre-commit hook issues
- [@../standards/precommit-workflow.md](../standards/precommit-workflow.md) - Pre-commit workflow
- [@common-tasks.md](./common-tasks.md) - Common development tasks
