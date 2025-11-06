# LangGraph API Reference

Complete API documentation for AIMQ's LangGraph integration.

## Decorators

### @workflow

Decorator for defining reusable LangGraph workflows.

```python
def workflow(
    state_class: type[dict] | None = None,
    checkpointer: bool = False,
) -> Callable
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `state_class` | `type[dict] \| None` | `None` | Custom state class (must be TypedDict) |
| `checkpointer` | `bool` | `False` | Enable state persistence via PostgreSQL |

**Returns:**

`Callable` - Decorator function that wraps the workflow builder

**Raises:**

- `TypeError`: If state_class is not a dict subclass
- `GraphBuildError`: If workflow builder returns invalid graph
- `GraphCompileError`: If graph compilation fails

**Example:**

```python
from typing import NotRequired, TypedDict
from langgraph.graph import END, StateGraph
from aimq.langgraph import workflow

class MyState(TypedDict):
    input: str
    output: NotRequired[str]

@workflow(state_class=MyState, checkpointer=True)
def my_workflow(graph: StateGraph, config: dict) -> StateGraph:
    """
    Custom workflow builder.

    Args:
        graph: Pre-initialized StateGraph with state_class
        config: Configuration dict with state_class and checkpointer

    Returns:
        Configured StateGraph
    """
    def process(state):
        return {"output": state["input"].upper()}

    graph.add_node("process", process)
    graph.add_edge("process", END)
    graph.set_entry_point("process")

    return graph

# Create instance
workflow_instance = my_workflow()

# Use with worker
from aimq.worker import Worker
worker = Worker()
worker.assign(workflow_instance, queue="my-queue")
```

**Configuration Access:**

The `config` dict passed to the builder contains:

```python
{
    "state_class": MyState,      # Your state class
    "checkpointer": True,        # Checkpointer enabled
    # ... any factory overrides
}
```

---

### @agent

Decorator for defining reusable LangGraph agents.

```python
def agent(
    tools: list[BaseTool] | None = None,
    system_prompt: str | None = None,
    llm: BaseChatModel | str | None = None,
    temperature: float = 0.1,
    memory: bool = False,
    state_class: type[dict] | None = None,
    reply_function: Callable[[str, dict], None] | None = None,
    allowed_llms: dict[str, BaseChatModel] | None = None,
    allow_system_prompt: bool = False,
) -> Callable
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tools` | `list[BaseTool] \| None` | `None` | LangChain tools available to agent |
| `system_prompt` | `str \| None` | `None` | Agent instructions/persona |
| `llm` | `BaseChatModel \| str \| None` | `None` | LLM instance, model name, or None for default |
| `temperature` | `float` | `0.1` | LLM temperature (0.0-1.0) |
| `memory` | `bool` | `False` | Enable conversation memory and checkpointing |
| `state_class` | `type[dict] \| None` | `None` | Custom state class (must extend AgentState) |
| `reply_function` | `Callable \| None` | `None` | Custom callback for sending responses |
| `allowed_llms` | `dict[str, BaseChatModel] \| None` | `None` | Whitelisted LLMs for job-level overrides |
| `allow_system_prompt` | `bool` | `False` | Allow job data to override system_prompt |

**Returns:**

`Callable` - Decorator function that wraps the agent builder

**Raises:**

- `TypeError`: If state_class is not a dict subclass or doesn't extend AgentState
- `LLMResolutionError`: If LLM parameter is invalid
- `GraphBuildError`: If agent builder returns invalid graph
- `GraphCompileError`: If graph compilation fails

**Example:**

```python
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, StateGraph
from aimq.langgraph import agent
from aimq.tools.supabase import ReadFile

@agent(
    tools=[ReadFile()],
    system_prompt="You are a helpful assistant",
    llm="mistral-large-latest",
    temperature=0.1,
    memory=True,
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
    },
    allow_system_prompt=True
)
def my_agent(graph: StateGraph, config: dict) -> StateGraph:
    """
    Custom agent builder.

    Args:
        graph: Pre-initialized StateGraph with AgentState
        config: Configuration dict with tools, llm, etc.

    Returns:
        Configured StateGraph
    """
    def reasoning_node(state):
        llm = config["llm"]
        tools = config["tools"]
        # Process...
        return {"messages": [...]}

    graph.add_node("reason", reasoning_node)
    graph.add_edge("reason", END)
    graph.set_entry_point("reason")

    return graph

