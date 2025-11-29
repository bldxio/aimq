# Workflows Guide

Workflows are deterministic multi-step processes with fixed execution paths. AIMQ's workflow system provides a decorator-based framework for building stateful pipelines powered by LangGraph.

## What Are Workflows?

A workflow is a program that:

1. Defines a series of **nodes** (processing steps)
2. Connects nodes with **edges** (transitions)
3. Routes execution based on **conditions** (optional)
4. Maintains **state** across steps
5. Produces a **final output**

Unlike agents that make dynamic decisions, workflows follow predetermined paths. This makes them faster, more predictable, and easier to debug.

### When to Use Workflows vs Agents

**Use workflows when:**

- Steps are known upfront
- Execution path is deterministic
- No reasoning or decision-making required
- Performance is critical
- Process is repeatable and structured

**Use agents instead when:**

- Task requires dynamic decision-making
- Available tools vary by context
- Multi-turn conversations needed
- Problem-solving approach depends on input

**Decision Matrix:**

| Characteristic | Workflow | Agent |
|---------------|----------|-------|
| Execution path | Fixed | Dynamic |
| Decision making | Rule-based | LLM-based |
| Performance | Fast | Slower |
| Debugging | Easy | Harder |
| Predictability | High | Variable |
| Use case | ETL, pipelines | QA, research |

**Examples:**

- ✅ **Workflow**: "Read CSV → Transform data → Store in DB"
- ✅ **Workflow**: "Fetch document → Detect type → OCR/parse → Extract metadata → Store"
- ❌ **Agent**: "Analyze these documents and answer questions"
- ❌ **Agent**: "Research topic X using available tools"

## Built-in Workflows

AIMQ includes production-ready workflows for common patterns.

### DocumentWorkflow

**Pattern**: Multi-step document processing pipeline

The DocumentWorkflow handles end-to-end document processing with automatic type detection and routing.

**Pipeline Steps:**

```
1. Fetch: Read document from storage
2. Detect: Identify document type (image, PDF, etc.)
3. Route: Choose processor based on type
4. Process: Extract text (OCR for images, parser for PDFs)
5. Store: Save results and metadata
```

**Features:**

- Automatic MIME type detection
- Conditional routing by document type
- OCR for images (JPEG, PNG, etc.)
- PDF text extraction
- Metadata extraction and storage
- Error handling at each step

**Example Usage:**

```python
from aimq.workflows import DocumentWorkflow
from aimq.tools.supabase import ReadFile
from aimq.tools.ocr import ImageOCR
from aimq.tools.pdf import PageSplitter
from aimq.worker import Worker

worker = Worker()

workflow = DocumentWorkflow(
    storage_tool=ReadFile(),       # Read from Supabase storage
    ocr_tool=ImageOCR(),            # Process images
    pdf_tool=PageSplitter(),        # Process PDFs
    checkpointer=True               # Enable resumable processing
)

worker.assign(
    workflow,
    queue="documents",
    timeout=600,
    delete_on_finish=False
)
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

```python
class DocumentState(TypedDict):
    # Required
    document_path: str
    metadata: dict
    status: str

    # Populated during processing
    raw_content: NotRequired[bytes]
    document_type: NotRequired[Literal["image", "pdf", "docx"]]
    text: NotRequired[str]
```

**Supported Document Types:**

- **Images**: JPEG, PNG, TIFF, BMP (via OCR)
- **PDFs**: Text extraction and OCR for scanned PDFs
- **Future**: DOCX, XLSX, PPTX (extensible)

**Use Cases:**

- Invoice processing
- Receipt OCR
- Contract analysis
- Batch document ingestion
- Document digitization

### MultiAgentWorkflow

**Pattern**: Supervisor-agent collaboration

Coordinates multiple specialized agents for complex tasks requiring different expertise.

**Architecture:**

```
Supervisor
    ├─> Research Agent (gather information)
    ├─> Analysis Agent (analyze data)
    ├─> Writing Agent (generate reports)
    └─> Validator Agent (verify results)
```

**Features:**

- Multiple specialist agents
- Supervisor for task delegation
- Parallel or sequential execution
- Result aggregation
- Error handling and retries

**Example Usage:**

```python
from aimq.workflows import MultiAgentWorkflow
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile, WriteRecord

worker = Worker()

# Define specialist agents
researcher = ReActAgent(
    tools=[ReadFile()],
    system_prompt="You are a research specialist. Gather information.",
    llm="mistral-large-latest"
)

writer = ReActAgent(
    tools=[WriteRecord()],
    system_prompt="You are a writing specialist. Create reports.",
    llm="mistral-large-latest"
)

