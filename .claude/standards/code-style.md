# Code Style Standards

## Overview

AIMQ follows PEP 8 with some project-specific conventions. We use automated tools (black, flake8) to enforce consistency.

## Formatting Tools

```bash
# Format code with black
just format

# Lint with flake8
just lint

# Type check with mypy
just type-check

# Run all checks
just ci
```

## Line Length

- **Max line length**: 100 characters (configured in `.flake8`)
- **Prefer shorter**: Aim for 80-90 when possible
- **Break long lines**: Use parentheses for implicit line continuation

```python
# ✅ Good: Implicit line continuation
result = some_function(
    argument1,
    argument2,
    argument3,
)

# ✅ Good: Break long strings
message = (
    "This is a very long message that would exceed "
    "the line length limit if written on one line"
)

# ❌ Bad: Line too long
result = some_function(argument1, argument2, argument3, argument4, argument5, argument6, argument7)
```

## Naming Conventions

### Classes
**PascalCase** for class names:
```python
class WorkerThread:
    pass

class QueueProvider:
    pass

class ReActAgent:
    pass
```

### Functions and Methods
**snake_case** for functions and methods:
```python
def process_job(data: dict) -> dict:
    pass

def send_message(queue: str, data: dict) -> None:
    pass

def get_supabase_client() -> Client:
    pass
```

### Constants
**UPPER_SNAKE_CASE** for constants:
```python
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300
QUEUE_POLL_INTERVAL = 1.0
```

### Private Attributes
**Leading underscore** for private/internal:
```python
class Worker:
    def __init__(self):
        self._internal_state = {}  # Private
        self.public_state = {}     # Public
```

### Module Names
**snake_case** for module names:
```python
# ✅ Good
worker.py
queue_provider.py
react_agent.py

# ❌ Bad
Worker.py
QueueProvider.py
ReactAgent.py
```

## Type Hints

**Always use type hints** for function signatures:

```python
# ✅ Good: Full type hints
def process_job(data: dict[str, Any]) -> dict[str, Any]:
    return {"status": "success"}

def get_queue(name: str) -> Queue | None:
    return queues.get(name)

# ❌ Bad: No type hints
def process_job(data):
    return {"status": "success"}
```

Use modern type hint syntax (Python 3.11+):
```python
# ✅ Good: Modern syntax
def get_items() -> list[str]:
    pass

def get_mapping() -> dict[str, int]:
    pass

def get_optional(key: str) -> str | None:
    pass

# ❌ Bad: Old syntax (pre-3.10)
from typing import List, Dict, Optional

def get_items() -> List[str]:
    pass

def get_mapping() -> Dict[str, int]:
    pass

def get_optional(key: str) -> Optional[str]:
    pass
```

## Imports

### Order
1. Standard library
2. Third-party packages
3. Local imports

```python
# ✅ Good: Organized imports
import os
import sys
from datetime import datetime

from langchain.schema import BaseMessage
from supabase import Client

from aimq.config import config
from aimq.queue import Queue
```

### Style
```python
# ✅ Good: Explicit imports
from aimq.agents.react import ReActAgent
from aimq.workflows.document import DocumentWorkflow

# ❌ Bad: Wildcard imports
from aimq.agents import *
from aimq.workflows import *

# ❌ Bad: Importing entire modules when you only need one thing
import aimq.agents.react
agent = aimq.agents.react.ReActAgent()  # Too verbose
```

## Function Length

**Prefer small functions** (max ~50 lines):

```python
# ✅ Good: Small, focused function
def process_job(job: Job) -> dict[str, Any]:
    validate_job(job)
    result = execute_job(job)
    archive_job(job)
    return result

# ❌ Bad: Large, monolithic function
def process_job(job: Job) -> dict[str, Any]:
    # 100+ lines of logic
    # Hard to test, hard to understand
    ...
```

## Error Handling

### Use Specific Exceptions
```python
# ✅ Good: Specific exceptions
from aimq.common.exceptions import QueueNotFoundError, JobValidationError

def get_queue(name: str) -> Queue:
    if name not in queues:
        raise QueueNotFoundError(f"Queue '{name}' not found")
    return queues[name]

# ❌ Bad: Generic exceptions
def get_queue(name: str) -> Queue:
    if name not in queues:
        raise Exception("Queue not found")  # Too generic!
    return queues[name]
```

### Early Returns
```python
# ✅ Good: Early return for error cases
def process_job(job: Job | None) -> dict[str, Any]:
    if job is None:
        return {"status": "error", "message": "No job provided"}

    if not job.data:
        return {"status": "error", "message": "Empty job data"}

    # Main logic here
    return {"status": "success"}

# ❌ Bad: Nested conditionals
def process_job(job: Job | None) -> dict[str, Any]:
    if job is not None:
        if job.data:
            # Main logic here
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Empty job data"}
    else:
        return {"status": "error", "message": "No job provided"}
```

## Documentation

### Docstrings
Use docstrings for public APIs:

```python
def process_job(job: Job) -> dict[str, Any]:
    """Process a job from the queue.

    Args:
        job: The job to process

    Returns:
        Result dictionary with status and data

    Raises:
        JobValidationError: If job data is invalid
    """
    ...
```

### Comments
Use comments sparingly—prefer self-documenting code:

```python
# ✅ Good: Self-documenting
def archive_completed_job(job: Job) -> None:
    provider.archive(job.id)

# ❌ Bad: Unnecessary comment
def archive_job(job: Job) -> None:
    # Archive the job
    provider.archive(job.id)  # This comment adds no value
```

Use comments for **why**, not **what**:

```python
# ✅ Good: Explains why
# Use timeout=0 to immediately delete messages instead of archiving
# This is required for high-throughput queues to avoid archive bloat
queue = Queue("fast-queue", timeout=0)

# ❌ Bad: Explains what (obvious from code)
# Create a queue with timeout 0
queue = Queue("fast-queue", timeout=0)
```

## Code Organization

### Class Structure
```python
class Worker:
    # 1. Class variables
    DEFAULT_TIMEOUT = 300

    # 2. __init__
    def __init__(self, name: str):
        self.name = name
        self._queues = {}

    # 3. Public methods
    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...

    # 4. Private methods
    def _process_queue(self, queue: Queue) -> None:
        ...

    # 5. Properties
    @property
    def is_running(self) -> bool:
        return self._running
```

### Module Structure
```python
# 1. Module docstring
"""Worker module for processing queue jobs."""

# 2. Imports
import os
from datetime import datetime

from langchain.schema import Runnable

from aimq.config import config

# 3. Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300

# 4. Classes
class Worker:
    ...

# 5. Functions
def create_worker(name: str) -> Worker:
    ...

# 6. Main block (if applicable)
if __name__ == "__main__":
    ...
```

## Flake8 Configuration

From `.flake8`:
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503, E501
max-complexity = 10
```

**Ignored rules**:
- `E203`: Whitespace before ':' (conflicts with black)
- `W503`: Line break before binary operator (conflicts with black)
- `E501`: Line too long (handled by black)

**Max complexity**: 10 (cyclomatic complexity)

## Black Configuration

From `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py311', 'py312', 'py313']
```

## Related

- See `quick-references/linting.md` for quick commands
- See `CONSTITUTION.md` for non-negotiable style rules
- See `CLAUDE.md` for detailed conventions
