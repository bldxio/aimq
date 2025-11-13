# Dependency Management Quick Reference

## Overview

AIMQ uses **uv** for dependency management (NOT pip or poetry).

## Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

## Project Setup

```bash
# Install all dependencies (including dev)
just install
# OR
uv sync --group dev

# Install production dependencies only
just install-prod
# OR
uv sync

# Install from scratch (clean .venv)
rm -rf .venv
uv sync --group dev
```

## Adding Dependencies

```bash
# Add production dependency
uv add langchain

# Add specific version
uv add "langchain>=0.3.0"

# Add dev dependency
uv add --group dev pytest

# Add multiple dependencies
uv add langchain langgraph supabase
```

## Removing Dependencies

```bash
# Remove dependency
uv remove langchain

# Remove dev dependency
uv remove --group dev pytest
```

## Updating Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Sync after update
uv sync --group dev

# Update specific package
uv add "langchain>=0.3.1"
```

## Running Commands

```bash
# Run Python script
uv run python script.py

# Run pytest
uv run pytest

# Run any command in venv
uv run <command>

# Activate venv manually (if needed)
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
```

## Listing Dependencies

```bash
# List installed packages
uv pip list

# Show dependency tree
uv pip tree

# Show outdated packages
uv pip list --outdated

# Show package details
uv pip show langchain
```

## Lock File

```bash
# Generate lock file
uv lock

# Update lock file
uv lock --upgrade

# Install from lock file (reproducible)
uv sync --frozen
```

## Virtual Environment

```bash
# Create venv (done automatically by uv sync)
uv venv

# Remove venv
rm -rf .venv

# Recreate venv
uv venv
uv sync --group dev
```

## Configuration

Dependencies are defined in `pyproject.toml`:

```toml
[project]
dependencies = [
    "langchain>=0.3.0",
    "langgraph>=0.2.0",
    "supabase>=2.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "flake8>=7.0.0",
]
```

## Common Tasks

### Install New Package
```bash
# 1. Add dependency
uv add package-name

# 2. Verify it's in pyproject.toml
cat pyproject.toml | grep package-name

# 3. Commit changes
git add pyproject.toml uv.lock
git commit -m "build: add package-name dependency"
```

### Update Package
```bash
# 1. Update to latest
uv add "package-name>=X.Y.Z"

# 2. Test that everything works
just ci

# 3. Commit changes
git add pyproject.toml uv.lock
git commit -m "build: update package-name to vX.Y.Z"
```

### Remove Package
```bash
# 1. Remove dependency
uv remove package-name

# 2. Verify it's gone
uv pip list | grep package-name

# 3. Commit changes
git add pyproject.toml uv.lock
git commit -m "build: remove package-name dependency"
```

### Sync Dependencies Across Team
```bash
# After pulling changes with updated dependencies
uv sync --group dev

# If issues, try clean install
rm -rf .venv
uv sync --group dev
```

## Troubleshooting

### Package Not Found
```bash
# Update package index
uv pip install --upgrade pip

# Try with specific version
uv add "package-name==X.Y.Z"
```

### Dependency Conflicts
```bash
# Check dependency tree
uv pip tree

# Try updating all dependencies
uv lock --upgrade
uv sync --group dev

# If still issues, check pyproject.toml for version conflicts
```

### Slow Installation
```bash
# uv is already fast, but you can:
# 1. Use frozen lock file
uv sync --frozen

# 2. Skip dev dependencies if not needed
uv sync
```

### Wrong Python Version
```bash
# Check Python version
python --version

# Should be 3.11-3.13
# If not, install correct version and recreate venv
rm -rf .venv
uv venv --python 3.12
uv sync --group dev
```

## Best Practices

1. **Always use uv**: Never use pip or poetry in this project
2. **Commit lock file**: Always commit `uv.lock` for reproducibility
3. **Pin versions**: Use version constraints in pyproject.toml
4. **Test after updates**: Run `just ci` after updating dependencies
5. **Keep dependencies minimal**: Only add what you need
6. **Use dev groups**: Keep dev dependencies separate

## Migration from pip/poetry

If you're used to pip or poetry:

| pip/poetry | uv |
|------------|-----|
| `pip install package` | `uv add package` |
| `pip install -r requirements.txt` | `uv sync` |
| `pip uninstall package` | `uv remove package` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |
| `poetry add package` | `uv add package` |
| `poetry install` | `uv sync` |
| `poetry update` | `uv lock --upgrade` |

## Related

- See `CONSTITUTION.md` for dependency management non-negotiables
- See `pyproject.toml` for current dependencies
- See `uv.lock` for locked versions
- See [uv docs](https://github.com/astral-sh/uv) for more details
