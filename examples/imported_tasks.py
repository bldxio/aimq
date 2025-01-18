"""
Example demonstrating loading multiple workflows from a subdirectory.
This module shows how to:
1. Import task modules from different files
2. Assign tasks to workers with custom queues
3. Set up a worker to handle multiple task types
"""

from aimq.worker import Worker
from .tasks import text_tasks, math_tasks

# Initialize the worker that will process the tasks
worker = Worker()

# Assign text processing tasks to default queues
# These tasks will use their function names as queue names
worker.assign(text_tasks.uppercase_text)
worker.assign(text_tasks.text_statistics)

# Assign math processing tasks to custom queues
# Using separate queues allows for better task organization and processing control
worker.assign(math_tasks.calculate_sum, queue="sum_math")
worker.assign(math_tasks.calculate_average, queue="average_math")

if __name__ == "__main__":
    # Start the worker to begin processing tasks from all assigned queues
    worker.start()
