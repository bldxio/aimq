# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIMQ (AI Message Queue) is a message queue processor for Supabase's pgmq integration with built-in AI-powered document processing and OCR capabilities. It uses LangChain's Runnable interface for task processing and provides a worker/queue architecture.

**Technology Stack:**
- Python 3.11-3.13 (uses modern type hints)
- uv for dependency management (NOT pip/poetry)
- LangChain for AI workflows and Runnables
- Supabase pgmq for message queuing
- EasyOCR/PyTorch for OCR processing
- Typer for CLI commands
- pytest for testing
- just for task automation

## Development Commands

### Environment Setup
```bash
# Install dev dependencies (includes pytest, mkdocs, etc.)
just install
# OR: uv sync --group dev

# Install production dependencies only
just install-prod
# OR: uv sync
```

### Testing
```bash
# Run all tests
just test
# OR: uv run pytest

# Run with coverage report
just test-cov
# OR: uv run pytest --cov=src/aimq

# Run a single test file
uv run pytest tests/aimq/test_worker.py

# Run a single test function
uv run pytest tests/aimq/test_worker.py::test_worker_initialization

# Run tests matching a pattern
uv run pytest -k "test_worker"
```

### Code Quality
```bash
# Lint code
just lint
# OR: uv run flake8 src/aimq tests

# Format code
just format
# OR: uv run black src/aimq tests

# Type checking
just type-check
# OR: uv run mypy src/aimq tests

# Run all CI checks (lint + type + test)
just ci

# Pre-commit hooks
just pre-commit
# OR: uv run pre-commit run --all-files
```

### Dependency Management
```bash
# Add a production dependency
uv add <package>

# Add to dev dependency group
uv add --group dev <package>

# Remove a dependency
uv remove <package>

# Update all dependencies
uv lock --upgrade
uv sync --group dev
```

### Documentation
```bash
# Serve docs locally
just docs-serve
# OR: uv run mkdocs serve

# Build documentation
just docs-build
# OR: uv run mkdocs build
```

## Architecture

### Core Components

1. **Worker** (`src/aimq/worker.py`)
   - Main orchestrator class
   - Manages multiple queues and worker threads
   - Provides `@worker.task()` decorator for registering task handlers
   - Uses `Worker.load(path)` to load task definitions from Python files
   - Worker threads poll queues in priority order (OrderedDict)

2. **Queue** (`src/aimq/queue.py`)
   - Wraps LangChain Runnables with queue-specific configuration
   - Each queue has: name, timeout, tags, delete_on_finish flag
   - Two modes: `timeout > 0` uses read/archive, `timeout = 0` uses pop (immediate delete)
   - Handles job lifecycle: read → invoke → archive/delete

3. **Job** (`src/aimq/job.py`)
   - Represents a single message from pgmq
   - Contains: id, data (dict), read_count, enqueued_at, vt (visibility timeout)
   - Tracks if message was popped vs read for cleanup logic

4. **Providers** (`src/aimq/providers/`)
   - `QueueProvider`: Abstract interface for queue operations
   - `SupabaseQueueProvider`: Implements pgmq operations via Supabase RPC
   - Methods: send, send_batch, read, pop, archive, delete

5. **Clients** (`src/aimq/clients/`)
   - `supabase.py`: Supabase client singleton (storage + database)
   - `mistral.py`: Mistral AI client wrapper

6. **Tools** (`src/aimq/tools/`)
   - LangChain tools that can be used in task workflows
   - `ocr/`: ImageOCR for text extraction from images
   - `pdf/`: PageSplitter for PDF processing
   - `supabase/`: ReadRecord, WriteRecord, ReadFile, WriteFile, Enqueue
   - `mistral/`: AI provider tools

7. **Attachment** (`src/aimq/attachment.py`)
   - Wrapper for binary data with automatic mimetype detection
   - Used by OCR and file processing tools
   - Provides `.to_file()` to convert to PIL Image

8. **Config** (`src/aimq/config.py`)
   - Pydantic Settings-based configuration
   - Loads from .env file automatically
   - Singleton pattern via `config = get_config()`

### Task Definition Pattern

Tasks are defined in a `tasks.py` file (or custom path) and loaded by the worker:

```python
from aimq.worker import Worker

worker = Worker()

@worker.task(queue="my-queue", timeout=300, delete_on_finish=False)
def process_job(data: dict) -> dict:
    # Process the job
    return {"status": "success"}
```

