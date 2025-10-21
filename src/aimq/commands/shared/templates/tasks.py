"""Template task definitions for AIMQ.

This module provides example task definitions that demonstrate how to create and use
worker tasks in AIMQ. These templates can be used as starting points for creating
your own task definitions.
"""

from typing import Any, Dict

from aimq.worker import Worker

# Create a worker instance to handle task processing
worker = Worker()


@worker.task()
def example(data: Dict[str, Any]) -> Dict[str, str]:
    """Example task that converts input text to uppercase.

    This is a simple example task that demonstrates the basic pattern for
    creating worker tasks in AIMQ. It takes a dictionary with a 'text' key
    and returns a dictionary with the uppercase version of that text.

    Args:
        data: Dictionary containing task data with a 'text' key.

    Returns:
        Dictionary with 'result' key containing the uppercase text.

    Example:
        ```python
        result = await worker.enqueue('example', {'text': 'hello'})
        assert result['result'] == 'HELLO'
        ```
    """
    text = data.get("text", "")
    return {"result": text.upper()}


if __name__ == "__main__":
    # Start the worker to begin processing tasks from all queues
    worker.start()