# Create multi-agent workflow
workflow = MultiAgentWorkflow(
    agents={
        "researcher": researcher,
        "writer": writer
    },
    supervisor_prompt="""You are a supervisor coordinating specialists.

    Available agents:
    - researcher: Gathers information from documents
    - writer: Creates structured reports

    Delegate tasks appropriately and aggregate results.""",
    checkpointer=True
)

worker.assign(workflow, queue="multi-agent", timeout=1800)
```

**Job Format:**

```json
{
  "task": "Research Q1 reports and create a summary",
  "agents_used": [],
  "results": {},
  "status": "pending"
}
```

**Use Cases:**

- Complex research projects
- Multi-domain analysis
- Collaborative document creation
- Specialized task decomposition

## Creating Custom Workflows

Build specialized workflows using the `@workflow` decorator.

### Step-by-Step Tutorial

#### 1. Define Custom State

State defines what data flows through the workflow:

```python
from typing import Annotated, NotRequired, TypedDict
from operator import add

class ETLState(TypedDict):
    """State for ETL (Extract-Transform-Load) pipeline."""

    # Required fields (must be present at initialization)
    source_path: str                      # Input file path
    load_status: str                      # Final status
    errors: Annotated[list[str], add]     # Accumulated errors

    # Optional fields (populated during execution)
    extracted_data: NotRequired[dict]     # Raw data from extract
    transformed_data: NotRequired[dict]   # Processed data
    row_count: NotRequired[int]           # Number of records
    metadata: NotRequired[dict]           # Additional info
```

**State Design Rules:**

- Use `TypedDict` for type safety
- Mark required fields (no `NotRequired`)
- Mark optional fields with `NotRequired`
- Use `Annotated[list, add]` for accumulating lists
- Keep state minimal (only what's needed across nodes)

#### 2. Define Workflow with Decorator

```python
from langgraph.graph import END, StateGraph
from aimq.langgraph import workflow
from aimq.tools.supabase import ReadFile, WriteRecord

@workflow(state_class=ETLState, checkpointer=True)
def etl_pipeline(graph: StateGraph, config: dict) -> StateGraph:
    """
    ETL workflow: Extract → Transform → Load

    The config dict contains:
    - state_class: Type[TypedDict] - The state class
    - checkpointer: bool - Whether persistence is enabled
    """

    def extract(state: ETLState) -> ETLState:
        """Extract data from source file."""
        import json

        tool = ReadFile()
        try:
            content = tool.invoke({"path": state["source_path"]})

            # Parse based on file type
            if state["source_path"].endswith(".json"):
                data = json.loads(content)
            elif state["source_path"].endswith(".csv"):
                # Simple CSV parsing
                lines = content.strip().split("\n")
                headers = lines[0].split(",")
                rows = [dict(zip(headers, line.split(","))) for line in lines[1:]]
                data = {"headers": headers, "rows": rows}
            else:
                data = {"raw": content}

            return {
                "extracted_data": data,
                "row_count": len(data.get("rows", [data]))
            }

        except Exception as e:
            return {"errors": [f"Extract failed: {e}"]}

    def transform(state: ETLState) -> ETLState:
        """Transform extracted data."""
        if not state.get("extracted_data"):
            return {"errors": ["No data to transform"]}

        try:
            data = state["extracted_data"]

            # Example transformations
            transformed = {
                "processed_at": "2024-10-30T12:00:00Z",
                "original_rows": state.get("row_count", 0)
            }

            if "rows" in data:
                # CSV: Uppercase all text
                transformed["data"] = [
                    {k: v.upper() if isinstance(v, str) else v for k, v in row.items()}
                    for row in data["rows"]
                ]
            else:
                # Generic transformation
                transformed["data"] = str(data).upper()

            return {"transformed_data": transformed}

        except Exception as e:
            return {"errors": [f"Transform failed: {e}"]}

    def load(state: ETLState) -> ETLState:
        """Load transformed data into database."""
        if not state.get("transformed_data"):
            return {
                "errors": ["No data to load"],
                "load_status": "failed"
            }

        tool = WriteRecord()
        try:
            tool.invoke({
                "table": "etl_results",
                "data": {
                    "source_path": state["source_path"],
                    "row_count": state.get("row_count", 0),
                    "transformed_data": state["transformed_data"],
                    "processed_at": "NOW()"
                }
            })

            return {"load_status": "success"}

        except Exception as e:
            return {
                "errors": [f"Load failed: {e}"],
                "load_status": "failed"
            }

    # Build graph (linear pipeline)
    graph.add_node("extract", extract)
    graph.add_node("transform", transform)
    graph.add_node("load", load)

    # Connect nodes sequentially
    graph.add_edge("extract", "transform")
    graph.add_edge("transform", "load")
    graph.add_edge("load", END)

    # Set starting node
    graph.set_entry_point("extract")

    return graph
