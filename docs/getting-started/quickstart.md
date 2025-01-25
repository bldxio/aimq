# AIMQ Quick Start

## Installation

```bash
# Install with poetry
poetry add aimq

# Or install globally
pipx install aimq
```

## CLI Setup

1. Create `.env` file:

```bash
cp .env.example .env
# Edit with your Supabase credentials
```

1. Basic commands:

```bash
# Start worker process
aimq worker --file worker.py

# Send job to queue
aimq send my_queue '{"key": "value"}'

# Monitor queues
aimq queues list
```

## Supabase Setup

1. Enable pgmq in Supabase:

```sql
-- Run in SQL Editor
create extension if not exists pgmq;
select pgmq_create('my_queue');
```

1. Required permissions:

```sql
grant usage on schema pgmq to postgres;
grant all privileges on all tables in schema pgmq to postgres;
```

## Defining Tasks

### Basic Task Structure

```python
# worker.py
from aimq import Worker
from langchain_core.runnables import RunnableLambda

worker = Worker()

@worker.task(queue="doc_processing")
def process_docs(data: dict) -> dict:
    '''Process document with AI chain'''
    return {"status": "processed", **data}
```

### Using Helpers

```python
from aimq.helpers import (
    echo,
    select,
    assign,
    orig,
    const
)

chain = (
    select(["document", "metadata"])
    | assign({
        "text": RunnableLambda(extract_text),
        "summary": summarizer_chain,
        "source": orig("queue")
    })
    | echo
)
```

## Key Tools

### CLI Tools

```bash
aimq worker --help  # Show worker options
aimq send <queue> <json>  # Send single job
aimq send-batch <queue> <file.json>  # Send batch jobs
aimq queues list  # List available queues
```

### Helper Functions

| Helper     | Description                          |
|------------|--------------------------------------|
| `echo`     | Print & pass through data            |
| `select`   | Choose specific data fields          |
| `assign`   | Create new data fields               |
| `orig`     | Access original job metadata         |
| `const`    | Create constant values in chains     |

## Example Workflow

1. Create PDF processing chain:

```python
# worker.py
from aimq import Worker, helpers as h

worker = Worker()

@worker.task(queue="pdf_queue")
def pdf_chain(data: dict) -> dict:
    return (
        h.select("pdf_path")
        | h.assign({
            "text": PDFTextExtractor(),
            "pages": h.const(1)
        })
        | h.echo
    )
```

1. Process jobs:

```bash
aimq worker --file worker.py
aimq send pdf_queue '{"pdf_path": "doc.pdf"}'