The worker loads this file using `Worker.load(path)` which:
1. Dynamically imports the Python module
2. Extracts the `worker` instance
3. Returns it with all registered tasks

### Message Flow

1. Message sent to Supabase pgmq queue (via `aimq send` CLI or Supabase RPC)
2. Worker thread polls queues in order
3. Queue reads/pops message → creates Job
4. Queue invokes Runnable with job.data
5. On success: archive or delete based on `delete_on_finish`
6. On error: message stays in queue, vt expires, becomes visible again

### Git URL Loading (Docker Deployment)

AIMQ supports loading tasks from git repositories using npm-style URLs:
- `git:user/repo` - GitHub default branch
- `git:user/repo@branch` - Specific branch/tag
- `git:user/repo#path/to/tasks.py` - Subdirectory path
- `git:gitlab.com/user/repo@v1.0.0` - Full URL with host

This is implemented in `src/aimq/commands/shared/git_loader.py` and used by the Docker entry point.

## Testing Conventions

- Test files mirror source structure: `tests/aimq/test_worker.py` tests `src/aimq/worker.py`
- Use pytest fixtures for common setup (see test files for examples)
- Mock external dependencies (Supabase, AI providers) using `unittest.mock`
- Target coverage: 89%+ (current project coverage)
- Use `@pytest.mark.asyncio` for async tests
- Test edge cases: missing queues, errors, threading behavior

## Important Implementation Notes

### Using uv (not pip/poetry)
- This project migrated from Poetry to uv
- Always use `uv add`, `uv remove`, `uv sync` for dependencies
- Dependencies are in `pyproject.toml` [project.dependencies]
- Dev dependencies are in [dependency-groups] (PEP 735)
- Run commands with `uv run <command>`

### LangChain Integration
- Tasks are LangChain Runnables (RunnableLambda wraps functions)
- Use `RunnableConfig` for metadata (worker name, queue name, job ID)
- Support LangChain tracing via LANGCHAIN_TRACING_V2 env var

### Threading & Concurrency
- Worker uses threading.Event for clean shutdown
- WorkerThread processes queues in a loop
- Handles RuntimeError vs critical errors differently
- Test threading with short `idle_wait` to avoid slow tests

### Configuration Pattern
- Config is a singleton: `from aimq.config import config`
- Pydantic Settings loads from .env automatically
- Use Field(alias="ENV_VAR_NAME") for environment variables

### Supabase pgmq Operations
- Queue names must exist in pgmq before use
- `timeout=0` → pop (immediate delete), `timeout>0` → read + archive/delete
- Messages have visibility timeout (vt) - invisible until vt expires
- Use archive for retry-able failures, delete for permanent completion

### CLI Commands (Typer)
- Commands are in `src/aimq/commands/`
- Entry point: `aimq` → `src/aimq/commands/__init__.py:app`
- Use Rich for pretty console output
- Templates stored in `src/aimq/commands/shared/templates/`

### Docker Deployment
- Supports local tasks.py via volume mount
- Supports git URLs via AIMQ_TASKS environment variable
- Uses `uv sync --frozen` for reproducible builds
- See docker/README.md for deployment patterns

## Release Workflow

### IMPORTANT: CHANGELOG.md Automation

**CHANGELOG.md is automatically generated from git commits!**

#### Using Conventional Commits

AIMQ uses conventional commit format for automatic CHANGELOG generation:

- `feat:` → Added section
- `fix:` → Fixed section
- `docs:`, `refactor:`, `perf:` → Changed section
- `security:` → Security section
- `deprecate:` → Deprecated section
- `remove:` → Removed section
- `test:`, `chore:`, `ci:`, `build:` → Skipped

**Examples:**
```
feat: add batch processing for OCR jobs
fix: resolve race condition in worker startup
docs: update Docker deployment guide
refactor: simplify queue provider interface
```

#### Manual CHANGELOG Generation

During development, you can generate CHANGELOG entries:

```bash
# Preview what will be generated from commits
just changelog-preview

# Generate and update CHANGELOG.md [Unreleased] section
just changelog

# Generate from specific commit/tag
just changelog-since v0.1.0

# Finalize [Unreleased] → [VERSION] for stable releases (automatic in workflow)
just changelog-finalize 0.1.1
```

#### Beta vs Stable CHANGELOG Workflow

**Beta Releases (dev branch):**
- Changes accumulate in `[Unreleased]` section
- `just release-beta` updates `[Unreleased]` only
- No version sections created for beta releases
- Beta releases have no git tags, so no version sections in CHANGELOG

