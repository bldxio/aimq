# LangGraph Integration

AIMQ's LangGraph integration provides advanced stateful workflows and agentic systems using a decorator-based architecture built on [LangGraph v1.0](https://langchain-ai.github.io/langgraph/).

## Overview

LangGraph enables building sophisticated multi-step AI workflows with state management, tool execution, conditional routing, and checkpointing. AIMQ wraps LangGraph's powerful graph primitives with a simple decorator pattern optimized for queue-based processing.

### Key Features

- **Decorator Pattern**: Define reusable agents and workflows with `@agent` and `@workflow` decorators
- **Built-in Agents**: Pre-built ReAct and Plan-Execute agents for common patterns
- **Built-in Workflows**: Document processing and multi-agent collaboration workflows
- **LLM Flexibility**: Use any LangChain-compatible LLM (Mistral, OpenAI, Anthropic, etc.)
- **Three-Level Configuration**: Defaults, factory overrides, and job-level overrides with security controls
- **Checkpointing**: Resumable workflows backed by Supabase PostgreSQL
- **Tool Integration**: Seamless integration with LangChain tools and AIMQ's built-in tools
- **Security**: Tool input validation, whitelisted LLM overrides, and controlled prompt injection

## Quick Start

### Installation

LangGraph integration requires additional dependencies:

```bash
# Install LangGraph dependencies
uv add langgraph langgraph-checkpoint-postgres langchain langchain-core

# Install LLM provider (example: Mistral)
uv add langchain-mistralai

# Optional: Additional tools
uv add python-magic pillow easyocr
```

### First Agent

Create a simple agent that answers questions using tools:

```python
# tasks.py
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile, ReadRecord
from aimq.worker import Worker

worker = Worker()

# Configure ReAct agent with tools
agent = ReActAgent(
    tools=[ReadFile(), ReadRecord()],
    system_prompt="You are a helpful assistant that answers questions using available tools.",
    llm="mistral-large-latest",
    memory=True,  # Enable checkpointing
    max_iterations=10
)

# Assign to queue
worker.assign(agent, queue="qa-agent", timeout=300)
```

Start the worker:

```bash
# Start worker
aimq start tasks.py

# Send a job
aimq send qa-agent '{
  "messages": [{"role": "user", "content": "Read the file at reports/summary.txt"}],
  "tools": ["read_file"],
  "iteration": 0,
  "errors": []
}'
```

### First Workflow

Create a multi-step workflow with custom state:

```python
# tasks.py
from typing import NotRequired, TypedDict
from langgraph.graph import END, StateGraph
from aimq.langgraph import workflow
from aimq.worker import Worker

# Define custom state
class MyState(TypedDict):
    input: str
    result: NotRequired[str]

# Define workflow
@workflow(state_class=MyState, checkpointer=True)
def my_workflow(graph: StateGraph, config: dict) -> StateGraph:
    def process(state):
        return {"result": state["input"].upper()}

    graph.add_node("process", process)
    graph.add_edge("process", END)
    graph.set_entry_point("process")

    return graph

worker = Worker()
wf = my_workflow()
worker.assign(wf, queue="my-workflow")
```

## Architecture

### Decorator Pattern

AIMQ's LangGraph integration uses a **decorator factory pattern**:

```python
@agent(tools=[...], llm="mistral-large-latest")
def my_agent(graph: StateGraph, config: dict) -> StateGraph:
    # Add nodes and edges to graph
    return graph

# Usage: Call factory to create instance
agent_instance = my_agent()
worker.assign(agent_instance, queue="my-queue")
```

**How it works:**

1. Decorator returns a **factory function**
2. Factory function creates a configured **runnable instance**
3. Instance is assigned to a queue like any other AIMQ task

This pattern enables:

- **Reusability**: Define once, instantiate with different configs
- **Testability**: Easy to test with different parameters
- **Composability**: Combine agents and workflows

### Three-Level Configuration

Configuration is resolved in three levels with increasing priority:

#### Level 1: Decorator Defaults

Set defaults when defining the agent/workflow:

```python
@agent(
    tools=[ReadFile()],
    system_prompt="You are a helpful assistant",
    llm="mistral-large-latest",
    temperature=0.1,
    memory=True
)
def my_agent(graph: StateGraph, config: dict) -> StateGraph:
    # config contains decorator defaults
    return graph
```

#### Level 2: Factory Overrides

Override when creating instances:

```python
# Create fast variant
fast_agent = my_agent(llm="mistral-small-latest", temperature=0.5)

# Create slow, thorough variant
thorough_agent = my_agent(llm="mistral-large-latest", temperature=0.0)

# Assign different instances
worker.assign(fast_agent, queue="fast-qa")
worker.assign(thorough_agent, queue="thorough-qa")
```

