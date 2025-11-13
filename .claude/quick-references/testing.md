# Testing Quick Reference

## Run Tests

```bash
# All tests (parallel)
just test

# With coverage report
just test-cov

# Sequential (for debugging)
just test-seq

# Watch mode (re-run on changes)
just test-watch

# Specific file
uv run pytest tests/aimq/test_worker.py

# Specific test
uv run pytest tests/aimq/test_worker.py::test_worker_initialization

# Pattern matching
uv run pytest -k "test_agent"

# Verbose output
uv run pytest -v

# Show print statements
uv run pytest -s
```

## Coverage

```bash
# Generate coverage report
just test-cov

# View HTML report
open htmlcov/index.html

# Terminal report only
uv run pytest --cov=src/aimq --cov-report=term
```

## Common Test Patterns

### Basic Test
```python
def test_something():
    result = function_under_test()
    assert result == expected_value
```

### Test with Fixture
```python
def test_with_fixture(sample_data):
    result = process(sample_data)
    assert result is not None
```

### Test Exception
```python
import pytest

def test_raises_error():
    with pytest.raises(ValueError):
        function_that_raises()
```

### Mock External Service
```python
from unittest.mock import Mock, patch

@patch('aimq.clients.supabase.get_supabase_client')
def test_with_mock(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client

    # Test code here
```

### Async Test
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## Debugging Tests

```bash
# Drop into debugger on failure
uv run pytest --pdb

# Drop into debugger at start of test
uv run pytest --trace

# Show local variables on failure
uv run pytest -l

# Stop on first failure
uv run pytest -x

# Run last failed tests
uv run pytest --lf
```

## Test Organization

```
tests/
├── aimq/
│   ├── agents/
│   │   └── test_react.py
│   ├── workflows/
│   │   └── test_document.py
│   └── test_worker.py
├── tools/
│   └── test_ocr.py
└── conftest.py  # Shared fixtures
```

## Coverage Goals

- **Target**: 79%+ overall
- **Priority**: Core logic (worker, queue, agents, workflows)
- **Check**: `just test-cov`

## Related

- See `standards/testing.md` for detailed testing standards
- See `conftest.py` for available fixtures
- See `pyproject.toml` for pytest configuration
