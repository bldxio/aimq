# AIMQ Task Runner
# Use `just <recipe>` to run tasks
# Run `just --list` to see all available recipes

# Default recipe - show available tasks
default:
    @just --list

# ============================================================================
# Development Setup
# ============================================================================

# Install development dependencies
install:
    uv sync --group dev

# Install production dependencies only
install-prod:
    uv sync

# ============================================================================
# Python Development Tasks
# ============================================================================

# Run all tests
test:
    uv run pytest

# Run tests with coverage report
test-cov:
    uv run pytest --cov=src/aimq

# Run tests in watch mode
test-watch:
    uv run pytest-watcher

# Lint code with flake8
lint:
    uv run flake8 src/aimq tests

# Format code with black
format:
    uv run black src/aimq tests

# Check types with mypy
type-check:
    uv run mypy src/aimq tests

# Run all quality checks (CI)
ci: lint type-check test

# Run pre-commit hooks on all files
pre-commit:
    uv run pre-commit run --all-files

# ============================================================================
# Docker Development
# ============================================================================

# Start development environment
dev:
    docker-compose up

# Build and start development environment
dev-build:
    docker-compose up --build

# Stop development environment
dev-down:
    docker-compose down

# ============================================================================
# Docker Production
# ============================================================================

# Start production environment
prod:
    docker-compose -f docker-compose.prod.yml up

# Build and start production environment
prod-build:
    docker-compose -f docker-compose.prod.yml up --build

# Stop production environment
prod-down:
    docker-compose -f docker-compose.prod.yml down

# ============================================================================
# Logs
# ============================================================================

# Tail all container logs
logs:
    docker-compose logs -f

# Tail API container logs
logs-api:
    docker-compose logs -f api

# Tail worker container logs
logs-worker:
    docker-compose logs -f worker

# Tail Redis container logs
logs-redis:
    docker-compose logs -f redis

# ============================================================================
# Cleanup
# ============================================================================

# Clean up all Docker containers and volumes
clean:
    docker-compose down -v
    docker-compose -f docker-compose.prod.yml down -v

# Clean Python cache files
clean-py:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true

# Clean everything (Docker + Python cache)
clean-all: clean clean-py

# ============================================================================
# Documentation
# ============================================================================

# Serve documentation locally
docs-serve:
    uv run mkdocs serve

# Build documentation
docs-build:
    uv run mkdocs build

# Deploy documentation to GitHub Pages
docs-deploy:
    uv run mkdocs gh-deploy

# ============================================================================
# Utilities
# ============================================================================

# Show project information
info:
    @echo "Project: AIMQ"
    @echo "Python: $(uv run python --version)"
    @echo "UV: $(uv --version)"
    @echo "Just: $(just --version)"
    @uv run python -c "import aimq; print(f'AIMQ version: {aimq.__version__ if hasattr(aimq, \"__version__\") else \"0.1.0\"}')"

# Update dependencies
update:
    uv lock --upgrade
    uv sync --group dev

# Add a new dependency
add package:
    uv add {{package}}

# Add a new dev dependency
add-dev package:
    uv add --dev {{package}}

# Remove a dependency
remove package:
    uv remove {{package}}

# ============================================================================
# Release Management
# ============================================================================

# Get current version
version:
    @uv run python scripts/sync_version.py

# Bump to next beta version (e.g., 0.1.1b1 -> 0.1.1b2)
version-beta:
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    if [[ $current =~ ^([0-9]+\.[0-9]+\.[0-9]+)b([0-9]+)$ ]]; then
        base="${BASH_REMATCH[1]}"
        num="${BASH_REMATCH[2]}"
        new_num=$((num + 1))
        new_version="${base}b${new_num}"
    else
        # If not a beta, assume we want the first beta of next patch
        if [[ $current =~ ^([0-9]+\.[0-9]+\.)([0-9]+)(.*)$ ]]; then
            major_minor="${BASH_REMATCH[1]}"
            patch="${BASH_REMATCH[2]}"
            new_patch=$((patch + 1))
            new_version="${major_minor}${new_patch}b1"
        else
            echo "Error: Could not parse version $current"
            exit 1
        fi
    fi
    uv run python scripts/sync_version.py "$new_version"

# Bump to release candidate (e.g., 0.1.1b2 -> 0.1.1rc1)
version-rc:
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    if [[ $current =~ ^([0-9]+\.[0-9]+\.[0-9]+)(b[0-9]+)?$ ]]; then
        base="${BASH_REMATCH[1]}"
        new_version="${base}rc1"
    else
        echo "Error: Could not parse version $current"
        exit 1
    fi
    uv run python scripts/sync_version.py "$new_version"

