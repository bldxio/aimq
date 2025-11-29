# Development Pitfalls

Common mistakes in testing, Git, module organization, performance, and documentation.

## Testing Pitfalls

### Testing Implementation Details

**Problem**: Tests break when refactoring internal code

**Example**:
```python
# ❌ Bad: Testing private attributes
def test_worker_internal_state():
    worker = Worker()
    assert worker._internal_counter == 0  # Breaks on refactor

# ✅ Good: Test public behavior
def test_worker_processes_jobs():
    worker = Worker()
    result = worker.process(job)
    assert result.status == "success"
```

### Not Mocking External Services

**Problem**: Tests are slow, flaky, and require network access

**Example**:
```python
# ❌ Bad: Hitting real API
def test_supabase_query():
    client = get_supabase_client()  # Real API call!
    result = client.table('jobs').select('*').execute()
    assert len(result.data) > 0

# ✅ Good: Mock the client
def test_supabase_query(mocker):
    mock_client = mocker.MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = []
    result = query_jobs(mock_client)
    assert result == []
```

### Brittle Assertions

**Problem**: Tests fail on minor changes

**Example**:
```python
# ❌ Bad: Exact string matching
def test_error_message():
    with pytest.raises(ValueError) as exc:
        raise_error()
    assert str(exc.value) == "Error: something went wrong at line 42"

# ✅ Good: Check for key parts
def test_error_message():
    with pytest.raises(ValueError) as exc:
        raise_error()
    assert "something went wrong" in str(exc.value)
```

## Error Handling Pitfalls

### Re-raising Exceptions in Workers

**Problem**: Worker crashes on job errors

**Example**:
```python
# ❌ Bad: Worker crashes
def worker_loop():
    while True:
        job = queue.receive()
        process_job(job)  # Exception crashes worker

# ✅ Good: Catch and log
def worker_loop():
    while True:
        try:
            job = queue.receive()
            process_job(job)
        except Exception as error:
            logger.error(f"Job failed: {error}")
            # Worker continues
```

**Lesson**: Workers are infrastructure, jobs are data. Infrastructure should never crash on bad data.

### Swallowing Exceptions

**Problem**: Errors are hidden, making debugging impossible

**Example**:
```python
# ❌ Bad: Silent failure
try:
    process_job(job)
except Exception:
    pass  # Error is lost!

# ✅ Good: Log the error
try:
    process_job(job)
except Exception as error:
    logger.error(f"Job failed: {error}", exc_info=True)
    handle_error(job, error)
```

### Not Using Dead Letter Queues

**Problem**: Failed jobs are lost forever

**Example**:
```python
# ❌ Bad: Job is lost
def handle_error(job, error):
    logger.error(f"Job failed: {error}")
    # Job is gone forever

# ✅ Good: Send to DLQ
def handle_error(job, error):
    logger.error(f"Job failed: {error}")
    if job.attempt >= max_retries:
        send_to_dlq(job, error)  # Can analyze later
```

## Git Pitfalls

### Committing Without Testing

**Problem**: Broken code in git history

**Example**:
```bash
# ❌ Bad: Commit without testing
git add .
git commit -m "fix: update worker"
git push
# Tests fail in CI!

# ✅ Good: Test before committing
just test
git add .
git commit -m "fix: update worker"
git push
```

### Vague Commit Messages

**Problem**: Can't understand what changed or why

**Example**:
```bash
# ❌ Bad: Vague messages
git commit -m "fix stuff"
git commit -m "update"
git commit -m "wip"

# ✅ Good: Descriptive messages
git commit -m "fix(worker): handle KeyboardInterrupt gracefully"
git commit -m "test: add coverage for queue error handling"
git commit -m "docs: update VISION.md with multi-agent chat"
```

### Not Using Branches

**Problem**: Can't experiment safely

**Example**:
```bash
# ❌ Bad: Work directly on main
git checkout main
# Make changes
git commit -m "experimental feature"
# Oops, broke main!

# ✅ Good: Use feature branches
git checkout -b feature/new-feature
# Make changes
git commit -m "feat: add new feature"
# Test thoroughly
git checkout dev
git merge feature/new-feature
```

