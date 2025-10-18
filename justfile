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