#### Level 3: Job-Level Overrides

Override per-job via message data (requires security whitelisting):

```python
# Configure allowed overrides
@agent(
    llm="mistral-large-latest",
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
    },
    allow_system_prompt=True
)
def my_agent(graph: StateGraph, config: dict) -> StateGraph:
    return graph

# Send job with overrides
aimq send qa-agent '{
  "messages": [...],
  "llm": "small",
  "system_prompt": "Be very concise",
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

**Security Note**: Job-level overrides require explicit whitelisting to prevent prompt injection and unauthorized LLM usage.

## Using Built-in Agents

AIMQ provides two production-ready agents implementing common patterns.

### ReActAgent

**Pattern**: Reasoning + Acting

The ReAct agent iteratively reasons about what to do, executes tools, and observes results until reaching a final answer.

**Use Cases:**

- Question answering with tool access
- Research and information gathering
- Multi-step problem solving
- Document analysis

**Example:**

```python
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile, ReadRecord
from aimq.tools.ocr import ImageOCR

agent = ReActAgent(
    tools=[
        ReadFile(),      # Read files from Supabase storage
        ReadRecord(),    # Query Supabase database
        ImageOCR(),      # Extract text from images
    ],
    system_prompt="""You are a document assistant.
    Use read_file for text files, image_ocr for images,
    and read_record to query databases.
    Provide clear, evidence-based answers.""",
    llm="mistral-large-latest",
    temperature=0.1,
    memory=True,         # Enable conversation history
    max_iterations=10    # Prevent infinite loops
)

worker.assign(agent, queue="doc-qa", timeout=900)
```

**Configuration Options:**

- `tools`: List of LangChain BaseTool objects
- `system_prompt`: Agent instructions and persona
- `llm`: Model name (string) or LangChain LLM object
- `temperature`: LLM temperature (0.0-1.0)
- `memory`: Enable checkpointing for resumable conversations
- `max_iterations`: Maximum reasoning loops

**Job Format:**

```json
{
  "messages": [
    {"role": "user", "content": "What is in the Q1 report?"}
  ],
  "tools": ["read_file", "read_record"],
  "iteration": 0,
  "errors": []
}
```

### PlanExecuteAgent

**Pattern**: Plan then Execute

Creates an execution plan upfront, then executes steps sequentially with optional replanning.

**Use Cases:**

- Complex multi-step tasks
- Structured workflows
- Batch processing
- Tasks requiring upfront planning

**Example:**

```python
from aimq.agents import PlanExecuteAgent
from aimq.tools.supabase import ReadFile, WriteRecord

agent = PlanExecuteAgent(
    tools=[ReadFile(), WriteRecord()],
    system_prompt="""You are a task planner.
    Break down complex tasks into clear steps,
    then execute methodically.""",
    llm="mistral-large-latest",
    temperature=0.2,  # Slight creativity for planning
    memory=True
)

worker.assign(agent, queue="planner", timeout=1200)
```

**Configuration Options:**

Same as ReActAgent, but no `max_iterations` (determined by plan length).

**Job Format:**

```json
{
  "input": "Analyze all Q1 reports and create a summary document",
  "plan": [],
  "current_step": 0,
  "step_results": [],
  "final_output": null,
  "needs_replan": false
}
```

## Using Built-in Workflows

### DocumentWorkflow

**Pattern**: Multi-step document processing pipeline

Processes documents through fetch → detect type → route → extract text → store.

**Features:**

- Automatic document type detection (image, PDF, etc.)
- Conditional routing based on type
- OCR for images
- PDF text extraction
- Metadata extraction and storage

**Example:**

```python
from aimq.workflows import DocumentWorkflow
from aimq.tools.supabase import ReadFile
from aimq.tools.ocr import ImageOCR
from aimq.tools.pdf import PageSplitter

workflow = DocumentWorkflow(
    storage_tool=ReadFile(),
    ocr_tool=ImageOCR(),
    pdf_tool=PageSplitter(),
    checkpointer=True
)

worker.assign(workflow, queue="documents", timeout=600)
```

**Job Format:**

```json
{
  "document_path": "uploads/invoice.pdf",
  "metadata": {},
  "status": "pending"
}
```

**State Flow:**

```
fetch → detect → [image → OCR] or [PDF → extract] → store
```

### MultiAgentWorkflow

**Pattern**: Supervisor-agent collaboration

Coordinates multiple specialized agents with a supervisor for complex tasks.

**Features:**

- Supervisor delegates to specialist agents
- Parallel or sequential execution
- Result aggregation
- Error handling and retries

**Example:**

```python
from aimq.workflows import MultiAgentWorkflow
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile, WriteRecord