# Bump to stable release (e.g., 0.1.1rc1 -> 0.1.1)
version-stable:
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    if [[ $current =~ ^([0-9]+\.[0-9]+\.[0-9]+)(b[0-9]+|rc[0-9]+)?$ ]]; then
        base="${BASH_REMATCH[1]}"
        new_version="$base"
    else
        echo "Error: Could not parse version $current"
        exit 1
    fi
    uv run python scripts/sync_version.py "$new_version"

# Bump patch version (e.g., 0.1.1 -> 0.1.2)
version-patch:
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    if [[ $current =~ ^([0-9]+\.[0-9]+\.)([0-9]+)$ ]]; then
        prefix="${BASH_REMATCH[1]}"
        patch="${BASH_REMATCH[2]}"
        new_patch=$((patch + 1))
        new_version="${prefix}${new_patch}"
    else
        echo "Error: Could not parse version $current (must be stable X.Y.Z)"
        exit 1
    fi
    uv run python scripts/sync_version.py "$new_version"

# Bump minor version (e.g., 0.1.1 -> 0.2.0)
version-minor:
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    if [[ $current =~ ^([0-9]+\.)([0-9]+)\.[0-9]+$ ]]; then
        major="${BASH_REMATCH[1]}"
        minor="${BASH_REMATCH[2]}"
        new_minor=$((minor + 1))
        new_version="${major}${new_minor}.0"
    else
        echo "Error: Could not parse version $current (must be stable X.Y.Z)"
        exit 1
    fi
    uv run python scripts/sync_version.py "$new_version"

# Bump major version (e.g., 0.1.1 -> 1.0.0)
version-major:
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    if [[ $current =~ ^([0-9]+)\.[0-9]+\.[0-9]+$ ]]; then
        major="${BASH_REMATCH[1]}"
        new_major=$((major + 1))
        new_version="${new_major}.0.0"
    else
        echo "Error: Could not parse version $current (must be stable X.Y.Z)"
        exit 1
    fi
    uv run python scripts/sync_version.py "$new_version"

# Build distribution packages
build:
    @echo "Building distribution packages..."
    uv build
    @echo "✓ Build complete. Packages in dist/"

# Publish to TestPyPI (for testing)
publish-test: build
    @echo "Publishing to TestPyPI..."
    uv publish --publish-url https://test.pypi.org/legacy/
    @echo "✓ Published to TestPyPI"
    @echo "Test installation: uv pip install --index-url https://test.pypi.org/simple/ aimq"

# Publish to PyPI (production)
publish: build
    @echo "Publishing to PyPI..."
    uv publish
    @echo "✓ Published to PyPI"

# Complete beta release workflow
release-beta: ci
    @echo "=== Beta Release Workflow ==="
    @echo ""
    @echo "Current version: $(uv run python -c \"import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])\")"
    @echo ""
    @echo "This will:"
    @echo "  1. Bump to next beta version"
    @echo "  2. Prompt you to update CHANGELOG.md"
    @echo "  3. Build the package"
    @echo ""
    @read -p "Continue? (y/N) " -n 1 -r; echo; [[ $$REPLY =~ ^[Yy]$$ ]]
    just version-beta
    @echo ""
    @echo "⚠️  Please update CHANGELOG.md now with your changes"
    @echo "Press Enter when done..."
    @read
    just build
    @echo ""
    @echo "✅ Beta release prepared!"
    @echo ""
    @echo "Next steps:"
    @echo "  1. Review changes: git diff"
    @echo "  2. Commit: git add -A && git commit -m 'chore: release v$(uv run python -c \"import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])\")'"
    @echo "  3. Push: git push origin dev"
    @echo "  4. GitHub Actions will automatically publish to TestPyPI"

# Complete stable release workflow
release: ci
    @echo "=== Stable Release Workflow ==="
    @echo ""
    @echo "Current version: $(uv run python -c \"import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])\")"
    @echo ""
    @echo "This will:"
    @echo "  1. Bump to stable version"
    @echo "  2. Prompt you to update CHANGELOG.md"
    @echo "  3. Build the package"
    @echo ""
    @read -p "Continue? (y/N) " -n 1 -r; echo; [[ $$REPLY =~ ^[Yy]$$ ]]
    just version-stable
    @echo ""
    @echo "⚠️  Please update CHANGELOG.md now with your changes"
    @echo "Press Enter when done..."
    @read
    just build
    @echo ""
    @echo "✅ Stable release prepared!"
    @echo ""
    @echo "Next steps:"
    @echo "  1. Review changes: git diff"
    @echo "  2. Commit: git add -A && git commit -m 'chore: release v$(uv run python -c \"import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])\")'"
    @echo "  3. Create release branch: git checkout -b release/v$(uv run python -c \"import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])\")"
    @echo "  4. Push: git push origin release/v$(uv run python -c \"import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])\")"
    @echo "  5. Create PR to main branch"
    @echo "  6. After merge, GitHub Actions will publish to PyPI"
