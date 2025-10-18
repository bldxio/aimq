# Quick Start Guide

This guide will help you get started with AIMQ (AI Message Queue) quickly.

## Prerequisites

1. A Supabase project with Queue integration enabled
2. "Expose Queues via PostgREST" setting turned on
3. At least one queue created in your Supabase project

## Environment Setup

Configure your environment variables:

```env
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-service-role-key
WORKER_NAME=my-worker  # Optional, defaults to 'peon'
```

## Using Workers (Recommended)

The Worker class provides a convenient way to define and manage queue processors using decorators.

1. Create a `tasks.py` file to define your queue processors:

```python
"""
Example tasks.py file demonstrating queue processors using AIMQ.
"""
from aimq import Worker
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

# Initialize the worker
worker = Worker()

# Define a simple task
@worker.task(queue="hello_world")
def hello_world(data):
    """Simple task that returns a greeting message."""
    return {"message": f"Hello {data.get('name', 'World')}!"}

# Define a LangChain-powered task
@worker.task(queue="ai_processor", timeout=300)
def process_with_ai(data):
    """Process text using LangChain."""
    # Create a LangChain runnable
    prompt = ChatPromptTemplate.from_template("Summarize this text: {text}")
    model = ChatOpenAI()
    chain = prompt | model

    # Process the input
    return chain.with_config({"text": data.get("text", "")})

if __name__ == "__main__":
    # This allows the file to be run directly with: python tasks.py
    worker.start()
```

2. Run your worker:

Option 1: Using the `aimq start` command:
```bash
# Run tasks.py with default settings
aimq start tasks.py

# Run with debug logging
aimq start tasks.py --debug

# Run with specific log level
aimq start tasks.py --log-level debug
```

Option 2: Running the file directly:
```bash
# Run tasks.py directly
python tasks.py
```

3. Send jobs to your queues:

```python
from aimq import Worker

# Create a worker instance (make sure tasks are defined first)
worker = Worker()

# Send a job to the hello_world queue
worker.send("hello_world", {"name": "Alice"})

# Send a job to the ai_processor queue
worker.send("ai_processor", {
    "text": "LangChain is a framework for developing applications powered by language models."
})
```

## Using Queues Directly

You can also use the Queue class directly if you want more control or don't need the Worker abstraction.

```python
from aimq.queue import Queue
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda

# Create a processor function
def process_text(data):
    prompt = ChatPromptTemplate.from_template("Summarize this text: {text}")
    model = ChatOpenAI()
    chain = prompt | model
    result = chain.invoke({"text": data.get("text", "")})
    return {"summary": result.content}

# Create a queue with a runnable
queue = Queue(
    runnable=RunnableLambda(process_text, name="text_processor"),
    timeout=300,
    delete_on_finish=True,
    tags=["ai", "text"]
)

# Send a job to the queue
job_id = queue.send({
    "text": "LangChain is a framework for developing applications powered by language models."
})

# Process a single job
result = queue.work()
```

## Advanced Features

### Delayed Jobs

```python
# Using Worker
worker.send("hello_world", {"name": "Bob"}, delay=60)

# Using Queue directly
queue.send({"text": "Process this later"}, delay=60)
```

### Task Configuration

```python
@worker.task(
    queue="important_task",
    timeout=600,  # 10 minute timeout
    delete_on_finish=True,  # Delete instead of archive completed jobs
    tags=["production", "high-priority"]  # Add metadata tags
)
def process_important_task(data):
    # Process important task
    return {"status": "completed"}
```

## Next Steps

- Learn more about [configuration options](configuration.md)
- Explore the [API Reference](../api/overview.md)