# Create instance
agent_instance = my_agent()

# Create with overrides
fast_agent = my_agent(llm="mistral-small-latest", temperature=0.5)

# Use with worker
worker.assign(agent_instance, queue="agent-queue")
```

**Configuration Access:**

The `config` dict passed to the builder contains:

```python
{
    "tools": [ReadFile()],
    "system_prompt": "You are a helpful assistant",
    "llm": ChatMistralAI(...),        # Resolved LLM instance
    "temperature": 0.1,
    "memory": True,
    "state_class": AgentState,
    "reply_function": default_reply_function,
    "allowed_llms": {...},
    "allow_system_prompt": True,
    # ... any factory overrides
}
```

---

## Built-in Agents

### ReActAgent

Reasoning + Acting agent that iteratively uses tools to accomplish tasks.

```python
class ReActAgent(BaseAgent):
    def __init__(
        self,
        tools: list[BaseTool],
        system_prompt: str = "You are a helpful AI assistant.",
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
        max_iterations: int = 10,
    ):
        ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tools` | `list[BaseTool]` | (required) | Tools the agent can use |
| `system_prompt` | `str` | `"You are a helpful AI assistant."` | Agent instructions |
| `llm` | `str` | `"mistral-large-latest"` | LLM model name |
| `temperature` | `float` | `0.1` | LLM temperature |
| `memory` | `bool` | `False` | Enable checkpointing |
| `max_iterations` | `int` | `10` | Maximum reasoning loops |

**Methods:**

- `invoke(input: dict, config: RunnableConfig | None = None) -> dict`
- `ainvoke(input: dict, config: RunnableConfig | None = None) -> dict`
- `stream(input: dict, config: RunnableConfig | None = None) -> Iterator[dict]`

**State:**

Uses `AgentState` with standard fields.

**Example:**

```python
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile, ReadRecord

agent = ReActAgent(
    tools=[ReadFile(), ReadRecord()],
    system_prompt="You are a document assistant",
    llm="mistral-large-latest",
    temperature=0.1,
    memory=True,
    max_iterations=10
)

# Invoke directly
result = agent.invoke({
    "messages": [{"role": "user", "content": "Read file.txt"}],
    "tools": ["read_file"],
    "iteration": 0,
    "errors": []
})

# Or assign to worker
worker.assign(agent, queue="qa-agent")
```

**Graph Structure:**

```
reason (decide action) → [act (execute tool) → reason] → end
```

---

### PlanExecuteAgent

Plan-then-execute agent that creates upfront plan and executes steps sequentially.

```python
class PlanExecuteAgent(BaseAgent):
    def __init__(
        self,
        tools: list[BaseTool],
        system_prompt: str = "You are a helpful AI assistant.",
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
    ):
        ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tools` | `list[BaseTool]` | (required) | Tools available for execution |
| `system_prompt` | `str` | `"You are a helpful AI assistant."` | Planning instructions |
| `llm` | `str` | `"mistral-large-latest"` | LLM model name |
| `temperature` | `float` | `0.1` | LLM temperature |
| `memory` | `bool` | `False` | Enable checkpointing |

**Methods:**

Same as ReActAgent.

**State:**

Uses `PlanExecuteState`:

```python
class PlanExecuteState(TypedDict):
    input: str
    plan: list[str]
    current_step: int
    step_results: Annotated[list[dict], add]
    final_output: dict | None
    needs_replan: bool
```

**Example:**

```python
from aimq.agents import PlanExecuteAgent
from aimq.tools.supabase import ReadFile, WriteRecord

agent = PlanExecuteAgent(
    tools=[ReadFile(), WriteRecord()],
    system_prompt="You are a task planner",
    llm="mistral-large-latest",
    memory=True
)

