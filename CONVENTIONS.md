# AIMQ Conventions

This document outlines the coding conventions and standards for the AIMQ project.

## Code Style

### Python

1. **Type Hints**
   - All function parameters and return values must have type hints
   - Use `Optional` for parameters that can be None
   - Use `Union` for parameters that can be multiple types
   - Use `TypeVar` for generic types
   - Example:
     ```python
     from typing import Optional, List, Dict

     def process_image(
         path: str,
         options: Optional[Dict[str, str]] = None
     ) -> List[Dict[str, str]]:
         ...
     ```

2. **Docstrings**
   - All public functions, classes, and modules must have docstrings
   - Use Google style docstrings
   - Include Args, Returns, and Raises sections
   - Example:
     ```python
     def process_image(path: str) -> dict:
         """Process an image file and extract text.

         Args:
             path: Path to the image file.

         Returns:
             dict: Extracted text and metadata.

         Raises:
             FileNotFoundError: If image file doesn't exist.
             ValueError: If image format is unsupported.
         """
         ...
     ```

3. **Naming Conventions**
   - Classes: PascalCase
   - Functions/Methods: snake_case
   - Variables: snake_case
   - Constants: SCREAMING_SNAKE_CASE
   - Private attributes/methods: _leading_underscore
   - Protected attributes/methods: __double_underscore

4. **Code Organization**
   - One class per file (with exceptions for small helper classes)
   - Related functionality grouped in modules
   - Clear separation of concerns
   - Maximum line length: 88 characters (Black default)

## Project Structure

```
aimq/
├── src/
│   └── aimq/
│       ├── commands/          # CLI command implementations
│       │   ├── send.py        # Job sending functionality
│       │   └── shared/        # Shared CLI components
│       │       └── paths.py   # Path management utilities
│       ├── providers/         # Queue provider implementations
│       │   ├── base.py        # Abstract provider interface
│       │   └── supabase.py    # Supabase provider implementation
│       ├── job.py             # Job model definition
│       ├── queue.py           # Queue management system
│       ├── worker.py          # Worker thread implementation
│       ├── logger.py          # Logging infrastructure
│       ├── helpers.py         # Runnable utilities
│       └── attachment.py      # File attachment handling
├── tests/
│   └── aimq/
│       └── test_queue.py      # Queue component tests
├── docs/                      # Documentation
├── examples/                  # Usage examples
└── site/                      # Generated documentation assets
```

Key components:
1. **Commands**: CLI interface for interacting with queues
2. **Providers**: Queue backend implementations (Supabase, etc.)
3. **Core Models**: Job, Queue, Worker classes for queue operations
4. **Utilities**: Logging, path management, and runnable helpers
5. **Attachments**: File handling and processing
6. **Tests**: Unit and integration tests for core functionality

Missing components (to be documented if present):
1. `config.py` - Configuration management
2. `clients/` - API client implementations
3. Additional test files for other components
4. Documentation generation assets

## Testing Standards

### Directory Structure
- All tests should be placed in the `tests` directory
- Test files should mirror the source directory structure
- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`

### Test Requirements
1. **Coverage Requirements**
   - Minimum 80% code coverage for new code
   - Critical components require 90%+ coverage
   - Integration tests required for public APIs

2. **Test Types**
   - Unit Tests: Test individual components in isolation
   - Integration Tests: Test component interactions
   - Functional Tests: Test complete features
   - Async Tests: Use pytest-asyncio for async code

3. **Test Structure**
   - Use pytest fixtures for test setup
   - Group related tests in classes
   - Use descriptive test names that explain the scenario
   - Follow Arrange-Act-Assert pattern

4. **Mocking Guidelines**
   - Mock external dependencies
   - Mock expensive operations
   - Use pytest's monkeypatch for environment/config
   - Document complex mocks

5. **Best Practices**
   - Tests should be independent and isolated
   - Avoid test interdependence
   - Clean up resources in fixtures
   - Keep tests focused and concise
   - Add docstrings for complex test cases

6. **Running Tests**
   ```bash
   # Run all tests
   poetry run pytest

   # Run with coverage
   poetry run pytest --cov=src

   # Run specific test file
   poetry run pytest tests/path/to/test_file.py

   # Run tests matching pattern
   poetry run pytest -k "pattern"
   ```

7. **Continuous Integration**
   - All tests must pass before merging
   - Coverage reports required for PRs
   - Performance tests for critical paths

## Git Conventions

1. **Branch Naming**
   - Feature branches: `feature/description`
   - Bug fixes: `fix/description`
   - Releases: `release/version`

2. **Commit Messages**
   - Start with type: feat, fix, docs, style, refactor, test, chore
   - Use present tense ("Add feature" not "Added feature")
   - First line is summary (50 chars or less)
   - Example:
     ```
     feat: add image preprocessing support

     - Add resize functionality
     - Add format conversion
     - Add basic image enhancement
     ```

3. **Pull Requests**
   - Link related issues
   - Include comprehensive description
   - Update tests and documentation
   - Keep changes focused and atomic

## Documentation

1. **Code Documentation**
   - Clear and concise docstrings
   - Comments for complex logic
   - Type hints for all functions
   - Examples in docstrings when helpful

2. **Project Documentation**
   - README.md for project overview
   - CONTRIBUTING.md for contribution guidelines
   - CHANGELOG.md for version history
   - API documentation in docs/

## Versioning

1. **Semantic Versioning**
   - MAJOR.MINOR.PATCH
   - Major: Breaking changes
   - Minor: New features, backward compatible
   - Patch: Bug fixes, backward compatible

2. **Version Control**
   - Tag all releases
   - Update CHANGELOG.md
   - Update version in pyproject.toml
