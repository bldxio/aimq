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
4. Install Poetry (package manager):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
5. Install dependencies:
   ```bash
   poetry install
   ```
6. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
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
   poetry run pytest
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

Releases are handled by repository maintainers only:
1. Create a release branch from `dev`
2. Update version numbers and CHANGELOG.md
3. Create a pull request from the release branch to `main`
4. After approval and merge, tag the release in GitHub

## Questions?

If you have questions, please open an issue in the GitHub repository.
