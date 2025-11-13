# Common Pitfalls

## Overview

Common mistakes and how to avoid them. Learn from others' mistakes so you don't have to make them yourself!

## Python Pitfalls

### Deprecation Warnings

**Problem**: Using deprecated APIs that will break in future versions

**Example**:
```python
# ❌ Deprecated (Python 3.12+)
from datetime import datetime
timestamp = datetime.utcnow()

# ✅ Current
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc)
```

**Why it matters**: Deprecated APIs will be removed in future versions, causing breaking changes.

**How to avoid**:
- Always fix deprecation warnings when you see them
- Run tests with warnings enabled: `pytest -W default`
- Keep dependencies updated
- Check release notes for deprecations

### Mutable Default Arguments

**Problem**: Using mutable objects as default arguments

**Example**:
```python
# ❌ Bad: List is shared across calls
def add_item(item, items=[]):
    items.append(item)
    return items

add_item(1)  # [1]
add_item(2)  # [1, 2] - Oops!

# ✅ Good: Use None and create new list
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### None Type Errors

**Problem**: Not checking for None before accessing attributes

**Example**:
```python
# ❌ Bad: Crashes if result is None
def process_result(result):
    return result.data  # AttributeError if result is None

# ✅ Good: Check for None first
def process_result(result):
    if result is None:
        return None
    return result.data

# ✅ Better: Use optional chaining (Python 3.10+)
def process_result(result):
    return result.data if result else None
```

**How to avoid**:
- Use type hints: `result: Optional[Result]`
- Check for None before accessing
- Use mypy for static type checking
- Test with None values

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

## Message Agent Pitfalls

### Message Serialization for Queues

**Problem**: LangChain message objects (HumanMessage, AIMessage) are not JSON serializable.

**Symptom**:
```python
TypeError: Object of type HumanMessage is not JSON serializable
```

**Root Cause**: Queue systems need JSON-serializable data, but LangChain messages are Python objects with complex internal state.

**Example**:
```python
from langchain_core.messages import HumanMessage

# ❌ Bad: Sending LangChain message objects to queue
message = HumanMessage(content="Hello!")
queue.send({
    "messages": [message]  # Not JSON serializable!
})

# ✅ Good: Convert to dict before sending
queue.send({
    "messages": [{"role": "user", "content": "Hello!"}]
})

# ✅ Also good: Use message.dict() if available
queue.send({
    "messages": [message.dict()]
})
```

**When It Happens**:
- Sending messages to queues (pgmq, Redis, etc.)
- Storing messages in databases
- Passing messages between services
- Any boundary crossing (network, storage, etc.)

**Prevention**:
- Always serialize at boundaries
- Test with actual queue/database early
- Use `message.dict()` or manual conversion
- Consider using message schemas (Pydantic)

**From Message Agent**:
```python
# Initial bug
job_data = {
    "messages": [HumanMessage(content=body)],  # ❌ Failed
    "metadata": metadata
}

# Fixed version
job_data = {
    "messages": [{"role": "user", "content": body}],  # ✅ Works
    "metadata": metadata
}
```

### Regex Edge Cases: Email Addresses

**Problem**: Simple @mention regex matches email addresses.

**Symptom**:
```python
mentions = detect_mentions("Contact user@example.com")
# Returns: ["user", "example"]  # ❌ Wrong!
```

**Root Cause**: The `@` symbol appears in both mentions and email addresses.

**Example**:
```python
# ❌ Bad: Matches emails as mentions
pattern = r'@(\w+)'
re.findall(pattern, "user@example.com")  # ["user", "example"]

# ✅ Good: Use word boundaries
pattern = r'@(\w+)(?=\s|$|[^\w@])'
re.findall(pattern, "user@example.com")  # []

# ✅ Also good: Negative lookbehind/lookahead
pattern = r'(?<!\w)@(\w+)(?!\w)'
```

**Test Cases**:
```python
def test_detect_mentions_ignores_emails():
    """Should not detect email addresses as mentions."""
    assert detect_mentions("user@example.com") == []
    assert detect_mentions("Contact: admin@site.org") == []

def test_detect_mentions_with_email_and_mention():
    """Should detect mentions but not emails."""
    text = "Hey @alice, email me at bob@example.com"
    assert detect_mentions(text) == ["alice"]
```

**Prevention**:
- Test regex with real-world data
- Consider edge cases (emails, URLs, etc.)
- Use word boundaries when appropriate
- Write comprehensive tests

**From Message Agent**:
```python
# Initial regex
r'@(\w+)'  # ❌ Matched emails

# Fixed regex
r'@(\w+)(?=\s|$|[^\w@])'  # ✅ Ignores emails
```

### pgmq Function Signatures

**Problem**: Calling pgmq functions with incorrect parameter names or structure.

**Symptom**:
```python
APIError: {'message': 'Could not find the function public.pgmq_send(msg, queue_name)
in the schema cache', 'code': 'PGRST202'}
```

**Root Cause**: pgmq functions have specific parameter names and order that must match exactly.

**Example**:
```python
# ❌ Bad: Wrong parameter names
supabase.rpc("pgmq_send", {
    "msg": payload,
    "queue_name": "my-queue"
})

# ✅ Good: Correct parameter names (check pgmq docs)
supabase.rpc("pgmq_send", {
    "queue_name": "my-queue",
    "msg": payload
})
```

**Prevention**:
- Check pgmq documentation for exact function signatures
- Test with actual Supabase instance early
- Use type hints if available
- Log function calls for debugging

**Common pgmq Functions**:
```python
# Send message
supabase.rpc("pgmq_send", {
    "queue_name": str,
    "msg": dict
})

# Read messages
supabase.rpc("pgmq_read", {
    "queue_name": str,
    "vt": int,  # visibility timeout
    "qty": int  # quantity
})

# Archive message
supabase.rpc("pgmq_archive", {
    "queue_name": str,
    "msg_id": int
})

# Delete message
supabase.rpc("pgmq_delete", {
    "queue_name": str,
    "msg_id": int
})
```

**From Message Agent**:
- Initial demo script had incorrect function names
- Fixed by checking pgmq documentation
- Added error handling for missing functions

## Related

- [Error Handling](../patterns/error-handling.md) - Error handling patterns
- [Testing Strategy](../patterns/testing-strategy.md) - Testing best practices
- [Module Organization](../patterns/module-organization.md) - Code organization
- [Git Workflow](../standards/git-workflow.md) - Git best practices
- [LLM API Differences](./llm-api-differences.md) - Provider API compatibility

---

**Remember**: Learn from mistakes, but don't be afraid to make them! 🎓✨
