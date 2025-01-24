# Worker Configuration

AIMQ workers can be configured through both environment variables and programmatic settings. This guide covers all available configuration options and best practices.

## Environment Variables

The following environment variables control worker behavior:

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKER_NAME` | Name of the worker instance | `'peon'` |
| `WORKER_LOG_LEVEL` | Logging level (debug, info, warning, error) | `'info'` |
| `WORKER_IDLE_WAIT` | Time to wait between queue checks (seconds) | `10.0` |

## Programmatic Configuration

You can configure workers programmatically when creating a Worker instance:

```python
from aimq import Worker

worker = Worker(
    name="custom-worker",      # Override worker name
    log_level="debug",        # Set logging level
    idle_wait=5.0            # Set idle wait time
)
```

## Configuration Precedence

Configuration values are determined in the following order (highest to lowest priority):
1. Programmatic configuration
2. Environment variables
3. Default values

## Worker Settings

### Name

The worker name is used to identify the worker instance in logs and monitoring:

```python
# Via environment
WORKER_NAME=analytics-worker

# Via code
worker = Worker(name="analytics-worker")
```

### Log Level

Control the verbosity of worker logs:

```python
# Via environment
WORKER_LOG_LEVEL=debug

# Via code
worker = Worker(log_level="debug")
```

Available log levels:
- `debug`: Detailed debugging information
- `info`: General operational information
- `warning`: Warning messages for potential issues
- `error`: Error messages for actual problems

### Idle Wait

Configure how long the worker waits between checking for new tasks:

```python
# Via environment
WORKER_IDLE_WAIT=5.0

# Via code
worker = Worker(idle_wait=5.0)
```

## Best Practices

1. **Worker Names**
   - Use descriptive names that indicate the worker's purpose
   - Include environment or region in the name if relevant
   - Example: `prod-us-east-analytics-worker`

2. **Log Levels**
   - Use `debug` during development
   - Use `info` in production
   - Use `warning` or `error` for minimal logging

3. **Idle Wait**
   - Lower values (1-5s) for time-sensitive tasks
   - Higher values (10-30s) for background tasks
   - Consider queue volume when setting this value

## Example Configurations

### Development Environment

```python
# .env
WORKER_NAME=dev-worker
WORKER_LOG_LEVEL=debug
WORKER_IDLE_WAIT=5.0
```

### Production Environment

```python
# .env
WORKER_NAME=prod-analytics
WORKER_LOG_LEVEL=info
WORKER_IDLE_WAIT=10.0
```

### Mixed Configuration

```python
# .env
WORKER_NAME=prod-worker
WORKER_LOG_LEVEL=info

# code
worker = Worker(
    name=os.getenv("WORKER_NAME"),
    log_level=os.getenv("WORKER_LOG_LEVEL"),
    idle_wait=5.0  # Override default and env
)
```

## Monitoring and Debugging

1. **Log Output**
   - All worker operations are logged according to log_level
   - Logs include worker name, timestamp, and operation details

2. **Performance Tuning**
   - Monitor worker performance with different idle_wait values
   - Adjust based on queue volume and task processing time

3. **Multiple Workers**
   - Use different names for each worker instance
   - Configure log levels independently for focused debugging
