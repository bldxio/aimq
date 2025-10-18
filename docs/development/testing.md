# Testing Guide

This guide covers the testing practices and requirements for AIMQ.

## Test Structure

Tests are organized to mirror the source code structure:

```
tests/
├── aimq/
│   ├── test_worker.py
│   ├── test_queue.py
│   ├── test_job.py
│   ├── clients/
│   │   └── test_supabase_client.py
│   └── tools/
│       ├── ocr/
│       │   └── test_image_ocr.py
│       └── pdf/
│           └── test_pdf_processor.py
└── conftest.py
```

## Running Tests

### Using just (Recommended)

```bash
# Run all tests
just test

# Run with coverage report
just test-cov

# Run all quality checks (lint + type + test)
just ci
```

### Using uv Directly

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/aimq

# Run specific test file
uv run pytest tests/aimq/test_worker.py

# Run tests matching a pattern
uv run pytest -k "test_process"

# Run with verbose output
uv run pytest -v
```

### Using pytest Directly

If you have AIMQ installed in your environment:

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/aimq
```

## Writing Tests

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

### Test Structure

Use pytest fixtures for test setup:

```python
import pytest
from aimq import Worker

@pytest.fixture
def worker():
    worker = Worker()
    worker.register_queue("test_queue")
    return worker

def test_process_job(worker):
    result = worker.process({"data": "test"})
    assert result["status"] == "success"
```

### Mocking

Use pytest's monkeypatch for mocking:

```python
def test_supabase_client(monkeypatch):
    mock_client = MockSupabaseClient()
    monkeypatch.setattr("aimq.clients.supabase.client", mock_client)
    # Test code here
```

## Code Quality

### Linting and Formatting

```bash
# Using just
just lint           # Check code style with flake8
just format         # Format code with black
just type-check     # Type checking with mypy

# Using uv directly
uv run flake8 src/aimq tests
uv run black src/aimq tests
uv run mypy src/aimq tests
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before committing:

```bash
# Install pre-commit hooks
just pre-commit

# Or manually
uv run pre-commit install

# Run hooks on all files
uv run pre-commit run --all-files
```

The pre-commit hooks will:
- Format code with black
- Check code style with flake8
- Run type checking with mypy
- Check for common issues

## CI/CD Pipeline

Our GitHub Actions pipeline runs tests on:

- Pull requests to main branch
- Push to main branch
- Release tags

The pipeline:

1. Sets up Python environment with uv
2. Installs dependencies with `uv sync --group dev`
3. Runs code quality checks (lint, format, type-check)
4. Runs all tests with coverage
5. Generates and uploads coverage reports
6. Builds documentation

### Running CI Checks Locally

Before pushing, run the same checks that CI will run:

```bash
# Run all CI checks locally
just ci

# Or manually
uv run flake8 src/aimq tests
uv run mypy src/aimq tests
uv run pytest --cov=src/aimq
```

## Test Coverage

AIMQ maintains high test coverage standards:

- **Minimum**: 80% overall coverage
- **Critical components**: 90%+ coverage
- **New code**: Must include tests

View coverage report:
```bash
just test-cov

# Or
uv run pytest --cov=src/aimq --cov-report=html
# Open htmlcov/index.html in browser
```

## Continuous Testing

For rapid feedback during development:

```bash
# Watch mode (if installed)
just test-watch

# Or use pytest-watch
uv run ptw
```
