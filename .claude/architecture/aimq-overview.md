# AIMQ Architecture Overview

## What is AIMQ?

**AIMQ (AI Message Queue)** is a message queue processor for Supabase's pgmq integration with built-in AI-powered document processing, agent orchestration, and workflow management capabilities.

## Core Concepts

### Message Queue Processing
- **Worker**: Orchestrates multiple queues and worker threads
- **Queue**: Wraps LangChain Runnables with queue-specific configuration
- **Job**: Represents a single message from pgmq
- **Provider**: Abstract interface for queue operations (pgmq via Supabase RPC)

### AI Capabilities
- **Agents**: Autonomous AI agents (ReAct, Plan-Execute) that can use tools
- **Workflows**: Multi-step LangGraph workflows for complex processing
- **Tools**: LangChain-compatible tools (OCR, PDF processing, Supabase operations)
- **Memory**: Checkpoint and memory management for stateful agents

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Language** | Python 3.11-3.13 |
| **Package Manager** | uv (NOT pip/poetry) |
| **AI Framework** | LangChain, LangGraph |
| **Queue** | Supabase pgmq (PostgreSQL Message Queue) |
| **Database** | Supabase (PostgreSQL + Storage) |
| **OCR** | EasyOCR, PyTorch |
| **CLI** | Typer, Rich |
| **Testing** | pytest, pytest-cov |
| **Automation** | just (task runner) |

## Module Architecture

```
src/aimq/
├── agents/          # Agent implementations (ReAct, Plan-Execute)
│   ├── base.py      # Base agent classes
│   ├── react.py     # ReAct agent (Reasoning + Acting)
│   ├── plan_execute.py  # Plan-Execute agent
│   ├── decorators.py    # Agent-specific decorators
│   ├── states.py    # Agent state models
│   └── validation.py    # Agent validation logic
│
├── workflows/       # Workflow implementations
│   ├── base.py      # Base workflow classes
│   ├── multi_agent.py   # Multi-agent collaboration
│   ├── document.py  # Document processing pipeline
│   ├── decorators.py    # Workflow-specific decorators
│   └── states.py    # Workflow state models
│
├── common/          # Shared utilities
│   ├── llm.py       # LLM initialization and configuration
│   └── exceptions.py    # Custom exception classes
│
├── memory/          # Memory and checkpoint management
│   └── checkpoint.py    # Checkpoint managers for stateful agents
│
├── clients/         # External service clients
│   ├── supabase.py  # Supabase client (singleton)
│   └── mistral.py   # Mistral AI client
│
├── providers/       # Queue provider implementations
│   ├── base.py      # Abstract QueueProvider interface
│   └── supabase.py  # SupabaseQueueProvider (pgmq via RPC)
│
├── tools/           # LangChain tools
│   ├── ocr/         # OCR tools (ImageOCR)
│   ├── pdf/         # PDF tools (PageSplitter)
│   ├── supabase/    # Supabase tools (ReadRecord, WriteRecord, etc.)
│   └── mistral/     # Mistral AI tools
│
├── commands/        # CLI commands
│   ├── worker.py    # Worker management (start, stop)
│   ├── queue.py     # Queue operations (send, read)
│   └── init.py      # Project initialization
│
├── worker.py        # Main Worker orchestrator
├── queue.py         # Queue wrapper for Runnables
├── job.py           # Job representation
├── config.py        # Configuration (Pydantic Settings)
├── attachment.py    # Binary data wrapper
├── logger.py        # Logging configuration
├── motd.py          # Message of the Day system
└── utils.py         # Utility functions
```

## Data Flow

### 1. Message Processing Flow
```
Supabase pgmq
    ↓
Worker polls queue
    ↓
Queue reads/pops message → Job
    ↓
Queue invokes Runnable with job.data
    ↓
Runnable processes (agent/workflow/custom)
    ↓
On success: archive or delete
On error: message stays in queue (retry)
```

### 2. Agent Execution Flow
```
Job data → Agent
    ↓
Agent analyzes input
    ↓
Agent selects tool(s)
    ↓
Tool executes (OCR, PDF, Supabase, etc.)
    ↓
Agent processes tool output
    ↓
Agent returns result
    ↓
Result archived/deleted in queue
```

### 3. Workflow Execution Flow
```
Job data → Workflow
    ↓
Workflow state initialized
    ↓
Step 1: Process input
    ↓
Step 2: Execute sub-tasks
    ↓
Step 3: Aggregate results
    ↓
Workflow returns final state
    ↓
Result archived/deleted in queue
```

## Key Design Patterns

### 1. Decorator Pattern
Tasks are registered using decorators:
```python
from aimq.worker import Worker

worker = Worker()

@worker.task(queue="my-queue", timeout=300)
def process_job(data: dict) -> dict:
    return {"status": "success"}
```

### 2. Singleton Pattern
Configuration and clients are singletons:
```python
from aimq.config import config  # Singleton instance
from aimq.clients.supabase import get_supabase_client  # Singleton
```

### 3. Provider Pattern
Queue operations abstracted behind provider interface:
```python
class QueueProvider(ABC):
    @abstractmethod
    def send(self, queue: str, data: dict) -> int:
        pass

    @abstractmethod
    def read(self, queue: str, vt: int) -> list[Job]:
        pass
```

### 4. Runnable Pattern
All tasks are LangChain Runnables:
```python
from langchain.schema.runnable import Runnable

class Queue:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def process(self, job: Job):
        return self.runnable.invoke(job.data)
```

## Configuration

Configuration uses Pydantic Settings with `.env` file:

```python
# .env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
OPENAI_API_KEY=xxx

# Access in code
from aimq.config import config

print(config.supabase_url)
print(config.openai_api_key)
```

## Deployment

### Local Development
```bash
# Install dependencies
just install

# Run worker
aimq worker start tasks.py
```

### Docker
```bash
# Build image
docker build -t aimq .

# Run with local tasks
docker run -v ./tasks.py:/app/tasks.py aimq

# Run with git URL
docker run -e AIMQ_TASKS=git:user/repo aimq
```

### Production
- Deploy to any container platform (Fly.io, Railway, etc.)
- Use environment variables for configuration
- Load tasks from git repositories
- Monitor with LangSmith (optional)

## Related

- See `patterns/module-organization.md` for module structure details
- See `architecture/langchain-integration.md` for LangChain details
- See `architecture/langgraph-integration.md` for LangGraph details
- See `CLAUDE.md` for comprehensive technical documentation
