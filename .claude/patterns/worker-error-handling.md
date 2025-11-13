# Worker Error Handling

## Overview

Workers should never crash on job errors. This pattern ensures workers remain stable and continue processing jobs even when individual jobs fail.

## Core Principle

**Workers are infrastructure, jobs are data.**

- Infrastructure should be stable and long-running
- Data (jobs) can be invalid, malformed, or cause errors
- One bad job should never take down the worker

## The Golden Rule

```python
# ❌ DON'T: Let job errors crash the worker
def worker_loop():
    while True:
        job = queue.receive()
        process_job(job)  # If this raises, worker dies!

# ✅ DO: Catch and handle job errors
def worker_loop():
    while True:
        try:
            job = queue.receive()
            process_job(job)
        except Exception as error:
            logger.error(f"Job failed: {error}")
            # Worker continues running
```

## Implementation Pattern

### Basic Worker Loop

```python
class Worker:
    def __init__(self, queue: Queue):
        self.queue = queue
        self.running = False

    def start(self):
        """Start the worker loop."""
        self.running = True
        logger.info("Worker started")

        while self.running:
            try:
                # Get next job
                job = self.queue.receive()
                if not job:
                    time.sleep(1)
                    continue

                # Process job
                try:
                    result = self.process_job(job)
                    self.queue.ack(job)
                    logger.info(f"Job {job.id} completed")

                except Exception as job_error:
                    # Job failed, but worker continues
                    logger.error(f"Job {job.id} failed: {job_error}")
                    self.queue.handle_error(job, job_error)

            except KeyboardInterrupt:
                # User wants to stop
                logger.info("Received interrupt, shutting down...")
                self.stop()

            except Exception as worker_error:
                # Worker-level error (queue connection, etc.)
                logger.critical(f"Worker error: {worker_error}")
                # Decide: retry or stop?
                if self.is_fatal(worker_error):
                    self.stop()
                else:
                    time.sleep(5)  # Back off and retry
```

### Error Categories

Different errors need different handling:

```python
def handle_error(self, error: Exception) -> None:
    """Handle error based on type."""

    # Job-level errors (continue processing)
    if isinstance(error, (ValidationError, DataError)):
        logger.error(f"Job error: {error}")
        # Worker continues
        return

    # Transient errors (retry)
    if isinstance(error, (NetworkError, TimeoutError)):
        logger.warning(f"Transient error: {error}")
        time.sleep(5)  # Back off
        return

    # Fatal errors (stop worker)
    if isinstance(error, (ConfigError, AuthError)):
        logger.critical(f"Fatal error: {error}")
        self.stop()
        return

    # Unknown errors (log and continue)
    logger.error(f"Unknown error: {error}", exc_info=True)
```

## Graceful Shutdown

### Signal Handling

Workers should respond to shutdown signals:

```python
import signal
import sys

class Worker:
    def __init__(self):
        self.running = False
        self.shutdown_requested = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signal gracefully."""
        if self.shutdown_requested:
            # Second signal = force quit
            logger.warning("Force quit requested")
            sys.exit(1)

        # First signal = graceful shutdown
        logger.info("Shutdown requested, finishing current job...")
        self.shutdown_requested = True
        self.running = False
```

### Graceful vs Force Quit

**First Ctrl+C (SIGINT)**:
- Finish current job
- Clean up resources
- Exit gracefully

**Second Ctrl+C (SIGINT)**:
- Stop immediately
- Exit with error code

```python
def start(self):
    """Start worker with graceful shutdown."""
    self.running = True
    current_job = None

    try:
        while self.running:
            current_job = self.queue.receive()
            if current_job:
                self.process_job(current_job)
                current_job = None

    except KeyboardInterrupt:
        if current_job:
            logger.info("Finishing current job before shutdown...")
            try:
                self.process_job(current_job)
            except Exception as e:
                logger.error(f"Job failed during shutdown: {e}")

        logger.info("Worker stopped gracefully")
```

## Testing

### Test Cases

From our test suite (tests/aimq/test_worker.py):