result = agent.invoke({
    "input": "Analyze Q1 reports and create summary",
    "plan": [],
    "current_step": 0,
    "step_results": [],
    "final_output": None,
    "needs_replan": False
})
```

**Graph Structure:**

```
plan → execute → [execute | replan | finalize] → end
```

---

## Built-in Workflows

### DocumentWorkflow

Multi-step document processing pipeline.

```python
class DocumentWorkflow(BaseWorkflow):
    def __init__(
        self,
        storage_tool: BaseTool,
        ocr_tool: BaseTool,
        pdf_tool: BaseTool | None = None,
        checkpointer: bool = False,
    ):
        ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `storage_tool` | `BaseTool` | (required) | Tool for reading files (e.g., ReadFile) |
| `ocr_tool` | `BaseTool` | (required) | Tool for OCR processing (e.g., ImageOCR) |
| `pdf_tool` | `BaseTool \| None` | `None` | Tool for PDF processing (e.g., PageSplitter) |
| `checkpointer` | `bool` | `False` | Enable state persistence |

**Methods:**

- `invoke(input: dict, config: RunnableConfig | None = None) -> dict`

**State:**

```python
class DocumentState(TypedDict):
    document_path: str                                   # Required
    metadata: dict                                       # Required
    status: str                                          # Required
    raw_content: NotRequired[bytes]                      # Fetched content
    document_type: NotRequired[Literal["image", "pdf"]]  # Detected type
    text: NotRequired[str]                               # Extracted text
```

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

result = workflow.invoke({
    "document_path": "uploads/invoice.pdf",
    "metadata": {},
    "status": "pending"
})

# Or assign to worker
worker.assign(workflow, queue="documents")
```

**Graph Structure:**

```
fetch → detect → [process_image | process_pdf] → store → end
```

---

### MultiAgentWorkflow

Supervisor-agent collaboration workflow.

```python
class MultiAgentWorkflow(BaseWorkflow):
    def __init__(
        self,
        agents: dict[str, BaseAgent],
        supervisor_prompt: str,
        checkpointer: bool = False,
    ):
        ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agents` | `dict[str, BaseAgent]` | (required) | Named specialist agents |
| `supervisor_prompt` | `str` | (required) | Supervisor instructions |
| `checkpointer` | `bool` | `False` | Enable state persistence |

**Example:**

```python
from aimq.workflows import MultiAgentWorkflow
from aimq.agents import ReActAgent

researcher = ReActAgent(tools=[...], system_prompt="Research specialist")
writer = ReActAgent(tools=[...], system_prompt="Writing specialist")

workflow = MultiAgentWorkflow(
    agents={"researcher": researcher, "writer": writer},
    supervisor_prompt="Delegate tasks to specialists",
    checkpointer=True
)

worker.assign(workflow, queue="multi-agent")
```

---

## State Classes

### AgentState

Standard state for agents.

```python
class AgentState(TypedDict):
    """Standard state for agents."""

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

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | `Annotated[Sequence[BaseMessage], add]` | Yes | LangChain message history (accumulates) |
| `tools` | `list[str]` | Yes | Available tool names |
| `iteration` | `int` | Yes | Iteration counter |
| `errors` | `Annotated[list[str], add]` | Yes | Error messages (accumulates) |
| `current_tool` | `str` | No | Tool being executed |
| `tool_input` | `dict` | No | Input for current tool |
| `tool_output` | `Any` | No | Output from tool execution |
| `final_answer` | `str` | No | Agent's final response |
| `tenant_id` | `str` | No | For multi-tenancy |
| `metadata` | `dict[str, Any]` | No | Custom metadata |

**Usage:**

```python
from aimq.langgraph.states import AgentState

# Extend with custom fields
class MyAgentState(AgentState):
    custom_field: NotRequired[str]

@agent(state_class=MyAgentState)
def my_agent(graph, config):
    return graph
```

---

### WorkflowState

Standard state for workflows.

