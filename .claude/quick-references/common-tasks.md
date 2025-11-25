# Common Tasks Quick Reference

## Development Setup

```bash
# Install dependencies
just install

# Install production only
just install-prod

# Update dependencies
uv lock --upgrade
uv sync --group dev
```

## Running the Worker

```bash
# Start worker with tasks file
aimq worker start tasks.py

# Start with specific workers
aimq worker start tasks.py --workers 4

# Start with custom name
aimq worker start tasks.py --name my-worker
```

## Queue Operations

```bash
# Send message to queue
aimq queue send my-queue '{"task": "process", "data": "value"}'

# Read messages (without removing)
aimq queue read my-queue

# Pop message (remove from queue)
aimq queue pop my-queue
```

## Testing

```bash
# Run all tests
just test

# Run with coverage
just test-cov

# Run specific test
uv run pytest tests/aimq/test_worker.py::test_worker_initialization
```

## Code Quality

```bash
# Format code
just format

# Lint code
just lint

# Type check
just type-check

# Run all checks
just ci
```

## Documentation

```bash
# Serve docs locally
just docs-serve

# Build docs
just docs-build

# Open docs in browser
open http://127.0.0.1:8000
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Stage changes
git add "file.py"

# Commit with conventional format
git commit -m "feat(agents): add new agent type"

# Push to remote
git push origin feature/my-feature
```

## Release Workflow

```bash
# Check current version
just version

# Beta release (dev branch)
just release-beta

# Stable release (main branch)
just release

# Manual version bump
just version-patch  # 0.1.1 → 0.1.2
just version-minor  # 0.1.1 → 0.2.0
just version-major  # 0.1.1 → 1.0.0
```

## Docker

```bash
# Build image
docker build -t aimq .

# Run with local tasks
docker run -v ./tasks.py:/app/tasks.py aimq

# Run with git URL
docker run -e AIMQ_TASKS=git:user/repo aimq

# Run with environment file
docker run --env-file .env aimq
```

## Debugging

```bash
# Run tests with debugger
uv run pytest --pdb

# Show print statements in tests
uv run pytest -s

# Verbose test output
uv run pytest -v

# Run single test with debugging
uv run pytest tests/aimq/test_worker.py::test_name -v -s
```

## Project Initialization

```bash
# Initialize new AIMQ project
aimq init my-project

# Creates:
# - tasks.py (example tasks)
# - .env.example (configuration template)
# - README.md (project documentation)
```

## Dependency Management

```bash
# Add production dependency
uv add package-name

# Add dev dependency
uv add --group dev package-name

# Remove dependency
uv remove package-name

# Show installed packages
uv pip list

# Show dependency tree
uv pip tree
```

## Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit environment variables
vim .env

# Required variables:
# - SUPABASE_URL
# - SUPABASE_KEY
# - OPENAI_API_KEY (or other LLM provider)
```

## Troubleshooting

```bash
# Check Python version
python --version  # Should be 3.11-3.13

# Check uv installation
uv --version

# Reinstall dependencies
rm -rf .venv
uv sync --group dev

# Clear pytest cache
rm -rf .pytest_cache

# Clear coverage data
rm -rf .coverage htmlcov/
```

## Related

- [@testing.md](./testing.md) - Testing commands and reference
- [@linting.md](./linting.md) - Linting commands and reference
- [@git-commands.md](./git-commands.md) - Git commands reference
- [@dependency-management.md](./dependency-management.md) - Dependency management
- [@../../CLAUDE.md](../../CLAUDE.md) - Comprehensive documentation