```

#### 3. Create and Assign Instance

```python
from aimq.worker import Worker

worker = Worker()
workflow_instance = etl_pipeline()
worker.assign(
    workflow_instance,
    queue="etl-pipeline",
    timeout=600,
    delete_on_finish=False
)
```

#### 4. Send Jobs

```bash
aimq send etl-pipeline '{
  "source_path": "data/sales_2024.csv",
  "load_status": "",
  "errors": []
}'
```

### Workflow State Management

**State Updates:**

Nodes return partial state updates (not full state):

```python
def my_node(state: MyState) -> MyState:
    # Access current state
    current_value = state.get("field")

    # Return updates only
    return {
        "field": "new_value",
        "another_field": 123
    }
```

**State Reducers:**

Use `Annotated` with `add` for accumulating lists:

```python
from operator import add
from typing import Annotated

class MyState(TypedDict):
    errors: Annotated[list[str], add]  # Errors accumulate

def node1(state):
    return {"errors": ["Error A"]}  # errors = ["Error A"]

def node2(state):
    return {"errors": ["Error B"]}  # errors = ["Error A", "Error B"]
```

**Required vs Optional:**

```python
class MyState(TypedDict):
    # Required: Must be in job data
    input_file: str
    status: str

    # Optional: Populated during workflow
    output: NotRequired[str]
    metadata: NotRequired[dict]
```

### Implementing Nodes

**Node Function Signature:**

```python
def my_node(state: MyState) -> MyState:
    """
    Process state and return updates.

    Args:
        state: Current workflow state

    Returns:
        Dict with state updates
    """
    # Access state
    input_data = state.get("input_file")

    # Process...
    result = process(input_data)

    # Return updates
    return {"output": result, "status": "processed"}
```

**Node Best Practices:**

1. **Single Responsibility**: Each node does one thing
2. **Error Handling**: Catch and report errors gracefully
3. **Logging**: Log progress for debugging
4. **State Validation**: Check required fields before processing
5. **Return Updates**: Only return changed fields

**Example Node with Best Practices:**

```python
import logging

logger = logging.getLogger(__name__)

def validate_node(state: MyState) -> MyState:
    """Validate input data."""
    logger.info("Validating input data")

    # Check required fields
    if not state.get("input_file"):
        logger.error("Missing input_file")
        return {
            "errors": ["input_file is required"],
            "status": "failed"
        }

    try:
        # Validate file exists
        if not os.path.exists(state["input_file"]):
            raise FileNotFoundError(f"File not found: {state['input_file']}")

        logger.info("Validation passed")
        return {"status": "validated"}

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return {
            "errors": [f"Validation error: {e}"],
            "status": "failed"
        }
```

### Conditional Routing

Use conditional edges for branching logic:

```python
from typing import Literal

@workflow(state_class=MyState)
def branching_workflow(graph: StateGraph, config: dict) -> StateGraph:

    def decide_route(state: MyState) -> Literal["process_a", "process_b", "error"]:
        """Routing logic based on state."""

        # Check for errors
        if state.get("errors"):
            return "error"

        # Route by data type
        if state.get("data_type") == "csv":
            return "process_a"
        elif state.get("data_type") == "json":
            return "process_b"

        return "error"

    # Add nodes
    graph.add_node("start", start_node)
    graph.add_node("process_a", process_csv_node)
    graph.add_node("process_b", process_json_node)
    graph.add_node("error", error_node)

    # Conditional routing
    graph.add_conditional_edges(
        "start",                    # From node
        decide_route,               # Decision function
        {
            "process_a": "process_a",
            "process_b": "process_b",
            "error": "error"
        }
    )

    # Connect to end
    graph.add_edge("process_a", END)
    graph.add_edge("process_b", END)
    graph.add_edge("error", END)

    graph.set_entry_point("start")

    return graph
```

**Routing Function Rules:**

- Return type must be `Literal[...]` with all possible routes
- Must return one of the keys in the routing map
- Can access full state for decision-making
- Should handle all cases (including errors)

### Linear Pipelines vs Branching

**Linear Pipeline:**

```python
# Simple sequential flow
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)
```

**Branching Workflow:**

```python
# Conditional routing
graph.add_conditional_edges(
    "router",
    decision_function,
    {
        "path_a": "process_a",
        "path_b": "process_b"
    }
)
```

**Parallel Paths (Converging):**

```python
# Multiple paths to same node
graph.add_edge("path_a", "merge")
graph.add_edge("path_b", "merge")
graph.add_edge("merge", END)
```

**Complex Graph:**

```python
# Combination of patterns
graph.add_conditional_edges("start", router, {...})
graph.add_edge("process_a", "validate")
graph.add_edge("process_b", "validate")
graph.add_conditional_edges("validate", check_valid, {...})
```

## Configuration Options

### State Class

Custom TypedDict defining workflow state:

```python
@workflow(state_class=MyState)
def my_workflow(graph, config):
    # state_class available in config
    state_class = config["state_class"]
    return graph