```python
class WorkflowState(TypedDict):
    """Standard state for workflows."""

    # Required fields
    input: dict
    errors: Annotated[list[str], add]

    # Optional fields
    current_step: NotRequired[str]
    step_results: NotRequired[Annotated[list[dict], add]]
    final_output: NotRequired[dict]
    metadata: NotRequired[dict[str, Any]]
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input` | `dict` | Yes | Original workflow input |
| `errors` | `Annotated[list[str], add]` | Yes | Error messages (accumulates) |
| `current_step` | `str` | No | Current step name |
| `step_results` | `Annotated[list[dict], add]` | No | Results from steps (accumulates) |
| `final_output` | `dict` | No | Final workflow result |
| `metadata` | `dict[str, Any]` | No | Custom metadata |

**Usage:**

```python
from aimq.langgraph.states import WorkflowState

# Use as-is or extend
@workflow(state_class=WorkflowState)
def my_workflow(graph, config):
    return graph
```

---

## Utility Functions

### resolve_llm()

Resolve LLM parameter to BaseChatModel instance.

```python
def resolve_llm(
    llm_param: BaseChatModel | str | None,
    default_model: str = "mistral-large-latest"
) -> BaseChatModel:
    ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_param` | `BaseChatModel \| str \| None` | (required) | LLM object, model name, or None |
| `default_model` | `str` | `"mistral-large-latest"` | Default model if llm_param is None |

**Returns:**

`BaseChatModel` - Resolved LLM instance

**Raises:**

- `TypeError`: If llm_param is invalid type
- `LLMResolutionError`: If LLM creation fails

**Examples:**

```python
from aimq.langgraph.utils import resolve_llm
from langchain_mistralai import ChatMistralAI

# None → default
llm = resolve_llm(None)  # Returns ChatMistralAI("mistral-large-latest")

# String → ChatMistralAI
llm = resolve_llm("mistral-small-latest")

# Object → pass through
llm = resolve_llm(ChatMistralAI(model="custom"))

# Custom default
llm = resolve_llm(None, default_model="gpt-4")
```

---

### get_default_llm()

Get default LLM from configuration with caching.

```python
def get_default_llm(model: str | None = None) -> BaseChatModel:
    ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str \| None` | `None` | Override model name |

**Returns:**

`BaseChatModel` - Cached ChatMistralAI instance

**Examples:**

```python
from aimq.langgraph.utils import get_default_llm

# Use config.mistral_model
llm = get_default_llm()

# Override model
llm = get_default_llm("mistral-small-latest")

# Subsequent calls return cached instance
llm2 = get_default_llm()  # Same object as llm
```

**Note:** LLM instances are cached to prevent connection pool exhaustion.

---

### default_reply_function()

Default reply function that enqueues responses.

```python
def default_reply_function(message: str, metadata: dict) -> None:
    ...
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Response message from agent |
| `metadata` | `dict` | Additional metadata (step info, status, etc.) |

**Behavior:**

Enqueues message to `process_agent_response` queue:

```python
{
    "message": message,
    "metadata": metadata,
    "timestamp": datetime.now().isoformat()
}
```

**Error Handling:**

Errors are logged but do not propagate (prevents agent execution failure).

**Example:**

```python
from aimq.langgraph.utils import default_reply_function

# Send update
default_reply_function("Step 1 complete", {"step": 1, "status": "success"})

# Message sent to process_agent_response queue
```

**Custom Reply Function:**

```python
def custom_reply(message: str, metadata: dict) -> None:
    """Custom reply handler."""
    print(f"Agent: {message}")
    # Send to webhook, log, etc.

@agent(reply_function=custom_reply)
def my_agent(graph, config):
    return graph
```

---

## Exception Types

All LangGraph exceptions inherit from `LangGraphError`.

### LangGraphError

Base exception for all LangGraph-related errors.

```python
class LangGraphError(Exception):
    """Base exception for all LangGraph-related errors."""
    pass
```

---

### GraphBuildError

Raised when graph building fails.

```python
class GraphBuildError(LangGraphError):
    """Raised when graph building fails."""
    pass
```

**When Raised:**

- Invalid node configuration
- Missing required nodes
- Invalid edge connections

**Example:**

```python
@workflow()
def bad_workflow(graph, config):
    # Missing entry point
    graph.add_node("step", lambda s: s)
    return graph  # Raises GraphBuildError