## Module Organization Pitfalls

### Organizing by Type Instead of Domain

**Problem**: Related code is scattered across modules

**Example**:
```
# ❌ Bad: Organized by type
src/
├── models/
│   ├── agent.py
│   ├── workflow.py
│   └── job.py
├── services/
│   ├── agent_service.py
│   ├── workflow_service.py
│   └── job_service.py
└── utils/
    ├── agent_utils.py
    └── workflow_utils.py

# ✅ Good: Organized by domain
src/
├── agents/
│   ├── base.py
│   ├── react.py
│   └── states.py
├── workflows/
│   ├── base.py
│   ├── multi_agent.py
│   └── states.py
└── common/
    ├── llm.py
    └── exceptions.py
```

**Lesson**: Group by functionality/domain, not by type. Related code should live together.

### Circular Imports

**Problem**: Modules import each other, causing import errors

**Example**:
```python
# ❌ Bad: Circular dependency
# agents/base.py
from workflows.base import Workflow

# workflows/base.py
from agents.base import Agent  # Circular!

# ✅ Good: Use common module
# common/types.py
class Agent: ...
class Workflow: ...

# agents/base.py
from common.types import Workflow

# workflows/base.py
from common.types import Agent
```

## Performance Pitfalls

### Not Using Connection Pools

**Problem**: Creating new connections for every request

**Example**:
```python
# ❌ Bad: New connection each time
def query_database():
    conn = create_connection()  # Slow!
    result = conn.query("SELECT ...")
    conn.close()
    return result

# ✅ Good: Use connection pool
pool = create_connection_pool()

def query_database():
    with pool.connection() as conn:
        return conn.query("SELECT ...")
```

### Synchronous I/O in Async Code

**Problem**: Blocking the event loop

**Example**:
```python
# ❌ Bad: Blocking I/O in async function
async def process_file(path):
    with open(path) as f:  # Blocks event loop!
        data = f.read()
    return data

# ✅ Good: Use async I/O
async def process_file(path):
    async with aiofiles.open(path) as f:
        data = await f.read()
    return data
```

## Documentation Pitfalls

### Outdated Documentation

**Problem**: Docs don't match reality

**Example**:
```python
# ❌ Bad: Outdated docstring
def process_job(job, retries=3):
    """Process a job with up to 5 retries."""  # Says 5, default is 3!
    ...

# ✅ Good: Accurate docstring
def process_job(job, retries=3):
    """Process a job with up to 3 retries (default)."""
    ...
```

**How to avoid**:
- Update docs when changing code
- Review docs during code review
- Use type hints (they're always accurate)
- Keep docs close to code

### Over-documenting

**Problem**: Too much documentation, hard to maintain

**Example**:
```python
# ❌ Bad: Obvious comments
def add(a, b):
    """Add two numbers together.

    Args:
        a: The first number to add
        b: The second number to add

    Returns:
        The sum of a and b

    Example:
        >>> add(1, 2)
        3
    """
    return a + b  # Return the sum

# ✅ Good: Document the why, not the what
def calculate_backoff(attempt, base_delay=1.0):
    """Calculate exponential backoff delay.

    Uses exponential backoff to avoid overwhelming services
    during transient failures.
    """
    return base_delay * (2 ** attempt)
```

## Related

- [@.claude/patterns/error-handling.md](../patterns/error-handling.md) - Error handling patterns
- [@.claude/patterns/testing-strategy.md](../patterns/testing-strategy.md) - Testing best practices
- [@.claude/patterns/module-organization.md](../patterns/module-organization.md) - Code organization
- [@.claude/standards/git-workflow.md](../standards/git-workflow.md) - Git best practices
- [@.claude/quick-references/common-pitfalls.md](./common-pitfalls.md) - All pitfalls index

---

**Remember**: Good practices prevent problems before they happen! 🛡️✨