# Define specialist agents
researcher = ReActAgent(
    tools=[ReadFile()],
    system_prompt="Research specialist"
)

writer = ReActAgent(
    tools=[WriteRecord()],
    system_prompt="Writing specialist"
)

# Create multi-agent workflow
workflow = MultiAgentWorkflow(
    agents={"researcher": researcher, "writer": writer},
    supervisor_prompt="Delegate tasks to specialists",
    checkpointer=True
)

worker.assign(workflow, queue="multi-agent", timeout=1800)
```

## Creating Custom Agents

Use the `@agent` decorator to build custom agents with full control over graph structure.

### Step-by-Step Guide

**1. Import Dependencies**

```python
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph
from aimq.langgraph import agent
from aimq.tools.supabase import ReadFile, WriteRecord
from aimq.worker import Worker
```

**2. Define Agent with Decorator**

```python
@agent(
    tools=[ReadFile(), WriteRecord()],
    system_prompt="You are a data processor",
    llm="mistral-large-latest",
    temperature=0.2,
    memory=True
)
def data_processor(graph: StateGraph, config: dict) -> StateGraph:
    # config contains: tools, system_prompt, llm, temperature, memory, etc.

    def analyze_node(state):
        # Access config
        llm = config["llm"]
        tools = config["tools"]

        # Process state
        # Return state updates
        return {"messages": [...], "iteration": state["iteration"] + 1}

    # Build graph
    graph.add_node("analyze", analyze_node)
    graph.add_edge("analyze", END)
    graph.set_entry_point("analyze")

    return graph
