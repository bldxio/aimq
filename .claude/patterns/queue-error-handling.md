# Queue Error Handling

## Overview

Robust error handling for message queue operations, including dead-letter queues (DLQ), retry logic, and custom error handlers. Ensures failed jobs are never lost and can be analyzed or retried.

## Core Pattern

### The Safety Net

Every queue operation should have multiple layers of protection:

1. **Try to process** the job
2. **Catch errors** if processing fails
3. **Retry** with exponential backoff
4. **Send to DLQ** if max retries exceeded
5. **Log everything** for debugging

## Dead Letter Queue (DLQ)

### What is a DLQ?

A separate queue for jobs that failed after all retry attempts. Think of it as a "failed jobs inbox" for later analysis.

### When to Use

- Job failed after max retries
- Unrecoverable errors (bad data, missing resources)
- Need to analyze failures
- Want to manually retry later

### Implementation

```python
class Queue:
    def __init__(
        self,
        queue_name: str,
        dlq_name: str | None = None,
        max_retries: int = 3,
    ):
        self.queue_name = queue_name
        self.dlq_name = dlq_name
        self.max_retries = max_retries

    def send_to_dlq(self, job: Job, error: Exception) -> None:
        """Send failed job to dead-letter queue."""
        if not self.dlq_name:
            raise ValueError("DLQ not configured")

        dlq_data = {
            "original_queue": self.queue_name,
            "job_id": job.id,
            "attempt_count": job.attempt,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "job_data": job.data,
        }

        self.provider.send(self.dlq_name, dlq_data)
        logger.error(f"Job {job.id} sent to DLQ after {job.attempt} attempts")
```

### DLQ Data Structure

Include everything needed to understand and retry the failure:

```python
{
    "original_queue": "document-processing",
    "job_id": "abc-123",
    "attempt_count": 3,
    "error_type": "ValidationError",
    "error_message": "Invalid document format",
    "timestamp": "2025-11-13T15:30:00Z",
    "job_data": {
        "document_id": "doc-456",
        "user_id": "user-789"
    }
}
```

## Retry Logic

### Exponential Backoff

Don't retry immediately - give the system time to recover:

```python
def calculate_backoff(attempt: int, base_delay: float = 1.0) -> float:
    """Calculate exponential backoff delay."""
    return base_delay * (2 ** attempt)

# Attempt 1: 1s
# Attempt 2: 2s
# Attempt 3: 4s
# Attempt 4: 8s
```

### Max Retries

Set reasonable limits:

```python
MAX_RETRIES = 3  # For transient errors
MAX_RETRIES = 0  # For validation errors (fail fast)
MAX_RETRIES = 10 # For critical operations
```

### Retry Decision

Not all errors should be retried:

```python
def should_retry(error: Exception, attempt: int) -> bool:
    """Decide if error is retryable."""
    # Don't retry validation errors
    if isinstance(error, ValidationError):
        return False

    # Don't retry if max attempts reached
    if attempt >= MAX_RETRIES:
        return False

    # Retry transient errors
    if isinstance(error, (NetworkError, TimeoutError)):
        return True

    # Default: retry
    return True
```

## Custom Error Handlers

### Why Custom Handlers?

Different errors need different handling:

- **Validation errors**: Log and skip
- **Network errors**: Retry with backoff
- **Resource errors**: Alert and escalate
- **Data errors**: Send to DLQ for manual review

### Implementation

```python
class Queue:
    def __init__(
        self,
        queue_name: str,
        error_handler: Callable[[Job, Exception], None] | None = None,
    ):
        self.error_handler = error_handler

    def handle_error(self, job: Job, error: Exception) -> None:
        """Handle job processing error."""
        # Call custom handler if provided
        if self.error_handler:
            try:
                self.error_handler(job, error)
            except Exception as handler_error:
                logger.error(f"Error handler failed: {handler_error}")

        # Default handling
        if job.attempt >= self.max_retries:
            if self.dlq_name:
                self.send_to_dlq(job, error)
            else:
                self.archive_job(job)
        else:
            self.retry_job(job)
```

### Custom Handler Example

```python
def custom_error_handler(job: Job, error: Exception) -> None:
    """Custom error handling logic."""
    if isinstance(error, ValidationError):
        # Log validation errors but don't retry
        logger.warning(f"Validation error for job {job.id}: {error}")
        metrics.increment("validation_errors")

    elif isinstance(error, NetworkError):
        # Alert on network errors
        logger.error(f"Network error for job {job.id}: {error}")
        alert_ops_team(f"Network issues in queue {job.queue}")

    elif isinstance(error, DataError):
        # Send data errors to special queue for review
        send_to_review_queue(job, error)

queue = Queue(
    queue_name="processing",
    error_handler=custom_error_handler,
)
```