```

---

### GraphCompileError

Raised when graph compilation fails.

```python
class GraphCompileError(LangGraphError):
    """Raised when graph compilation fails."""
    pass
```

**When Raised:**

- Circular dependencies
- Unreachable nodes
- Invalid state schema

**Example:**

```python
@workflow()
def circular_workflow(graph, config):
    graph.add_edge("a", "b")
    graph.add_edge("b", "a")  # Circular!
    return graph  # Raises GraphCompileError
```

---

### StateValidationError

Raised when state validation fails.

```python
class StateValidationError(LangGraphError):
    """Raised when state validation fails."""
    pass
```

**When Raised:**

- Missing required state fields
- Invalid state type
- State doesn't extend AgentState (for agents)

**Example:**

```python
# Job missing required field
{
    # "messages": [...],  # Missing!
    "tools": [],
    "iteration": 0,
    "errors": []
}
# Raises StateValidationError
```

---

### CheckpointerError

Raised when checkpointer configuration or operation fails.

```python
class CheckpointerError(LangGraphError):
    """Raised when checkpointer configuration or operation fails."""
    pass
```

**When Raised:**

- Invalid Supabase connection
- Schema not initialized
- Checkpoint save/load failure

**Example:**

```python
# Missing SUPABASE_URL
@workflow(checkpointer=True)
def my_workflow(graph, config):
    return graph

# Raises CheckpointerError: SUPABASE_URL required
```

---

### OverrideSecurityError

Raised when job override violates security policy.

```python
class OverrideSecurityError(LangGraphError):
    """Raised when job override violates security policy."""
    pass
```

**When Raised:**

- LLM key not in allowed_llms
- system_prompt override when allow_system_prompt=False
- Invalid override value type

**Example:**

```python
@agent(
    allowed_llms={"small": ChatMistralAI(...)},
    allow_system_prompt=False
)
def my_agent(graph, config):
    return graph

# Job with unauthorized override
{
    "llm": "gpt-4",  # Not in allowed_llms!
    "messages": [...]
}
# Raises OverrideSecurityError
```

---

### LLMResolutionError

Raised when LLM resolution fails.

```python
class LLMResolutionError(LangGraphError):
    """Raised when LLM resolution fails."""
    pass
```

**When Raised:**

- Invalid LLM parameter type
- Failed to create LLM instance
- Missing required LangChain package

**Example:**

```python
# Invalid type
llm = resolve_llm(123)  # Raises LLMResolutionError

# Missing package
@agent(llm="gpt-4")
def my_agent(graph, config):
    return graph
# Raises LLMResolutionError (langchain-openai not installed)
```

---

### ToolValidationError

Raised when tool input validation fails.

```python
class ToolValidationError(LangGraphError):
    """Raised when tool input validation fails."""
    pass
```

**When Raised:**

- Tool input doesn't match schema
- Unauthorized file path access
- SQL injection attempt detected

**Example:**

```python
# Path traversal
validator.validate_file_path("../../etc/passwd")
# Raises ToolValidationError

# SQL injection
validator.validate_sql_query("DROP TABLE users")
# Raises ToolValidationError
```

---

## Checkpointing

### get_checkpointer()

Get or create Supabase checkpoint saver singleton.

```python
def get_checkpointer() -> PostgresSaver:
    ...
```

**Returns:**

`PostgresSaver` - LangGraph PostgreSQL checkpointer instance

**Raises:**

- `CheckpointerError`: If Supabase configuration is invalid

**Example:**

```python
from aimq.langgraph.checkpoint import get_checkpointer

# Get checkpointer
saver = get_checkpointer()

# Use with graph
graph = StateGraph(MyState)
# ... add nodes and edges ...
compiled = graph.compile(checkpointer=saver)
```

**Requirements:**

- `SUPABASE_URL` environment variable
- `SUPABASE_KEY` environment variable
- LangGraph schema created in database

**Connection String:**

Built from Supabase config:

```
postgresql://postgres:{encoded_key}@db.{project}.supabase.co:5432/postgres
```

---

## Tool Validation

### ToolInputValidator

Validates tool inputs against schemas for security.

```python
class ToolInputValidator:
    """Validates tool inputs against tool schemas for security."""

    def validate(self, tool: BaseTool, input_data: dict) -> dict:
        ...

    def validate_file_path(
        self,
        path: str,
        allowed_patterns: list[str] | None = None
    ) -> None:
        ...

    def validate_sql_query(self, query: str) -> None:
        ...
