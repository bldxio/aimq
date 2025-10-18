# Quick Start Guide

This guide will help you get started with AIMQ (AI Message Queue) in minutes.

## Zero-Installation Quick Start

The fastest way to try AIMQ requires no installation:

```bash
# Initialize a new project
uvx aimq init my-aimq-project
cd my-aimq-project

# Configure Supabase credentials
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY

# Start the worker
uvx aimq start
```

That's it! The worker is now running and will process jobs from your queues.

## Prerequisites

1. **Supabase Project** with pgmq extension enabled:
   - Go to Database → Extensions
   - Enable the `pgmq` extension

2. **Supabase Credentials**:
   - `SUPABASE_URL`: Your project URL (e.g., `https://xxx.supabase.co`)
   - `SUPABASE_KEY`: Your service role key or anon key

## Environment Setup

The `aimq init` command creates a `.env.example` file. Copy and configure it:

```bash
# Copy the example
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional
WORKER_NAME=my-worker
WORKER_LOG_LEVEL=info
WORKER_IDLE_WAIT=10.0
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

```bash
# Using uvx (no installation)
uvx aimq start

# Or if you installed with uv tool install
aimq start

# With debug logging
aimq start --debug

# With specific worker file
aimq start my_tasks.py
```

You can also run the file directly:
```bash
python tasks.py
# or
uv run python tasks.py
```

3. Send jobs to your queues:

**Using the CLI** (recommended for testing):
```bash
# Send a message to a queue
aimq send hello_world '{"name": "Alice"}'

# Or with uvx
uvx aimq send hello_world '{"name": "Alice"}'
```

**Programmatically from Python**:
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

**Or directly via Supabase**:
```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Send a message using pgmq
supabase.rpc("pgmq_send", {
    "queue_name": "hello_world",
    "msg": {"name": "Alice"}
}).execute()
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

## Docker Deployment

AIMQ can be deployed using Docker with two approaches:

### Local Development
```bash
# Generate Docker files
aimq init --docker

# Start with docker-compose
docker-compose up -d
```

### Production with Git URLs
```bash
# Load tasks from a git repository
docker run --rm \
  -e AIMQ_TASKS=git:mycompany/aimq-tasks@production \
  -e SUPABASE_URL=https://xxx.supabase.co \
  -e SUPABASE_KEY=your-key \
  aimq:latest
```

Git URL patterns supported:
- `git:user/repo` - Default branch
- `git:user/repo@branch` - Specific branch or tag
- `git:user/repo#path/to/tasks` - Subdirectory in monorepo

For more details, see [Docker & Kubernetes Deployment](../deployment/docker-kubernetes.md).

## Queue Management

Enable or disable queues dynamically:

```bash
# Enable a queue
aimq enable my-queue

# Disable a queue
aimq disable my-queue
```

## Next Steps

- Learn more about [configuration options](configuration.md)
- See [Docker deployment patterns](../deployment/docker-kubernetes.md)
- Explore the [API Reference](../api/overview.md)
- Read about [OCR capabilities](../user-guide/ocr.md)
