# Overview

AIMQ (pronounced "aim-q") is an Agentic Infrastructure Message Queue system that
provides a powerful framework for building AI-powered workflows using message queues.
While currently focused on Supabase queues, its architecture is designed to support any
PGMQ-based queue system.

## Core Components

### Library

The AIMQ library enables you to:

- Define workers and their associated tasks
- Create queue-aligned tasks that return LangChain runnables
- Integrate with built-in and custom LangChain tools
- Leverage built-in Supabase tools for:
  - Queue management (enqueue, dequeue)
  - Database operations (read/write records)
  - Storage operations (read/write files)
  - Real-time updates for UI synchronization

### CLI Tool

The `aimq` command-line interface provides several essential commands:

- `aimq init .` - Set up a new AIMQ project
- `aimq start tasks.py` - Run tasks defined in your tasks file
- `aimq new` - Generate Supabase migrations for:
  - Queue setup
  - Hook configuration
  - Other infrastructure needs

## Key Features

### Worker-Queue Pattern

- Workers manage the processing of jobs across multiple queues
- Each task is associated with a specific queue
- Tasks return LangChain runnables for flexible AI workflow integration

### Built-in Tools

1. **Queue Management**

   - Enqueue new jobs
   - Create multi-step workflows
   - Handle job delays and timeouts

1. **Supabase Integration**

   - Database record operations
   - File storage management
   - Real-time updates
   - Queue infrastructure

### Real-time Updates

- Workers can insert or update records
- UI components can subscribe to changes
- Immediate feedback for end-users

## Getting Started

### Installation

1. Install the CLI tool (recommended):

   ```bash
   pipx install aimq
   ```

1. Install the library for your project:

   ```bash
   pip install aimq
   ```

### Using the CLI

1. Initialize a new project:

   ```bash
   aimq init .
   ```

1. Define your tasks in `tasks.py`:

   ```python
   from aimq import Worker

   worker = Worker()

   @worker.task(queue="process_documents")
   def process_documents():
       # Return a LangChain runnable
       return document_processing_chain
   ```

1. Start your worker with the CLI:

   ```bash
   aimq start tasks.py
   ```

### Using the Library

You can use AIMQ as a library without the CLI. Here's a basic example:

```python
from aimq import Worker

# Create a worker instance
worker = Worker()

@worker.task(
    queue="text_stats",  # Custom queue name
    timeout=10,  # Maximum execution time in seconds
    delete_on_finish=True,  # Remove completed tasks
)
def text_statistics(data: dict) -> dict:
    """Calculate text statistics."""
    text = data.get("text", "")
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "avg_word_length": len(text) / len(words) if words else 0
    }

if __name__ == "__main__":
    # Start the worker directly
    worker.start()
```

## Next Steps

- Learn about [Task Definition](architecture.md)
- Explore [Queue Configuration](architecture.md)
- Understand [Supabase Integration](supabase-setup.md)
