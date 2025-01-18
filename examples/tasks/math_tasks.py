"""
Math processing workflows for demonstration.
"""

from langchain_core.runnables import chain

@chain
def calculate_sum(data: dict) -> dict:
    """Calculate sum of provided numbers."""
    numbers = data.get('numbers', [])
    return {'result': sum(numbers)}

@chain
def calculate_average(data: dict) -> dict:
    """Calculate average of provided numbers."""
    numbers = data.get('numbers', [])
    if not numbers:
        return {'result': 0}
    return {'result': sum(numbers) / len(numbers)}