**Stable Releases (main branch):**
- `just release` workflow:
  1. Updates `[Unreleased]` from commits
  2. Prompts for review/edits
  3. Converts `[Unreleased]` → `[X.Y.Z] - DATE`
  4. Adds git tag comparison link
- Version sections align with git tags
- After merge to main, git tag is created

#### Release Workflows Automate This

The `just release-beta` and `just release` commands automatically:
1. Generate CHANGELOG from commits since last release
2. Prompt you to review the generated entries
3. Allow manual edits before finalizing
4. **For stable releases only:** Convert `[Unreleased]` to version section with tag link

#### When to Update Manually

You should manually edit CHANGELOG.md when:
- Generated entries need clarification
- You want to add user-facing context
- Combining multiple related commits into one entry
- Adding breaking change warnings

**See:** `docs/development/conventional-commits.md` for complete guide

### Version Strategy

- **dev branch**: Beta versions (0.1.1b1, 0.1.1b2, etc.) → TestPyPI (no git tags)
- **main branch**: Stable versions (0.1.1, 0.2.0, etc.) → PyPI + git tags
- **Release candidates**: Optional (0.1.1rc1) for pre-release testing

**Git Tag Policy:**
- Beta releases: No git tags created (tracked via TestPyPI only)
- Stable releases: Git tags automatically created by GitHub Actions after merge to main
- Tags point to merge commits on main branch

### Beta Release Process (dev branch)

**Note:** Beta releases are published to TestPyPI but do NOT create git tags. Tags are only created for stable releases on main branch.

**CHANGELOG Behavior:** Beta releases only update the `[Unreleased]` section. No version sections are created until stable release.

1. **Prepare the release:**
   ```bash
   just release-beta
   ```
   This will:
   - Run CI checks (lint, type-check, test)
   - Bump version (0.1.1b1 → 0.1.1b2)
   - **Update CHANGELOG [Unreleased]** from git commits
   - Prompt to review generated entries
   - Build the package

2. **Review CHANGELOG.md:**
   - Generated automatically from conventional commits into `[Unreleased]` section
   - Edit manually if needed (add context, clarify entries)
   - Ensure all changes are user-facing
   - **No version section created** - changes stay in `[Unreleased]`

3. **Commit and push:**
   ```bash
   git add -A
   git commit -m "chore: release v0.1.1b2"
   git push origin dev
   ```

4. **Automated publishing:**
   - GitHub Actions detects version change in pyproject.toml
   - Automatically publishes to TestPyPI
   - Creates summary with installation instructions
   - **No git tag is created** (beta releases are tracked via TestPyPI only)

5. **Test the release:**
   ```bash
   uv pip install --index-url https://test.pypi.org/simple/ aimq==0.1.1b2
   ```

### Stable Release Process (main branch - Maintainers Only)

**Note:** Git tags are created automatically by GitHub Actions AFTER merging to main. The tag points to the merge commit on main branch.

**CHANGELOG Behavior:** Stable releases convert `[Unreleased]` to a versioned section `[X.Y.Z]` with git tag comparison link.

1. **Ensure dev is ready:**
   - All tests passing
   - All beta changes accumulated in `[Unreleased]` section
   - Documentation current

2. **Prepare stable release:**
   ```bash
   just release
   ```
   This will:
   - Run CI checks
   - Bump to stable (0.1.1b2 → 0.1.1)
   - Update `[Unreleased]` from commits
   - Prompt to review `[Unreleased]` entries
   - **Convert `[Unreleased]` → `[0.1.1] - DATE`** with git tag link
   - Prompt to review finalized version section
   - Build the package

3. **Create release branch:**
   ```bash
   git add -A
   git commit -m "chore: release v0.1.1"
   git checkout -b release/v0.1.1
   git push origin release/v0.1.1
   ```

4. **Create PR to main:**
   - Create pull request from `release/v0.1.1` to `main`
   - Review and approve
   - Merge to main

5. **Automated publishing (triggered by merge to main):**
   - GitHub Actions detects version change in pyproject.toml
   - Publishes to PyPI
   - **Creates git tag `v0.1.1`** on the merge commit
   - Creates GitHub release with the tag
   - Generates release notes from CHANGELOG.md

6. **Sync back to dev:**
   ```bash
   git checkout main
   git pull
   git checkout dev
   git merge main
   git push origin dev
   ```