```

**3. Create and Assign Instance**

```python
worker = Worker()
agent_instance = data_processor()
worker.assign(agent_instance, queue="data-processor", timeout=600)
```

**4. Send Jobs**

```json
{
  "messages": [
    {"role": "user", "content": "Process data/sales.csv"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}
```

### Agent State

Agents use `AgentState` by default:

```python
class AgentState(TypedDict):
    # Required fields
    messages: Annotated[Sequence[BaseMessage], add]
    tools: list[str]
    iteration: int
    errors: Annotated[list[str], add]

    # Optional fields
    current_tool: NotRequired[str]
    tool_input: NotRequired[dict]
    tool_output: NotRequired[Any]
    final_answer: NotRequired[str]
    tenant_id: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]
```

**Custom State:**

```python
from aimq.langgraph.states import AgentState

class MyAgentState(AgentState):
    # Extend with custom fields
    custom_field: NotRequired[str]

@agent(state_class=MyAgentState)
def my_agent(graph: StateGraph, config: dict) -> StateGraph:
    # Use custom state
    return graph
```

## Creating Custom Workflows

Use the `@workflow` decorator for non-agentic multi-step processes.

### Step-by-Step Guide

**1. Define Custom State**

```python
from typing import Annotated, NotRequired, TypedDict
from operator import add

class ETLState(TypedDict):
    # Required fields
    source_path: str
    load_status: str
    errors: Annotated[list[str], add]  # Errors accumulate

    # Optional fields
    extracted_data: NotRequired[dict]
    transformed_data: NotRequired[dict]
    row_count: NotRequired[int]
```

**2. Define Workflow with Decorator**

```python
from langgraph.graph import END, StateGraph
from aimq.langgraph import workflow

@workflow(state_class=ETLState, checkpointer=True)
def etl_pipeline(graph: StateGraph, config: dict) -> StateGraph:

    def extract(state: ETLState) -> ETLState:
        # Read data
        return {"extracted_data": {...}, "row_count": 100}

    def transform(state: ETLState) -> ETLState:
        # Transform data
        return {"transformed_data": {...}}

    def load(state: ETLState) -> ETLState:
        # Store results
        return {"load_status": "success"}

    # Build linear pipeline
    graph.add_node("extract", extract)
    graph.add_node("transform", transform)
    graph.add_node("load", load)

    graph.add_edge("extract", "transform")
    graph.add_edge("transform", "load")
    graph.add_edge("load", END)

    graph.set_entry_point("extract")

    return graph
```

**3. Create and Assign Instance**

```python
worker = Worker()
workflow_instance = etl_pipeline()
worker.assign(workflow_instance, queue="etl", timeout=600)
```

**4. Send Jobs**

```json
{
  "source_path": "data/sales.csv",
  "load_status": "",
  "errors": []
}
```

### Conditional Routing

Add branching logic with conditional edges:

```python
@workflow(state_class=MyState)
def branching_workflow(graph: StateGraph, config: dict) -> StateGraph:

    def decide_route(state) -> str:
        if state.get("condition"):
            return "path_a"
        return "path_b"

    graph.add_node("start", start_node)
    graph.add_node("path_a", path_a_node)
    graph.add_node("path_b", path_b_node)

    graph.add_conditional_edges(
        "start",
        decide_route,
        {"path_a": "path_a", "path_b": "path_b"}
    )

    graph.add_edge("path_a", END)
    graph.add_edge("path_b", END)
    graph.set_entry_point("start")

    return graph
```

## Checkpointing & State Management

### Enabling Checkpointing

Enable persistent state to resume workflows after interruption:

```python
@agent(memory=True)  # For agents
def my_agent(...):
    pass

@workflow(checkpointer=True)  # For workflows
def my_workflow(...):
    pass
```

### Database Schema Setup

Checkpointing requires PostgreSQL tables. Run this SQL in Supabase dashboard:

```sql
-- Create schema
CREATE SCHEMA IF NOT EXISTS langgraph;

-- Checkpoints table
CREATE TABLE IF NOT EXISTS langgraph.checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
    ON langgraph.checkpoints(thread_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_created
    ON langgraph.checkpoints(created_at);
```

Or use the provided SQL file:

```bash
# In Supabase SQL Editor, run:
cat docs/deployment/langgraph-schema.sql
```

### Thread IDs for Resumable Workflows

Use `thread_id` to resume conversations or workflows:

```json
{
  "messages": [
    {"role": "user", "content": "Continue analyzing the document"}
  ],
  "thread_id": "user-123-session-456",
  "tools": [],
  "iteration": 0,
  "errors": []
}
```

**Benefits:**

- Resume interrupted workflows
- Multi-turn conversations with history
- User session continuity
- Debugging and replay

### State Classes

**AgentState** (for agents):

```python
from aimq.langgraph.states import AgentState

# Built-in fields: messages, tools, iteration, errors
# Optional: current_tool, tool_input, final_answer, etc.
```

**WorkflowState** (for workflows):

```python
from aimq.langgraph.states import WorkflowState

# Built-in fields: input, errors
# Optional: current_step, step_results, final_output
```

**Custom States**:

```python
from typing import NotRequired, TypedDict
from operator import add
from typing import Annotated

class MyState(TypedDict):
    required_field: str
    optional_field: NotRequired[str]
    accumulating_list: Annotated[list, add]  # Merges across updates
```

## Security

### Job-Level Override Controls

Prevent unauthorized LLM usage and prompt injection:

```python
@agent(
    llm="mistral-large-latest",
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
    },
    allow_system_prompt=True  # Allow job-level prompt override
)
def my_agent(...):
    pass
```

**Security Rules:**

- **LLM Override**: Only allowed if key exists in `allowed_llms`
- **System Prompt Override**: Only allowed if `allow_system_prompt=True`
- **Validation**: Happens before graph execution
- **Error**: Raises `OverrideSecurityError` on violation

**Example Violation:**

```python
# This will raise OverrideSecurityError
aimq send qa-agent '{
  "llm": "gpt-4",  # Not in allowed_llms
  "messages": [...]
}'
```

### Tool Input Validation

All tool inputs are validated against Pydantic schemas:

```python
from aimq.langgraph.validation import ToolInputValidator

validator = ToolInputValidator()

# Validates against tool.args_schema
validated = validator.validate(tool, input_data)

# Prevents path traversal
validator.validate_file_path("../../etc/passwd")  # Raises

# Detects SQL injection
validator.validate_sql_query("DROP TABLE users")  # Raises
```

**What is Validated:**

- Path traversal attempts (`../`)
- Sensitive file access (`/etc/passwd`, `.env`, `.ssh/`)
- SQL injection patterns (`DROP`, `DELETE`, `EXECUTE`)
- Pydantic schema compliance

**Configuration:**

Validation is automatic for all tools in agents. No configuration needed.

## Configuration Reference

### Environment Variables

```bash
# LLM Configuration
MISTRAL_API_KEY=your_api_key
MISTRAL_MODEL=mistral-large-latest

