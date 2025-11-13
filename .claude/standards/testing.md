# Testing Standards

## Overview

AIMQ maintains high test coverage (79%+) with fast, reliable tests that enable confident refactoring and rapid iteration.

## Test Structure

Tests mirror the source structure:

```
tests/
├── aimq/
│   ├── agents/
│   │   ├── test_react.py
│   │   └── test_plan_execute.py
│   ├── workflows/
│   │   ├── test_multi_agent.py
│   │   └── test_document.py
│   ├── common/
│   │   ├── test_llm.py
│   │   └── test_exceptions.py
│   ├── test_worker.py
│   ├── test_queue.py
│   └── test_job.py
├── tools/
│   ├── test_ocr.py
│   └── test_pdf.py
└── conftest.py
```

**Rule**: `tests/aimq/test_worker.py` tests `src/aimq/worker.py`

## Running Tests

```bash
# All tests (parallel)
just test

# With coverage report
just test-cov

# Specific file
uv run pytest tests/aimq/test_worker.py

# Specific test
uv run pytest tests/aimq/test_worker.py::test_worker_initialization

# Pattern matching
uv run pytest -k "test_agent"

# Sequential (for debugging)
just test-seq

# Watch mode (re-run on changes)
just test-watch
```

## Test Naming

```python
# ✅ Good: Descriptive, specific
def test_worker_processes_job_successfully():
    ...

def test_queue_archives_message_on_success():
    ...

def test_react_agent_handles_tool_error():
    ...

# ❌ Bad: Vague, unclear
def test_worker():
    ...

def test_success():
    ...

def test_1():
    ...
```

## Test Structure Pattern

Use **Arrange-Act-Assert** (AAA):

```python
def test_worker_processes_job_successfully():
    # Arrange: Set up test data and mocks
    worker = Worker()
    mock_provider = Mock(spec=QueueProvider)
    job_data = {"task": "process", "data": "test"}

    # Act: Execute the code under test
    result = worker.process_job(job_data)

    # Assert: Verify the outcome
    assert result["status"] == "success"
    mock_provider.archive.assert_called_once()
```

## Mocking External Dependencies

**Always mock external services** (Supabase, AI providers, file I/O):

```python
from unittest.mock import Mock, patch, MagicMock

# Mock Supabase client
@patch('aimq.clients.supabase.get_supabase_client')
def test_queue_reads_message(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.rpc.return_value.execute.return_value.data = [...]

    # Test code here

# Mock LLM calls
@patch('aimq.common.llm.ChatOpenAI')
def test_agent_generates_response(mock_llm):
    mock_llm.return_value.invoke.return_value = "response"

    # Test code here
```

## Fixtures

Use pytest fixtures for common setup (defined in `conftest.py`):

```python
# conftest.py
import pytest

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    client = Mock()
    client.rpc.return_value.execute.return_value.data = []
    return client

@pytest.fixture
def sample_job():
    """Sample job for testing"""
    return Job(
        id=1,
        data={"task": "test"},
        read_count=0,
        enqueued_at=datetime.now(),
        vt=datetime.now() + timedelta(seconds=30)
    )

# test_worker.py
def test_worker_processes_job(mock_supabase_client, sample_job):
    worker = Worker(provider=mock_supabase_client)
    result = worker.process(sample_job)
    assert result is not None
```

## Testing Async Code

Use `@pytest.mark.asyncio` for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_agent_execution():
    agent = AsyncReActAgent()
    result = await agent.execute({"input": "test"})
    assert result["status"] == "success"
```

## Testing Edge Cases

Always test:
- **Happy path**: Normal, expected behavior
- **Error cases**: What happens when things go wrong
- **Edge cases**: Empty inputs, None values, boundary conditions
- **Race conditions**: Threading/concurrency issues (if applicable)

```python
def test_worker_handles_missing_queue():
    """Test that worker raises error for non-existent queue"""
    worker = Worker()
    with pytest.raises(QueueNotFoundError):
        worker.process_queue("non-existent-queue")

def test_queue_handles_empty_message():
    """Test that queue handles empty message data"""
    queue = Queue("test-queue")
    result = queue.process(Job(id=1, data={}, ...))
    assert result["status"] == "skipped"

def test_agent_handles_tool_timeout():
    """Test that agent handles tool timeout gracefully"""
    agent = ReActAgent(timeout=1)
    with patch('aimq.tools.ocr.ImageOCR.run', side_effect=TimeoutError):
        result = agent.execute({"input": "test"})
        assert "error" in result
```

## Coverage Goals

- **Target**: 80%+ overall coverage (90%+ excellent)
- **Priority**: Core logic (worker, queue, agents, workflows) - aim for 90%+
- **Lower priority**: CLI commands, utilities, type stubs - aim for 80%+

Check coverage:
```bash
just test-cov
# Opens htmlcov/index.html in browser
```

### Pragmatic Testing Philosophy

**Perfect is the enemy of good**:
- Focus on core functionality first
- Skip tricky edge cases if they block progress
- Mark complex tests as `@pytest.mark.skip` or `@pytest.mark.integration`
- Get meaningful coverage quickly, refine later

**Example**:
```python
@pytest.mark.skip(reason="Complex timing issue, defer to integration tests")
def test_race_condition():
    pass

@pytest.mark.integration
def test_race_condition_integration():
    # Test in integration suite instead
    pass
```

## Test Performance

- **Fast tests**: Target < 30 seconds for full suite
- **Use mocks**: Don't hit real APIs or databases
- **Parallel execution**: Use `pytest-xdist` (`-n auto`)
- **Timeouts**: Set test timeouts to catch hangs (`--timeout=30`)

## What NOT to Test

- **External libraries**: Don't test LangChain, pytest, etc.
- **Type checking**: That's what mypy is for
- **Trivial code**: Simple getters/setters, property accessors
- **Generated code**: Auto-generated files, migrations

## Common Pitfalls

### ❌ Testing Implementation Details
```python
# BAD: Testing internal state
def test_worker_internal_state():
    worker = Worker()
    assert worker._internal_counter == 0  # Don't test private attributes
```

### ❌ Brittle Tests
```python
# BAD: Depends on exact string matching
def test_error_message():
    with pytest.raises(ValueError) as exc:
        raise_error()
    assert str(exc.value) == "Error: something went wrong at line 42"  # Too specific!
```

### ❌ Slow Tests
```python
# BAD: Hitting real APIs
def test_supabase_integration():
    client = get_supabase_client()  # Real API call!
    result = client.table('jobs').select('*').execute()
    assert len(result.data) > 0
```

## Best Practices

1. **Test behavior, not implementation**: Focus on what the code does, not how
2. **One assertion per test**: Or at least one logical concept
3. **Use descriptive names**: Test name should explain what's being tested
4. **Keep tests independent**: Each test should run in isolation
5. **Mock external dependencies**: No real API calls, file I/O, or network requests
6. **Use fixtures for setup**: Don't repeat setup code
7. **Test edge cases**: Empty inputs, None values, errors
8. **Keep tests fast**: Use mocks, avoid sleep(), run in parallel

## Related

- [Testing Strategy](../patterns/testing-strategy.md) - Systematic testing approach
- [Quick Reference: Testing](../quick-references/testing.md) - Quick commands
- [Error Handling](../patterns/error-handling.md) - Testing error handling
- See `pyproject.toml` for pytest configuration