### Manual Version Bumps

When Claude Code is asked to bump versions:

```bash
# Check current version
just version

# Beta versions (dev branch)
just version-beta          # 0.1.1b1 → 0.1.1b2

# Release candidates
just version-rc            # 0.1.1b2 → 0.1.1rc1

# Stable release
just version-stable        # 0.1.1rc1 → 0.1.1

# Semantic versioning (stable versions only)
just version-patch         # 0.1.1 → 0.1.2
just version-minor         # 0.1.1 → 0.2.0
just version-major         # 0.1.1 → 1.0.0
```

### Pre-Release Checklist

Before any release, verify:
- [ ] All tests passing (`just ci`)
- [ ] Using conventional commits (feat:, fix:, etc.)
- [ ] CHANGELOG.md will be auto-generated or manually updated
- [ ] Version numbers synced (pyproject.toml and __init__.py)
- [ ] Documentation reflects changes
- [ ] No uncommitted changes
- [ ] Branch is up to date with remote

**Tip:** Use conventional commits (feat:, fix:, docs:) for automatic CHANGELOG generation!

### GitHub Actions Workflows

**CI Workflow (`.github/workflows/ci.yml`)**
- Runs on: PR to dev/main, push to dev/main
- Tests: Python 3.11, 3.12, 3.13
- Checks: lint, type-check, test coverage

**Publish Workflow (`.github/workflows/publish.yml`)**
- Triggers: Version change in pyproject.toml
- dev → TestPyPI
- main → PyPI + GitHub Release

**Docs Workflow (`.github/workflows/docs.yml`)**
- Triggers: Push to main
- Builds and deploys to GitHub Pages

### Required GitHub Secrets

Ensure these secrets are set in GitHub repository settings:

**Environment: dev**
- `TEST_PYPI_API_TOKEN` - TestPyPI API token

**Environment: prd**
- `PYPI_API_TOKEN` - PyPI API token

**Repository Secrets**
- `CODECOV_TOKEN` - Codecov upload token (optional, for coverage reports)
  - See `docs/development/codecov-setup.md` for setup instructions
  - Free for open source projects at https://codecov.io

### Troubleshooting Releases

**Version not publishing:**
- Check GitHub Actions logs
- Verify pyproject.toml version changed in commit
- Ensure secrets are set correctly

**Tests failing on CI:**
- Run `just ci` locally first
- Check for environment-specific issues
- Review test logs in GitHub Actions

**Version sync issues:**
- Run `uv run python scripts/sync_version.py <version>` manually
- Verify both pyproject.toml and __init__.py match

## Common Pitfalls

1. **Don't use pip/poetry** - This project uses uv exclusively
2. **Config is a singleton** - Import `config` not `Config` class
3. **Tasks need `worker` export** - Module must have `worker = Worker()` instance
4. **Queue names must be strings** - No spaces, use kebab-case
5. **Attachment mimetype is private** - Use `.mimetype` property, not `._mimetype`
6. **Threading tests need events** - Use threading.Event for synchronization
7. **Mock queue providers in tests** - Don't hit real Supabase in unit tests

## Project Structure

```
src/aimq/
├── worker.py           # Main Worker and WorkerThread classes
├── queue.py            # Queue wrapper for LangChain Runnables
├── job.py              # Job representation from pgmq
├── config.py           # Configuration singleton
├── logger.py           # Logging infrastructure
├── attachment.py       # Binary data wrapper with mimetype detection
├── utils.py            # Utility functions (module loading, etc.)
├── providers/          # Queue provider implementations
│   ├── base.py         # Abstract QueueProvider
│   └── supabase.py     # SupabaseQueueProvider (pgmq)
├── clients/            # External service clients
│   ├── supabase.py     # Supabase client singleton
│   └── mistral.py      # Mistral AI client
├── tools/              # LangChain tools for task workflows
│   ├── ocr/            # OCR processing tools
│   ├── pdf/            # PDF processing tools
│   ├── supabase/       # Supabase interaction tools
│   └── mistral/        # Mistral AI tools
└── commands/           # CLI command implementations
    ├── __init__.py     # Typer app entry point
    ├── start.py        # Start worker command
    ├── init.py         # Project initialization
    ├── send.py         # Send message to queue
    ├── enable.py       # Enable queue
    ├── disable.py      # Disable queue
    └── shared/         # Shared utilities and templates
        ├── git_loader.py    # Git URL loading
        └── templates/       # Project templates
```
