# Key Libraries Reference

## Overview

Quick reference for the main libraries and frameworks used in AIMQ.

## Core Dependencies

### LangChain
**Purpose**: AI application framework, provides Runnable interface and tools

**Key Concepts**:
- `Runnable`: Base interface for all LangChain components
- `RunnableLambda`: Wraps Python functions as Runnables
- `BaseTool`: Base class for tools that agents can use
- `RunnableConfig`: Configuration passed to Runnables (metadata, callbacks)

**Usage in AIMQ**:
```python
from langchain.schema.runnable import Runnable, RunnableLambda
from langchain.tools import BaseTool

# Tasks are Runnables
task = RunnableLambda(lambda data: {"status": "success"})

# Tools inherit from BaseTool
class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"

    def _run(self, input: str) -> str:
        return "result"
```

**Docs**: https://python.langchain.com/

### LangGraph
**Purpose**: Build stateful, multi-actor applications with LLMs

**Key Concepts**:
- `StateGraph`: Graph-based workflow with state management
- `MessagesState`: Built-in state for message-based workflows
- `Checkpointer`: Persistence for workflow state
- `CompiledGraph`: Executable workflow

**Usage in AIMQ**:
```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

# Define workflow
workflow = StateGraph(MessagesState)
workflow.add_node("agent", agent_node)
workflow.add_edge("agent", END)

# Compile with checkpointing
app = workflow.compile(checkpointer=MemorySaver())
```

**Docs**: https://langchain-ai.github.io/langgraph/

### Supabase
**Purpose**: PostgreSQL database, storage, and pgmq integration

**Key Concepts**:
- `Client`: Main Supabase client
- `rpc()`: Call PostgreSQL functions (used for pgmq)
- `storage`: File storage API
- `table()`: Database table operations

**Usage in AIMQ**:
```python
from supabase import create_client

client = create_client(url, key)

# pgmq operations via RPC
result = client.rpc('pgmq_send', {
    'queue_name': 'my-queue',
    'msg': {'data': 'value'}
}).execute()

# Storage operations
client.storage.from_('bucket').upload('path', file)

# Database operations
client.table('jobs').select('*').execute()
```

**Docs**: https://supabase.com/docs/reference/python/

### Pydantic
**Purpose**: Data validation and settings management

**Key Concepts**:
- `BaseModel`: Data validation models
- `BaseSettings`: Environment-based configuration
- `Field`: Field definitions with validation
- Type hints for automatic validation

**Usage in AIMQ**:
```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Configuration
class Config(BaseSettings):
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_key: str = Field(alias="SUPABASE_KEY")

    class Config:
        env_file = ".env"

# Data models
class JobData(BaseModel):
    task: str
    priority: int = 1
```

**Docs**: https://docs.pydantic.dev/

### Typer
**Purpose**: CLI framework with type hints

**Key Concepts**:
- `Typer()`: CLI application
- Type hints for automatic argument parsing
- Rich integration for pretty output
- Command groups and subcommands

**Usage in AIMQ**:
```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def start(
    tasks_path: str = typer.Argument(..., help="Path to tasks file"),
    workers: int = typer.Option(1, help="Number of workers")
):
    console.print(f"Starting {workers} workers...")
```

**Docs**: https://typer.tiangolo.com/

## Testing Dependencies

### pytest
**Purpose**: Testing framework

**Key Features**:
- Simple test discovery (`test_*.py`)
- Fixtures for setup/teardown
- Parametrized tests
- Plugin ecosystem

**Usage**:
```python
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_something(sample_data):
    assert sample_data["key"] == "value"

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
])
def test_double(input, expected):
    assert input * 2 == expected
```

**Docs**: https://docs.pytest.org/

### pytest-cov
**Purpose**: Coverage reporting for pytest

**Usage**:
```bash
pytest --cov=src/aimq --cov-report=html
```

**Docs**: https://pytest-cov.readthedocs.io/

## Development Tools

### uv
**Purpose**: Fast Python package manager (replaces pip/poetry)

**Key Commands**:
```bash
# Install dependencies
uv sync

# Add dependency
uv add package-name

# Add dev dependency
uv add --group dev package-name

# Run command
uv run pytest

# Update dependencies
uv lock --upgrade
```

**Docs**: https://github.com/astral-sh/uv

### black
**Purpose**: Code formatter

**Usage**:
```bash
black src/aimq tests
```

**Config**: `pyproject.toml` → `[tool.black]`

**Docs**: https://black.readthedocs.io/

### flake8
**Purpose**: Linter (style checker)

**Usage**:
```bash
flake8 src/aimq tests
```

**Config**: `.flake8`

**Docs**: https://flake8.pycqa.org/

### mypy
**Purpose**: Static type checker

**Usage**:
```bash
mypy src/aimq tests
```

**Config**: `pyproject.toml` → `[tool.pyright]`

**Docs**: https://mypy.readthedocs.io/

### just
**Purpose**: Task runner (like make but better)

**Usage**:
```bash
just test
just lint
just format
just ci
```

**Config**: `justfile`

**Docs**: https://just.systems/

## AI/ML Dependencies

### EasyOCR
**Purpose**: OCR (Optical Character Recognition)

**Usage in AIMQ**:
```python
import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext(image_path)
```

**Docs**: https://github.com/JaidedAI/EasyOCR

### PyTorch
**Purpose**: Deep learning framework (required by EasyOCR)

**Note**: Large dependency, consider optional installation

**Docs**: https://pytorch.org/

## Version Requirements

From `pyproject.toml`:
```toml
requires-python = ">=3.11,<=3.13"

dependencies = [
    "langchain>=0.3.0",
    "langgraph>=0.2.0",
    "supabase>=2.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "typer>=0.12.0",
    "rich>=13.0.0",
    # ... more
]
```

## Related

- [@aimq-overview.md](./aimq-overview.md) - How these libraries fit together
- [@langchain-integration.md](./langchain-integration.md) - LangChain integration details
- [@langgraph-integration.md](./langgraph-integration.md) - LangGraph workflow patterns
- [@../quick-references/dependency-management.md](../quick-references/dependency-management.md) - Dependency management