## Error Logging

### What to Log

Log everything needed to debug failures:

```python
logger.error(
    f"Job processing failed",
    extra={
        "job_id": job.id,
        "queue": self.queue_name,
        "attempt": job.attempt,
        "max_retries": self.max_retries,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "job_data": job.data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)
```

### Log Levels

- **DEBUG**: Retry attempts
- **INFO**: Successful processing
- **WARNING**: Recoverable errors
- **ERROR**: Failed jobs, DLQ sends
- **CRITICAL**: System failures

## Complete Example

From our codebase (src/aimq/queue.py):

```python
def handle_error(self, job: Job, error: Exception) -> None:
    """Handle job processing error with DLQ support."""
    logger.error(f"Job {job.id} failed: {error}")

    # Call custom error handler if provided
    if self.error_handler:
        try:
            self.error_handler(job, error)
        except Exception as handler_error:
            logger.error(f"Error handler failed: {handler_error}")

    # Check if max retries exceeded
    if job.attempt >= self.max_retries:
        if self.dlq_name:
            # Send to DLQ
            try:
                self.send_to_dlq(job, error)
            except Exception as dlq_error:
                logger.error(f"Failed to send to DLQ: {dlq_error}")
                # Archive as fallback
                self.archive_job(job)
        else:
            # No DLQ configured, archive the job
            self.archive_job(job)
    else:
        # Retry the job
        self.retry_job(job)
```

## Testing

### Test Cases

From our test suite (tests/aimq/test_queue.py):

```python
def test_dlq_send_success(mock_queue):
    """Test successful DLQ send."""
    job = Job(id="123", attempt=3, data={})
    error = Exception("Test error")

    mock_queue.send_to_dlq(job, error)

    # Verify DLQ was called
    mock_queue.provider.send.assert_called_once()
    assert "error_type" in mock_queue.provider.send.call_args[0][1]

def test_dlq_not_configured(mock_queue):
    """Test error when DLQ not configured."""
    mock_queue.dlq_name = None
    job = Job(id="123", attempt=3, data={})

    with pytest.raises(ValueError, match="DLQ not configured"):
        mock_queue.send_to_dlq(job, Exception("Test"))

def test_max_retries_with_dlq(mock_queue):
    """Test job sent to DLQ after max retries."""
    job = Job(id="123", attempt=3, data={})
    mock_queue.max_retries = 3
    mock_queue.dlq_name = "test-dlq"

    mock_queue.handle_error(job, Exception("Test"))

    # Should send to DLQ, not retry
    mock_queue.send_to_dlq.assert_called_once()
    mock_queue.retry_job.assert_not_called()

def test_custom_error_handler(mock_queue):
    """Test custom error handler is called."""
    handler_called = False

    def custom_handler(job, error):
        nonlocal handler_called
        handler_called = True

    mock_queue.error_handler = custom_handler
    job = Job(id="123", attempt=1, data={})

    mock_queue.handle_error(job, Exception("Test"))

    assert handler_called
```

## Best Practices

### ✅ Do

- **Always configure a DLQ** for production queues
- **Log all errors** with full context
- **Use exponential backoff** for retries
- **Set reasonable max retries** (3-5 for most cases)
- **Test error paths** thoroughly
- **Monitor DLQ size** and alert on growth
- **Review DLQ regularly** and fix root causes

### ❌ Don't

- Don't lose failed jobs (always DLQ or archive)
- Don't retry forever (set max retries)
- Don't retry immediately (use backoff)
- Don't ignore DLQ (it's your bug inbox)
- Don't retry validation errors (fail fast)
- Don't crash on error handler failures

## Monitoring

### Metrics to Track

```python
# Job processing
metrics.increment("jobs.processed")
metrics.increment("jobs.failed")
metrics.increment("jobs.retried")

# DLQ
metrics.gauge("dlq.size", dlq_size)
metrics.increment("dlq.sent")

# Error types
metrics.increment(f"errors.{error_type}")
```

### Alerts

- DLQ size growing rapidly
- High error rate (>5%)
- Specific error types spiking
- DLQ send failures

## Related

- [Worker Error Handling](./worker-error-handling.md) - Worker-level error handling
- [Error Handling](./error-handling.md) - General error handling patterns
- [Testing Strategy](./testing-strategy.md) - How to test error handling

---

**Remember**: Failed jobs are data. Capture them, analyze them, learn from them! 📮✨
