"""
Basic task example demonstrating simple text processing tasks.
This module provides examples of:
1. Creating tasks with default configurations
2. Creating tasks with custom queue names and settings
3. Basic text processing operations
"""

from typing import Any, Dict

from aimq.worker import Worker

# Create a worker instance to handle task processing
worker = Worker()

# Task Definitions


@worker.task()
def uppercase_text(data: Dict[str, Any]) -> Dict[str, str]:
    """Convert input text to uppercase.

    Args:
        data (dict): Input dictionary containing 'text' key with the string to process

    Returns:
        dict: Dictionary with 'result' key containing the uppercase version of input text
    """
    text = data.get("text", "")
    return {"result": text.upper()}


@worker.task(
    queue="text_stats",  # Custom queue name for text statistics processing
    timeout=10,  # Maximum time (in seconds) allowed for task execution
    delete_on_finish=True,  # Remove task from queue after successful completion
)
def text_statistics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate basic statistics about the input text.

    Args:
        data (dict): Input dictionary containing 'text' key with the string to analyze

    Returns:
        dict: Dictionary containing:
            - word_count: Number of words in the text
            - char_count: Total number of characters
            - avg_word_length: Average length of words
    """
    text = data.get("text", "")
    words = text.split()

    results = {
        "word_count": len(words),
        "char_count": len(text),
        "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
    }
    return results


if __name__ == "__main__":
    # Start the worker to begin processing tasks from all queues
    worker.start()
