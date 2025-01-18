# Queue Processing

This guide explains how to work with AIMQ's queue processing system.

## Queue Basics

### Creating a Queue and Task

```python
from aimq import Worker

worker = Worker()

@worker.task(queue="documents")
def process_document(data):
    # Process document based on type
    if data.get("process_type") == "ocr":
        return process_ocr(data)
    elif data.get("process_type") == "pdf":
        return process_pdf(data)
```

### Sending Jobs to a Queue

```python
# Send a job directly
worker.send("documents", {
    "file_id": "123",
    "process_type": "ocr"
})

# Or using the queue directly
queue = worker.queues["documents"]
queue.send({
    "file_id": "456",
    "process_type": "pdf"
})
```

## Processing Jobs

### Basic Job Processing

```python
@worker.processor("documents")
async def process_document(job):
    # Access job data
    file_id = job.data["file_id"]
    process_type = job.data["process_type"]
    
    # Process based on type
    if process_type == "ocr":
        return await process_ocr(file_id)
    elif process_type == "pdf":
        return await process_pdf(file_id)
```

### Error Handling

```python
@worker.processor("documents")
async def process_document(job):
    try:
        result = await process_file(job.data)
        return {"status": "success", "result": result}
    except Exception as e:
        # Job will be retried
        raise ProcessingError(f"Failed to process: {str(e)}")
```

## Advanced Features

### Job Priority

```python
# Send high priority job
queue.send(data, priority=1)

# Send low priority job
queue.send(data, priority=10)
```

### Delayed Processing

```python
# Process after 1 hour
queue.send(data, delay=3600)
```

### Batch Processing

```python
@worker.processor("documents")
async def process_documents(jobs):
    results = []
    for job in jobs:
        result = await process_document(job)
        results.append(result)
    return results

# Enable batch processing
worker.enable_batch_processing("documents", batch_size=10)
```

## Monitoring

### Job Status

```python
# Check job status
job = queue.get_job(job_id)
print(f"Job {job.id} status: {job.status}")

# Get queue stats
stats = queue.get_stats()
print(f"Pending jobs: {stats.pending}")
print(f"Processing jobs: {stats.processing}")
```

### Logging

```python
# Enable debug logging
worker.set_log_level("DEBUG")

# Print logs
worker.print_logs()
