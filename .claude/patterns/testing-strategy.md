# Testing Strategy

## Overview

A systematic approach to testing that balances coverage, maintainability, and pragmatism. Focus on testing what matters most first, and don't let perfect be the enemy of good.

## Core Principles

### 1. Test Core Functionality First

**Priority order**:
1. Core business logic (agents, workflows, queue)
2. Critical paths (error handling, state management)
3. Integration points (external services)
4. Edge cases and optimizations

**Why**: Get the most value from testing effort. 80% coverage of critical code is better than 100% coverage of trivial code.

### 2. Mock External Dependencies

**Always mock**:
- External APIs (Supabase, Mistral, OpenAI)
- File system operations
- Network calls
- Database connections
- Time-dependent operations

**Why**: Tests should be fast (<1s per test), reliable, and runnable offline.

**Example**:
```python
@pytest.fixture
def mock_supabase(mocker):
    """Mock Supabase client for testing."""
    mock_client = mocker.MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = []
    return mock_client

def test_queue_with_mock(mock_supabase):
    queue = Queue(client=mock_supabase, queue_name="test")
    # Test without hitting real Supabase
```

### 3. Test Error Paths, Not Just Happy Paths

**Test both**:
- ✅ Success cases
- ❌ Failure cases
- ⚠️ Edge cases
- 🔄 Retry logic
- 💥 Exception handling

**Why**: Most bugs happen in error handling code.

**Example**:
```python
def test_queue_handles_job_error():
    """Test that queue handles job errors gracefully."""
    queue = Queue(...)

    # Test error is caught and logged
    with pytest.raises(JobError):
        queue.process_job(invalid_job)

    # Verify error was logged
    assert "Job failed" in caplog.text
```

### 4. Parametrize Similar Tests

**Use `@pytest.mark.parametrize`** for testing multiple inputs:

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    (None, None),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

**Why**: DRY tests, better coverage, easier to add cases.

### 5. Skip Tricky Edge Cases (Pragmatically)

**When to skip**:
- Complex timing issues
- Race conditions
- Platform-specific behavior
- Requires extensive mocking

**How to skip**:
```python
@pytest.mark.skip(reason="Complex timing issue, defer to integration tests")
def test_race_condition():
    pass

@pytest.mark.integration
def test_race_condition_integration():
    # Test in integration suite instead
    pass
```

**Why**: Don't let edge cases block progress on core functionality.

## Testing Workflow

### Phase 1: Core Functionality (Target: 80%)

Focus on the most critical modules:

1. **Queue operations**
   - Send/receive messages
   - Error handling
   - DLQ functionality
   - Retry logic

2. **Worker operations**
   - Job processing
   - Signal handling
   - Graceful shutdown
   - Error recovery

3. **Agent logic**
   - State management
   - Tool execution
   - Response generation
   - Error handling

4. **Workflow orchestration**
   - State transitions
   - Agent coordination
   - Checkpoint management
   - Error propagation

### Phase 2: Integration Points (Target: 85%)

Test how components work together:

1. **External services**
   - Supabase integration
   - LLM providers
   - File storage
   - Message queues

2. **Data flow**
   - Input validation
   - State persistence
   - Output formatting
   - Error propagation

### Phase 3: Edge Cases (Target: 90%+)

Fill in the gaps:

1. **Boundary conditions**
   - Empty inputs
   - Large inputs
   - Invalid inputs
   - Null/None values

2. **Error scenarios**
   - Network failures
   - Timeouts
   - Invalid responses
   - Resource exhaustion

## Test Organization

### Structure

Mirror source structure in tests:

```
src/aimq/
├── agents/
│   ├── base.py
│   └── react.py
tests/aimq/
├── agents/
│   ├── test_base.py
│   └── test_react.py
```

### Naming

- Test files: `test_<module>.py`
- Test functions: `test_<what_it_tests>`
- Test classes: `Test<ClassName>`

### Grouping

Group related tests in classes:

```python
class TestQueueErrorHandling:
    def test_dlq_send_success(self):
        pass

    def test_dlq_not_configured(self):
        pass

    def test_max_retries_with_dlq(self):
        pass
```

## Fixtures

### Common Fixtures

Create reusable fixtures for common setups:

```python
@pytest.fixture
def mock_llm(mocker):
    """Mock LLM for testing."""
    mock = mocker.MagicMock()
    mock.invoke.return_value = "Test response"
    return mock

@pytest.fixture
def sample_agent_state():
    """Sample agent state for testing."""
    return AgentState(
        messages=[],
        next_step="start",
        metadata={}
    )
```

### Fixture Scope

- `function` (default): New instance per test
- `class`: Shared within test class
- `module`: Shared within test file
- `session`: Shared across all tests

## Coverage Goals

### Targets

- **Overall**: 80%+ (good), 90%+ (excellent)
- **Core modules**: 90%+ (agents, workflows, queue, worker)
- **Utilities**: 80%+ (tools, common)
- **Examples**: Not required

### Measuring

```bash
# Run with coverage
pytest --cov=src/aimq --cov-report=term-missing

# Generate HTML report
pytest --cov=src/aimq --cov-report=html

# Check specific module
pytest --cov=src/aimq/agents --cov-report=term-missing
```

### Improving

1. **Find gaps**: Look at coverage report
2. **Prioritize**: Focus on critical uncovered code
3. **Add tests**: Write tests for gaps
4. **Refactor**: Sometimes uncovered code is dead code

## Real-World Example

From our recent work (commit 91c4ae1):

**Goal**: Improve worker and queue coverage

**Approach**:
1. Identified core functionality (signal handling, DLQ)
2. Added 11 focused tests
3. Skipped complex edge cases
4. Fixed deprecation warning while there

**Results**:
- worker.py: 75% → 84% (+9%)
- queue.py: 75% → 93% (+18%)
- Overall: 82% → 84% (+2%)
- Time: ~2 hours

**Lesson**: Systematic, focused testing beats random testing.

## Anti-Patterns

### ❌ Don't

- Test implementation details
- Write brittle tests that break on refactoring
- Mock everything (test real logic)
- Aim for 100% coverage at all costs
- Let edge cases block core testing

### ✅ Do

- Test behavior and contracts
- Write resilient tests
- Mock external dependencies only
- Aim for meaningful coverage
- Defer edge cases pragmatically

## Related

- [@../standards/testing.md](../standards/testing.md) - Testing conventions
- [@test-mocking-external-services.md](./test-mocking-external-services.md) - Mocking patterns
- [@error-handling.md](./error-handling.md) - Error handling patterns
- [@../quick-references/testing.md](../quick-references/testing.md) - Testing quick reference
- [Common Pitfalls](../quick-references/common-pitfalls.md) - Things to avoid

---

**Remember**: Tests are documentation that runs. Write tests that explain what the code does and why! 📝✨