```

#### validate()

Validate tool input against tool's args_schema.

```python
def validate(self, tool: BaseTool, input_data: dict) -> dict:
    ...
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool` | `BaseTool` | LangChain tool to validate against |
| `input_data` | `dict` | Input data from LLM or user |

**Returns:**

`dict` - Validated input dictionary

**Raises:**

- `ToolValidationError`: If validation fails

**Example:**

```python
from aimq.langgraph.validation import ToolInputValidator
from aimq.tools.supabase import ReadFile

validator = ToolInputValidator()
tool = ReadFile()

# Valid input
validated = validator.validate(tool, {"path": "file.txt"})

# Invalid input
try:
    validator.validate(tool, {"wrong_field": "value"})
except ToolValidationError as e:
    print(f"Validation failed: {e}")
```

#### validate_file_path()

Validate file path for security.

```python
def validate_file_path(
    self,
    path: str,
    allowed_patterns: list[str] | None = None
) -> None:
    ...
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | File path to validate |
| `allowed_patterns` | `list[str] \| None` | Allowed path patterns (glob style) |

**Raises:**

- `ToolValidationError`: If path is invalid or unauthorized

**Prevents:**

- Path traversal attacks (`../`)
- Absolute paths outside allowed directories
- Access to sensitive files (`.env`, `/etc/passwd`, `.ssh/`)

**Example:**

```python
validator = ToolInputValidator()

# Valid paths
validator.validate_file_path("data/file.txt")
validator.validate_file_path("/tmp/file.txt", allowed_patterns=["/tmp/*"])

# Invalid paths
validator.validate_file_path("../../etc/passwd")  # Raises
validator.validate_file_path("/etc/shadow")       # Raises
validator.validate_file_path("~/.ssh/id_rsa")     # Raises
```

#### validate_sql_query()

Validate SQL query for basic injection patterns.

```python
def validate_sql_query(self, query: str) -> None:
    ...
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | SQL query to validate |

**Raises:**

- `ToolValidationError`: If query contains suspicious patterns

**Detects:**

- `DROP TABLE`
- `DELETE FROM`
- `TRUNCATE`
- `ALTER TABLE`
- `EXEC`, `EXECUTE`
- SQL comments (`--`, `/**/`)

**Example:**

```python
validator = ToolInputValidator()

# Safe query
validator.validate_sql_query("SELECT * FROM users WHERE id = 1")

# Suspicious queries
validator.validate_sql_query("DROP TABLE users")     # Raises
validator.validate_sql_query("DELETE FROM users")    # Raises
validator.validate_sql_query("SELECT * FROM users; --") # Raises
```

**Note:** This is basic validation. Always use parameterized queries in production.

---

## Type Definitions

### State Type Annotations

```python
from typing import Annotated, Any, NotRequired, Sequence, TypedDict
from operator import add
from langchain_core.messages import BaseMessage

# Accumulating field
messages: Annotated[Sequence[BaseMessage], add]

# Optional field
final_answer: NotRequired[str]

# Required field
iteration: int
```

### LLM Types

```python
from langchain_core.language_models import BaseChatModel

# LLM parameter types
llm: BaseChatModel | str | None
```

### Tool Types

```python
from langchain.tools import BaseTool

# Tool list
tools: list[BaseTool]
```

### Callback Types

```python
from typing import Callable

# Reply function
reply_function: Callable[[str, dict], None]
```

---

## See Also

- **[LangGraph Integration Guide](../user-guide/langgraph.md)**: Main integration documentation
- **[Agents Guide](../user-guide/agents.md)**: Agent patterns and usage
- **[Workflows Guide](../user-guide/workflows.md)**: Workflow patterns and usage
- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)**: Official LangGraph docs
- **[LangChain Tools](https://python.langchain.com/docs/integrations/tools)**: Tool integrations