# Supabase (required for checkpointing)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Optional
LANGGRAPH_CHECKPOINT_ENABLED=true
```

### Config Fields

Access via `from aimq.config import config`:

```python
config.mistral_api_key      # Mistral API key
config.mistral_model        # Default model name
config.supabase_url         # Supabase project URL
config.supabase_key         # Supabase anon key
```

### Decorator Parameters

**@agent:**

- `tools`: List[BaseTool] - Tools available to agent
- `system_prompt`: str - Agent instructions
- `llm`: str | BaseChatModel - LLM model or name
- `temperature`: float - LLM temperature (default: 0.1)
- `memory`: bool - Enable checkpointing (default: False)
- `state_class`: Type[dict] - Custom state class
- `reply_function`: Callable - Custom reply handler
- `allowed_llms`: Dict[str, BaseChatModel] - Whitelisted LLMs
- `allow_system_prompt`: bool - Allow prompt override (default: False)

**@workflow:**

- `state_class`: Type[dict] - Custom state class
- `checkpointer`: bool - Enable persistence (default: False)

## Best Practices

**1. Use Checkpointing for Long Workflows**

Enable `memory=True` or `checkpointer=True` for tasks that:

- Take more than 60 seconds
- Involve multi-turn conversations
- May need to resume after interruption
- Require debugging and replay

**2. Set Max Iterations**

Prevent infinite loops in agents:

```python
agent = ReActAgent(
    max_iterations=10,  # Stop after 10 reasoning cycles
    ...
)
```

**3. Validate Tool Inputs**

Always use Pydantic schemas for tools:

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    path: str = Field(..., description="File path")

class MyTool(BaseTool):
    name = "my_tool"
    args_schema = MyToolInput  # Enables validation
```

**4. Use Logger for Debugging**

AIMQ's logger is integrated throughout:

```python
import logging
logger = logging.getLogger(__name__)

def my_node(state):
    logger.info("Processing step X")
    logger.debug(f"State: {state}")
    return {...}
```

**5. Test Locally Before Deploying**

Test agents and workflows with simple jobs:

```python
if __name__ == "__main__":
    # Test mode: process one job then exit
    worker.start()
```

**6. Handle Errors Gracefully**

Collect errors in state:

```python
def my_node(state):
    try:
        result = risky_operation()
        return {"result": result}
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return {"errors": [str(e)]}
```

**7. Use Appropriate LLM Models**

- `mistral-small-latest`: Fast, simple tasks
- `mistral-large-latest`: Complex reasoning, tool use
- `mistral-medium-latest`: Balance of speed and capability

**8. Secure Job-Level Overrides**

Only whitelist necessary LLM variants:

```python
@agent(
    allowed_llms={
        "fast": ChatMistralAI(model="mistral-small-latest"),
        # Don't expose expensive models if not needed
    },
    allow_system_prompt=False  # Prevent prompt injection
)
```

## Troubleshooting

### Checkpointer Connection Fails

**Error**: `CheckpointerError: SUPABASE_URL required`

**Solution**: Set environment variables:

```bash
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your_anon_key
```

### Schema Not Initialized

**Error**: `relation "langgraph.checkpoints" does not exist`

**Solution**: Run schema SQL in Supabase dashboard (see [Database Schema Setup](#database-schema-setup))

### LLM Resolution Fails

**Error**: `LLMResolutionError: langchain-mistralai is required`

**Solution**: Install LLM provider:

```bash
uv add langchain-mistralai
```

### Tool Validation Fails

**Error**: `ToolValidationError: Invalid input for tool 'read_file'`

**Solution**: Ensure job data matches tool schema:

```python
# Correct
{"path": "documents/file.txt"}

# Incorrect
{"file": "documents/file.txt"}  # Wrong field name
```

### Infinite Loop in Agent

**Error**: Agent runs forever without reaching final answer

**Solution**: Set `max_iterations`:

```python
agent = ReActAgent(
    max_iterations=10,  # Stop after 10 loops
    ...
)
```

### Job Override Rejected

**Error**: `OverrideSecurityError: LLM key 'gpt-4' not in allowed_llms`

**Solution**: Add to whitelist or use allowed key:

```python
@agent(
    allowed_llms={
        "gpt4": ChatOpenAI(model="gpt-4"),  # Whitelist GPT-4
    }
)
```

### Thread ID Not Resuming

**Problem**: Sending `thread_id` but workflow starts fresh

**Solution**: Ensure checkpointing is enabled:

```python
@agent(memory=True)  # Must be True
```

## Next Steps

- **[Agents Guide](./agents.md)**: Deep dive into agent patterns and customization
- **[Workflows Guide](./workflows.md)**: Advanced workflow patterns and composition
- **[API Reference](../api/langgraph.md)**: Complete API documentation with type signatures
- **Examples**: Check `examples/langgraph/` for working code

## Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/integrations/tools)
- [AIMQ Examples](https://github.com/bldxio/aimq/tree/main/examples/langgraph)
