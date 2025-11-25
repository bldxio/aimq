# Error Handling Pattern

## Overview

AIMQ uses custom exceptions and consistent error handling patterns to make debugging easier and provide clear error messages.

## Custom Exceptions

All custom exceptions are defined in `common/exceptions.py`:

```python
from aimq.common.exceptions import (
    QueueNotFoundError,
    JobValidationError,
    ProviderError,
    AgentError,
    WorkflowError,
)
```

## Exception Hierarchy

```
Exception
└── AIMQError (base for all AIMQ exceptions)
    ├── QueueNotFoundError
    ├── JobValidationError
    ├── ProviderError
    ├── AgentError
    └── WorkflowError
```

## When to Use Custom Exceptions

### ✅ Use Custom Exceptions For:
- Domain-specific errors (queue not found, job validation failed)
- Errors that need special handling
- Errors that users/developers need to catch specifically
- Errors with additional context

### ❌ Don't Use Custom Exceptions For:
- Standard Python errors (ValueError, TypeError, KeyError)
- Errors from external libraries (let them propagate)
- Temporary/debugging errors

## Pattern: Raise Specific Exceptions

```python
# ✅ Good: Specific exception with context
def get_queue(name: str) -> Queue:
    if name not in self._queues:
        raise QueueNotFoundError(
            f"Queue '{name}' not found. "
            f"Available queues: {list(self._queues.keys())}"
        )
    return self._queues[name]

# ❌ Bad: Generic exception
def get_queue(name: str) -> Queue:
    if name not in self._queues:
        raise Exception("Queue not found")  # Too generic!
    return self._queues[name]
```

## Pattern: Early Returns for Validation

```python
# ✅ Good: Early returns with clear errors
def process_job(job: Job | None) -> dict[str, Any]:
    if job is None:
        raise JobValidationError("Job cannot be None")

    if not job.data:
        raise JobValidationError("Job data cannot be empty")

    if "task" not in job.data:
        raise JobValidationError("Job data must contain 'task' field")

    # Main logic here
    return execute_task(job)

# ❌ Bad: Nested conditionals
def process_job(job: Job | None) -> dict[str, Any]:
    if job is not None:
        if job.data:
            if "task" in job.data:
                return execute_task(job)
            else:
                raise JobValidationError("Missing task")
        else:
            raise JobValidationError("Empty data")
    else:
        raise JobValidationError("No job")
```

## Pattern: Try-Except with Context

```python
# ✅ Good: Catch specific exceptions, add context
def invoke_runnable(runnable: Runnable, data: dict) -> dict:
    try:
        return runnable.invoke(data)
    except ValueError as e:
        raise JobValidationError(f"Invalid job data: {e}") from e
    except TimeoutError as e:
        raise ProviderError(f"Runnable timed out: {e}") from e
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in runnable: {e}", exc_info=True)
        raise

# ❌ Bad: Catch all exceptions without context
def invoke_runnable(runnable: Runnable, data: dict) -> dict:
    try:
        return runnable.invoke(data)
    except Exception:
        raise Exception("Error")  # Lost context!
```

## Pattern: Logging Errors

```python
from aimq.logger import logger

# ✅ Good: Log with context and exc_info
def process_queue(queue: Queue) -> None:
    try:
        job = queue.read()
        result = queue.process(job)
    except QueueNotFoundError as e:
        logger.error(f"Queue error: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error processing queue '{queue.name}': {e}",
            exc_info=True,  # Include stack trace
            extra={
                "queue_name": queue.name,
                "job_id": job.id if job else None,
            }
        )
        raise

# ❌ Bad: No logging or context
def process_queue(queue: Queue) -> None:
    try:
        job = queue.read()
        result = queue.process(job)
    except Exception:
        raise  # No logging, no context
```

## Pattern: Error Recovery