```python
def test_worker_handles_job_error(mock_worker):
    """Test worker continues after job error."""
    mock_worker.queue.receive.side_effect = [
        Job(id="1", data={}),
        Job(id="2", data={}),
        None,  # Stop
    ]

    # First job raises error
    mock_worker.process_job.side_effect = [
        Exception("Job 1 failed"),
        "success",
    ]

    mock_worker.start()

    # Worker should process both jobs
    assert mock_worker.process_job.call_count == 2

def test_graceful_shutdown(mock_worker):
    """Test worker finishes current job on shutdown."""
    current_job = Job(id="1", data={})
    mock_worker.queue.receive.return_value = current_job

    # Simulate Ctrl+C after receiving job
    def process_with_interrupt(job):
        mock_worker.running = False
        raise KeyboardInterrupt()

    mock_worker.process_job.side_effect = process_with_interrupt

    mock_worker.start()

    # Should attempt to finish job
    assert mock_worker.process_job.called

def test_force_quit(mock_worker):
    """Test force quit on second signal."""
    signal_count = 0

    def handle_signal(signum, frame):
        nonlocal signal_count
        signal_count += 1
        if signal_count == 2:
            sys.exit(1)

    signal.signal(signal.SIGINT, handle_signal)

    # Send two signals
    os.kill(os.getpid(), signal.SIGINT)
    os.kill(os.getpid(), signal.SIGINT)

    # Should exit with error code
    assert signal_count == 2
```

## Real-World Example

From our codebase (src/aimq/worker.py):

```python
def start(self):
    """Start the worker."""
    self.running = True
    logger.info(f"Worker started, listening to queue: {self.queue.queue_name}")

    while self.running:
        try:
            # Receive job from queue
            job = self.queue.receive()
            if not job:
                time.sleep(self.poll_interval)
                continue

            # Process job
            try:
                result = self.process_job(job)
                self.queue.ack(job)
                logger.info(f"Job {job.id} completed successfully")

            except Exception as job_error:
                # Job failed, but worker continues
                logger.error(f"Job {job.id} failed: {job_error}")
                self.queue.handle_error(job, job_error)

        except (KeyboardInterrupt, SystemExit):
            # Graceful shutdown
            logger.info("Shutdown signal received")
            self.stop()

        except Exception as worker_error:
            # Worker-level error
            logger.critical(f"Worker error: {worker_error}", exc_info=True)
            # Continue running (don't crash)
```

## Best Practices

### ✅ Do

- **Catch all exceptions** in the worker loop
- **Log errors** with full context
- **Continue processing** after job errors
- **Handle signals** gracefully
- **Finish current job** before shutdown
- **Test error paths** thoroughly
- **Monitor worker health**

### ❌ Don't

- Don't let job errors crash the worker
- Don't ignore errors silently
- Don't exit immediately on first error
- Don't process jobs during shutdown
- Don't lose current job on shutdown
- Don't ignore signal handlers

## Error Recovery

### Transient Errors

For temporary issues (network, rate limits):

```python
def handle_transient_error(self, error: Exception) -> None:
    """Handle transient error with backoff."""
    logger.warning(f"Transient error: {error}")

    # Exponential backoff
    backoff = min(self.backoff * 2, self.max_backoff)
    logger.info(f"Backing off for {backoff}s")
    time.sleep(backoff)

    self.backoff = backoff
```

### Fatal Errors

For unrecoverable issues (config, auth):

```python
def handle_fatal_error(self, error: Exception) -> None:
    """Handle fatal error by stopping worker."""
    logger.critical(f"Fatal error: {error}")

    # Clean up resources
    self.cleanup()

    # Stop worker
    self.stop()

    # Exit with error code
    sys.exit(1)
```

## Monitoring

### Health Checks

```python
def health_check(self) -> dict:
    """Return worker health status."""
    return {
        "running": self.running,
        "jobs_processed": self.jobs_processed,
        "jobs_failed": self.jobs_failed,
        "uptime": time.time() - self.start_time,
        "last_job": self.last_job_time,
    }
```

### Metrics

```python
# Worker metrics
metrics.gauge("worker.running", 1 if self.running else 0)
metrics.gauge("worker.uptime", time.time() - self.start_time)
metrics.increment("worker.jobs_processed")
metrics.increment("worker.jobs_failed")

# Error metrics
metrics.increment(f"worker.errors.{error_type}")
```

### Alerts

- Worker stopped unexpectedly
- High error rate (>5%)
- No jobs processed in X minutes
- Worker restart loop

## Related

- [Queue Error Handling](./queue-error-handling.md) - Queue-level error handling
- [Error Handling](./error-handling.md) - General error handling patterns
- [Testing Strategy](./testing-strategy.md) - How to test error handling

---

**Remember**: Workers are infrastructure. Infrastructure should be boring, stable, and reliable! 🛡️✨
