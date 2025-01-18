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

Run all tests:
```bash
poetry run pytest
```

Run with coverage:
```bash
poetry run pytest --cov=src
```

Run specific test file:
```bash
poetry run pytest tests/aimq/test_worker.py
```

Run tests matching a pattern:
```bash
poetry run pytest -k "test_process"
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

## CI/CD Pipeline

Our GitHub Actions pipeline runs tests on:

- Pull requests to main branch
- Push to main branch
- Release tags

The pipeline:

1. Runs all tests
2. Generates coverage report
3. Checks code style
4. Builds documentation
