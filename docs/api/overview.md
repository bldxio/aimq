# API Reference

This section provides detailed documentation for AIMQ's API.

## Core Components

### Worker

The [`Worker`](../reference/aimq/worker.md) class is the main entry point for AIMQ. It manages queues and processes jobs:

```python
from aimq import Worker

worker = Worker()

@worker.task(queue="my_queue")
def process_data(data):
    # Process data here
    return {"status": "processed"}
```

### Queue

The [`Queue`](../reference/aimq/queue.md) class handles message queue operations:

```python
from aimq import Queue

queue = Queue("my_queue")
queue.send({"data": "to process"})
```

### Job

The [`Job`](../reference/aimq/job.md) class represents a unit of work:

```python
from aimq import Job

# Jobs are usually created from queue messages
job = Job.from_response(response_data)
print(f"Processing job {job.id}")
```

## Tools

AIMQ provides several built-in tools for document processing:

### OCR Tools

- Image OCR: Extract text from images
- PDF Processor: Process PDF documents

### Storage Tools

#### Supabase Storage
- Read and write files to Supabase Storage
- Manage file metadata and access control

#### Supabase Database
- Read and write records to Supabase Database
- Manage database records and relationships

## Error Handling

AIMQ provides several exception classes for error handling:

```python
from aimq.exceptions import QueueError, ProcessingError

try:
    result = queue.work()
except QueueError as e:
    print(f"Queue error: {e}")
except ProcessingError as e:
    print(f"Processing error: {e}")
