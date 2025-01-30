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

1. **Third-Party Packages Without Type Hints**

   - For third-party packages missing type hints (no py.typed marker or stubs):

     - Add a `# type: ignore` comment on the import line
     - Document the ignored package in a comment if additional context is needed
     - Example:

     ```python
     # Package lacks type hints as of v1.2.0
     import some_package  # type: ignore
     ```

1. **Docstrings**

   - All public functions, classes, and modules must have docstrings
   - Use Google style docstrings
   - Include Args, Returns, and Raises sections
   - Single-line docstrings should fit on one line with quotes
   - Multi-line docstrings require a blank line between summary and description
   - First line should be in imperative mood (e.g., "Process data" not "Processes data")
   - All sentences should end with a period

   Example:

   ```python
   """Convert input data to the required format.

   This function takes raw input data and processes it according
   to the specified requirements.

   Args:
       data: Raw input data to process.

   Returns:
       Processed data in the required format.
   """
   ```

1. **Imports**

   - Remove unused imports
   - Use TYPE_CHECKING for type-only imports
   - For third-party packages missing type hints (no py.typed marker or stubs):
     - Add a `# type: ignore` comment on the import line
     - Document the ignored package in a comment if additional context is needed

   Example:

   ```python
   from typing import TYPE_CHECKING

   # Runtime imports
   import json
   from pathlib import Path

   # Type-checking imports
   if TYPE_CHECKING:
       from mypackage.types import SpecialType

   # Package lacks type hints as of v1.2.0
   import some_package  # type: ignore
   ```

1. **Naming Conventions**

   - Classes: PascalCase
   - Functions/Methods: snake_case
   - Variables: snake_case
   - Constants: SCREAMING_SNAKE_CASE
   - Private attributes/methods: \_leading_underscore
   - Protected attributes/methods: \_\_double_underscore

1. **Code Organization**

   - One class per file (with exceptions for small helper classes)
   - Related functionality grouped in modules
   - Clear separation of concerns
   - Maximum line length: 88 characters (Black default)
   - Long lines should be split across multiple lines, especially for:
     - Function calls with many arguments
     - Long string literals
     - Complex expressions

   Example of handling long lines:

   ```python
   # Bad:
   result = some_function_call(first_argument="value1", second_argument="value2", third_argument="value3")

   # Good:
   result = some_function_call(
       first_argument="value1",
       second_argument="value2",
       third_argument="value3"
   )
   ```

## Project Structure

```text
aimq/
├── src/
│   └── aimq/
│       ├── commands/          # CLI command implementations
│       ├── providers/         # Queue provider implementations
│       ├── tools/             # Tool implementations and utilities
│       ├── config.py          # Configuration management
│       ├── job.py             # Job model definition
│       ├── queue.py           # Queue management system
│       ├── worker.py          # Worker thread implementation
│       ├── logger.py          # Logging infrastructure
│       ├── helpers.py         # Runnable utilities
│       ├── types.py           # Type definitions and aliases
│       ├── utils.py           # General utility functions
│       └── attachment.py      # File attachment handling
├── tests/                     # Test suite
├── docs/                      # Documentation
├── examples/                  # Usage examples
└── site/                      # Generated documentation assets
```

Key components:

1. **Commands**: CLI interface for interacting with queues
1. **Providers**: Queue backend implementations (Supabase, etc.)
1. **Core Models**: Job, Queue, Worker classes for queue operations
1. **Utilities**: Logging, path management, and runnable helpers
1. **Attachments**: File handling and processing
1. **Tests**: Unit and integration tests for core functionality

Missing components (to be documented if present):

1. Additional test files for other components
1. Documentation generation assets

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

1. **Test Types**

   - Unit Tests: Test individual components in isolation
   - Integration Tests: Test component interactions
   - Functional Tests: Test complete features
   - Async Tests: Use pytest-asyncio for async code

1. **Test Structure**

   - Use pytest fixtures for test setup
   - Group related tests in classes
   - Use descriptive test names that explain the scenario
   - Follow Arrange-Act-Assert pattern

1. **Mocking Guidelines**

   - Mock external dependencies
   - Mock expensive operations
   - Use pytest's monkeypatch for environment/config
   - Document complex mocks

1. **Best Practices**

   - Tests should be independent and isolated
   - Avoid test interdependence
   - Clean up resources in fixtures
   - Keep tests focused and concise
   - Add docstrings for complex test cases

1. **Running Tests**

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

1. **Continuous Integration**

   - All tests must pass before merging
   - Coverage reports required for PRs
   - Performance tests for critical paths

## Dependency Management

1. **Poetry**

   - Use Poetry for dependency management and packaging
   - All dependencies must be specified in `pyproject.toml`
   - Lock file (`poetry.lock`) must be committed
   - Version constraints:
     - Use `^` for compatible release (e.g., `^1.2.3`)
     - Use `~` for patch-level changes (e.g., `~1.2.3`)
     - Pin exact versions only when necessary

1. **Development Dependencies**

   - Development tools go in `[tool.poetry.group.dev.dependencies]`
   - Testing packages go in `[tool.poetry.group.test.dependencies]`
   - Documentation packages go in `[tool.poetry.group.docs.dependencies]`

1. **Virtual Environments**

   - Use Poetry's built-in virtual environment management
   - Do not commit `.venv` directory
   - Run `poetry install` to set up development environment

## Git Conventions

1. **Branch Naming**

   - Feature branches: `feature/description`
   - Bug fixes: `fix/description`
   - Releases: `release/version`

1. **Commit Messages**

   - Start with type: feat, fix, docs, style, refactor, test, chore

   - Use present tense ("Add feature" not "Added feature")

   - First line is summary (50 chars or less)

   - Example:

     ```markdown
     feat: add image preprocessing support

     - Add resize functionality
     - Add format conversion
     - Add basic image enhancement
     ```

1. **Pull Requests**

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

1. **Project Documentation**

   - README.md for project overview
   - CONTRIBUTING.md for contribution guidelines
   - CHANGELOG.md for version history
   - API documentation in docs/

## Markdown

1. **Document Structure**

   - Headings must be surrounded by blank lines
   - Lists must be surrounded by blank lines
   - Fenced code blocks must be surrounded by blank lines
   - All fenced code blocks must specify a language
   - Ordered lists may use any consistent prefix style (1. or all 1.)

1. **Code Examples**

   ```python
   # Example with proper spacing and language specification
   def example():
       pass
   ```

1. **Line Length**

   - Follow the same 88 character limit as Python code
   - Exception: URLs and code blocks may exceed this limit

## Versioning

1. **Semantic Versioning**

   - MAJOR.MINOR.PATCH
   - Major: Breaking changes
   - Minor: New features, backward compatible
   - Patch: Bug fixes, backward compatible

1. **Version Control**

   - Tag all releases
   - Update CHANGELOG.md
   - Update version in pyproject.toml