```

### Checkpointer

Enable persistent state for resumable workflows:

```python
@workflow(checkpointer=True)
def my_workflow(graph, config):
    # Workflow state saved to database
    # Can resume from interruption
    return graph
```

**Requirements:**

- Supabase connection configured
- LangGraph schema created
- `thread_id` in job data (for resuming)

**Job with Thread ID:**

```json
{
  "source_path": "large_file.csv",
  "thread_id": "batch-2024-10-30",
  "load_status": "",
  "errors": []
}
```

## Advanced Topics

### Sub-workflows

Compose workflows from smaller workflows:

```python
@workflow(state_class=PreprocessState)
def preprocess_workflow(graph, config):
    """Sub-workflow for preprocessing."""
    # Define preprocessing steps
    return graph

@workflow(state_class=MainState)
def main_workflow(graph, config):
    """Main workflow using sub-workflow."""

    def preprocess_step(state):
        # Call sub-workflow
        preprocess = preprocess_workflow()
        result = preprocess.invoke({
            "input": state["raw_data"]
        })
        return {"preprocessed": result}

    graph.add_node("preprocess", preprocess_step)
    # Continue with main workflow...
    return graph
```

### Error Handling

Collect and handle errors systematically:

```python
class MyState(TypedDict):
    errors: Annotated[list[str], add]  # Accumulate errors
    status: str

def risky_node(state: MyState) -> MyState:
    try:
        result = risky_operation()
        return {"result": result, "status": "success"}
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        return {
            "errors": [f"Node failed: {e}"],
            "status": "error"
        }

def error_handler(state: MyState) -> MyState:
    """Handle accumulated errors."""
    if state.get("errors"):
        logger.error(f"Workflow failed with errors: {state['errors']}")
        return {"status": "failed"}
    return {"status": "success"}
```

**Error Routing:**

```python
def error_check(state) -> Literal["continue", "error"]:
    return "error" if state.get("errors") else "continue"

graph.add_conditional_edges(
    "risky_node",
    error_check,
    {"continue": "next_node", "error": "error_handler"}
)
```

### Checkpointing Long Workflows

Resume workflows after interruption:

```python
@workflow(checkpointer=True)
def long_workflow(graph, config):
    """Workflow with checkpointing enabled."""

    def step1(state):
        # Heavy processing...
        return {"step1_result": "done"}
        # State automatically saved after this step

    def step2(state):
        # If workflow interrupted, can resume from here
        return {"step2_result": "done"}

    graph.add_node("step1", step1)
    graph.add_node("step2", step2)
    graph.add_edge("step1", "step2")
    graph.add_edge("step2", END)

    return graph
```

**Resume Example:**

```bash
# Initial job
aimq send long-workflow '{
  "input": "data.csv",
  "thread_id": "job-123",
  "errors": []
}'

# If interrupted, resume by sending same thread_id
aimq send long-workflow '{
  "input": "data.csv",
  "thread_id": "job-123",  # Same ID
  "errors": []
}'
```

## Examples

Complete working examples in `examples/langgraph/`:

**Custom Workflow with Decorator:**

```bash
uv run python examples/langgraph/custom_workflow_decorator.py
```

**Document Processing Workflow:**

```bash
uv run python examples/langgraph/using_builtin_document.py
```

**Multi-Agent Workflow:**

```bash
uv run python examples/langgraph/using_builtin_multi_agent.py
```

## API Reference

See complete API documentation: [LangGraph API Reference](../api/langgraph.md)

**Key Classes:**

- `aimq.workflows.DocumentWorkflow`: Built-in document processing
- `aimq.workflows.MultiAgentWorkflow`: Built-in multi-agent coordination
- `aimq.langgraph.states.WorkflowState`: Standard workflow state
- `aimq.langgraph.decorators.workflow`: Workflow decorator

**Key Functions:**

- `get_checkpointer()`: Get PostgreSQL checkpointer instance

## Next Steps

- **[Agents Guide](./agents.md)**: Learn about agentic workflows
- **[LangGraph Integration](./langgraph.md)**: Main integration guide
- **[API Reference](../api/langgraph.md)**: Complete API documentation
- **Examples**: `examples/langgraph/` for working code
