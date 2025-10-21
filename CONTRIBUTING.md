# Contributing to AIMQ

Thank you for your interest in contributing to AIMQ! This document provides guidelines and instructions for contributing to the project.

## Branch Strategy

AIMQ follows a strict branching strategy:
- `main`: Production-ready code, only updated through releases
- `dev`: Development branch where all feature work is integrated
- Feature branches: Created in your fork for specific features/fixes

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/aimq.git
   cd aimq
   ```
3. Add the original repository as upstream:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/aimq.git
   ```
4. Install uv (package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
5. Install dependencies:
   ```bash
   uv sync --group dev
   # or use just: just install
   ```
6. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Development Workflow

1. Sync your fork with upstream:
   ```bash
   git checkout dev
   git fetch upstream
   git merge upstream/dev
   git push origin dev
   ```

2. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes following our coding standards (see CONVENTIONS.md):
   - Use type hints for all function parameters and return values
   - Write docstrings for all public functions and classes
   - Follow PEP 8 style guidelines
   - Add tests for new functionality

4. Run tests locally:
   ```bash
   uv run pytest
   # or use just: just test
   ```

5. Commit your changes:
   - Write clear, concise commit messages
   - Reference any relevant issues

6. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a pull request to the `dev` branch of the main repository

## Code Style

We use several tools to maintain code quality:
- Black for code formatting
- isort for import sorting
- Flake8 for style guide enforcement
- MyPy for type checking

These are all configured in the pre-commit hooks.

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Include both positive and negative test cases
- Mock external services where appropriate
- Follow testing standards in CONVENTIONS.md

## Documentation

- Update documentation for any changed functionality
- Include docstrings for all public functions and classes
- Update the README.md if needed
- Add examples for new features

## Pull Request Process

1. Create a pull request from your feature branch to the `dev` branch
2. Update the README.md with details of changes if needed
3. Update the CHANGELOG.md with a note describing your changes
4. Ensure all checks pass (tests, linting, type checking)
5. Request review from maintainers
6. Address any review feedback
7. Once approved, maintainers will merge your PR into `dev`

## Release Process

### Version Strategy

- **dev branch**: Beta versions (e.g., `0.1.1b1`, `0.1.1b2`) published to TestPyPI
- **main branch**: Stable versions (e.g., `0.1.1`) published to PyPI
- Release candidates (e.g., `0.1.1rc1`) can be used before stable releases

### Beta Releases (Contributors)

Beta releases are created on the `dev` branch for testing new features:

1. Make sure all changes are committed and pushed
2. Run the beta release workflow:
   ```bash
   just release-beta
   ```
3. This will:
   - Run all CI checks (lint, type-check, test)
   - Bump to the next beta version (e.g., `0.1.1b1` → `0.1.1b2`)
   - Prompt you to update CHANGELOG.md
   - Build the package
4. Review the changes:
   ```bash
   git diff
   ```
5. Commit and push:
   ```bash
   git add -A
   git commit -m "chore: release v0.1.1b2"
   git push origin dev
   ```
6. GitHub Actions will automatically publish to TestPyPI
7. Test the installation:
   ```bash
   uv pip install --index-url https://test.pypi.org/simple/ aimq==0.1.1b2
   ```

### Stable Releases (Maintainers Only)

Stable releases are created on the `main` branch and published to PyPI:

1. Ensure the `dev` branch is ready for release (all tests passing, CHANGELOG up to date)
2. Run the stable release workflow:
   ```bash
   just release
   ```
3. This will:
   - Run all CI checks
   - Bump to stable version (e.g., `0.1.1b2` → `0.1.1`)
   - Prompt you to update CHANGELOG.md
   - Build the package
4. Review the changes and commit:
   ```bash
   git add -A
   git commit -m "chore: release v0.1.1"
   ```
5. Create a release branch:
   ```bash
   git checkout -b release/v0.1.1
   git push origin release/v0.1.1
   ```
6. Create a pull request from `release/v0.1.1` to `main`
7. After approval and merge, GitHub Actions will:
   - Publish to PyPI
   - Create a GitHub release with tag `v0.1.1`
8. Merge `main` back to `dev` to sync versions

### Version Bump Commands

For manual version management, use these commands:

```bash
# Check current version
just version

# Beta versions (for dev branch)
just version-beta          # 0.1.1b1 → 0.1.1b2

# Release candidates
just version-rc            # 0.1.1b2 → 0.1.1rc1

# Stable releases
just version-stable        # 0.1.1rc1 → 0.1.1

# Semantic versioning (for stable versions only)
just version-patch         # 0.1.1 → 0.1.2
just version-minor         # 0.1.1 → 0.2.0
just version-major         # 0.1.1 → 1.0.0
```

### Manual Publishing

For manual publishing (not recommended):

```bash
# Build the package
just build

# Publish to TestPyPI
just publish-test

# Publish to PyPI (requires PYPI_API_TOKEN)
just publish
```

## Questions?

If you have questions, please open an issue in the GitHub repository.