```python
# ✅ Good: Graceful degradation
def get_llm(provider: str = "openai") -> BaseChatModel:
    try:
        if provider == "openai":
            return ChatOpenAI()
        elif provider == "anthropic":
            return ChatAnthropic()
    except Exception as e:
        logger.warning(f"Failed to initialize {provider}: {e}")
        # Fall back to default
        logger.info("Falling back to OpenAI")
        return ChatOpenAI()

# ✅ Good: Retry with backoff
def send_message(queue: str, data: dict, retries: int = 3) -> int:
    for attempt in range(retries):
        try:
            return provider.send(queue, data)
        except ProviderError as e:
            if attempt == retries - 1:
                raise
            logger.warning(f"Retry {attempt + 1}/{retries}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Pattern: Context Managers for Cleanup

```python
from contextlib import contextmanager

# ✅ Good: Ensure cleanup even on error
@contextmanager
def worker_context(worker: Worker):
    """Context manager for worker lifecycle"""
    try:
        worker.start()
        yield worker
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
        raise
    finally:
        worker.stop()  # Always cleanup

# Usage
with worker_context(worker) as w:
    w.process_queues()
```

## Pattern: Error Messages

```python
# ✅ Good: Helpful error messages
raise QueueNotFoundError(
    f"Queue '{queue_name}' not found. "
    f"Available queues: {list(queues.keys())}. "
    f"Did you forget to register it with @worker.task()?"
)

# ✅ Good: Include relevant context
raise JobValidationError(
    f"Invalid job data for queue '{queue_name}': "
    f"missing required field 'task'. "
    f"Received: {job.data}"
)

# ❌ Bad: Vague error messages
raise QueueNotFoundError("Queue not found")
raise JobValidationError("Invalid data")
```

## Pattern: Type Checking for Errors

```python
# ✅ Good: Type hints prevent errors
def process_job(job: Job) -> dict[str, Any]:
    # Type checker ensures job is not None
    return {"status": "success", "job_id": job.id}

# ✅ Good: Handle optional types explicitly
def get_job(job_id: int) -> Job | None:
    return jobs.get(job_id)

def process_job_by_id(job_id: int) -> dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        raise JobValidationError(f"Job {job_id} not found")
    return process_job(job)
```

## Anti-Patterns to Avoid

### ❌ Bare Except
```python
# BAD: Catches everything, including KeyboardInterrupt
try:
    process()
except:
    pass
```

### ❌ Swallowing Exceptions
```python
# BAD: Error is hidden
try:
    critical_operation()
except Exception:
    pass  # Silent failure!
```

### ❌ Raising Generic Exceptions
```python
# BAD: No context, hard to debug
if not valid:
    raise Exception("Error")
```

### ❌ Catching Without Re-raising
```python
# BAD: Error is logged but not propagated
try:
    process()
except Exception as e:
    logger.error(f"Error: {e}")
    # Should re-raise!
```

### ❌ Too Broad Exception Handling
```python
# BAD: Catches too much
try:
    result = complex_operation()
    process_result(result)
    save_to_database(result)
except Exception:
    # Which operation failed?
    pass
```

## Testing Error Handling

```python
import pytest

def test_queue_not_found_error():
    """Test that QueueNotFoundError is raised for missing queue"""
    worker = Worker()

    with pytest.raises(QueueNotFoundError) as exc_info:
        worker.get_queue("non-existent")

    # Check error message
    assert "non-existent" in str(exc_info.value)
    assert "Available queues" in str(exc_info.value)

def test_job_validation_error():
    """Test that JobValidationError is raised for invalid data"""
    queue = Queue("test-queue")
    job = Job(id=1, data={}, ...)  # Missing 'task' field

    with pytest.raises(JobValidationError) as exc_info:
        queue.process(job)

    assert "task" in str(exc_info.value).lower()
```

## Best Practices

1. **Use specific exceptions**: Create custom exceptions for domain errors
2. **Add context**: Include relevant information in error messages
3. **Log errors**: Use logger with exc_info=True for stack traces
4. **Fail fast**: Validate early, raise errors immediately
5. **Clean up resources**: Use context managers or try-finally
6. **Test error cases**: Write tests for error conditions
7. **Document exceptions**: Note which exceptions functions can raise

## Related

- [@../standards/testing.md](../standards/testing.md) - Testing error handling
- [@worker-error-handling.md](./worker-error-handling.md) - Worker-specific error patterns
- [@queue-error-handling.md](./queue-error-handling.md) - Queue error patterns
- [@../../CONSTITUTION.md](../../CONSTITUTION.md) - Error handling non-negotiables
