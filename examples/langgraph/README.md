# LangGraph Integration Examples

This directory contains comprehensive examples demonstrating AIMQ's LangGraph integration features.

## Examples Overview

| Example | Type | Description | File | Complexity |
|---------|------|-------------|------|------------|
| ReAct Agent | Built-in | Document Q&A with reasoning-action loop | `using_builtin_react.py` | Beginner |
| Document Workflow | Built-in | Automated document processing pipeline | `using_builtin_document.py` | Beginner |
| Custom Agent | Decorator | Data processing agent with custom logic | `custom_agent_decorator.py` | Intermediate |
| Custom Workflow | Decorator | ETL pipeline with custom state | `custom_workflow_decorator.py` | Advanced |

## Prerequisites

### 1. Dependencies Installed

```bash
# Install all dependencies including LangGraph
uv sync
```

### 2. Supabase Configuration

Create a `.env` file in the project root:

```bash
# Required for all examples
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Required for agent examples (ReAct, Custom Agent)
MISTRAL_API_KEY=your-mistral-api-key

# Optional: Enable LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=aimq-examples
```

### 3. Checkpointing Setup (Optional)

For memory-enabled examples (resumable workflows):

**Option A: Automatic setup**
```bash
# Set in .env
LANGGRAPH_CHECKPOINT_ENABLED=true
```

**Option B: Manual setup**
```bash
# Run SQL from docs/deployment/langgraph-schema.sql in Supabase SQL Editor
# This creates the langgraph.checkpoints table
```

### 4. Queue Setup

Enable queues before running workers:

```bash
# Enable all example queues
aimq enable doc-qa
aimq enable doc-pipeline
aimq enable data-processor
aimq enable etl-pipeline
```

## Running Examples

### 1. Built-in ReAct Agent

The ReAct (Reasoning + Acting) pattern enables agents to reason about tasks and execute tools iteratively.

**Features demonstrated:**
- Using built-in agents
- Tool integration (ReadFile, ImageOCR, ReadRecord)
- Checkpointing with `memory=True`
- Reasoning-action loop
- Multi-step workflows

**Start the worker:**
```bash
# Terminal 1
uv run python examples/langgraph/using_builtin_react.py
```

**Send test jobs:**
```bash
# Terminal 2

# Simple file query
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "Read the file at documents/report.pdf"}
  ],
  "tools": ["read_file"],
  "iteration": 0,
  "errors": []
}'

# Multi-step reasoning
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "Compare sales data from Q1 and Q2 reports"}
  ],
  "tools": ["read_file", "read_record"],
  "iteration": 0,
  "errors": []
}'

# OCR processing
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "Extract text from images/invoice.jpg"}
  ],
  "tools": ["image_ocr"],
  "iteration": 0,
  "errors": []
}'
```

---

### 2. Built-in Document Workflow

Automated pipeline for document ingestion and processing with type detection.

**Features demonstrated:**
- Built-in workflows
- Conditional routing by document type
- Multi-step pipeline (fetch → detect → process → store)
- Error handling in nodes
- Batch processing patterns

**Start the worker:**
```bash
# Terminal 1
uv run python examples/langgraph/using_builtin_document.py
```

**Send test jobs:**
```bash
# Terminal 2

# Process PDF document
aimq send doc-pipeline '{
  "document_path": "uploads/report.pdf",
  "metadata": {"source": "email", "priority": "high"},
  "status": "pending"
}'

# Process scanned image
aimq send doc-pipeline '{
  "document_path": "scans/invoice_001.jpg",
  "metadata": {"type": "invoice", "department": "finance"},
  "status": "pending"
}'

# Batch processing
for file in uploads/*.pdf; do
  aimq send doc-pipeline "{
    \"document_path\": \"$file\",
    \"metadata\": {\"batch\": \"2024-10\"},
    \"status\": \"pending\"
  }"
done
```

---

### 3. Custom Agent with Decorator

Build custom agents with the `@agent` decorator for specialized workflows.

**Features demonstrated:**
- `@agent` decorator pattern
- Custom graph building with nodes and edges
- Accessing config in nodes (tools, LLM, system_prompt)
- LLM integration via Mistral client
- Tool chaining (ReadFile → Analyze → WriteRecord)

**Start the worker:**
```bash
# Terminal 1
uv run python examples/langgraph/custom_agent_decorator.py
```

**Send test jobs:**
```bash
# Terminal 2

# Analyze CSV file
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "data/sales_2024.csv"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}'

# Analyze JSON data
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "exports/user_data.json"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}'

# Resumable analysis with thread_id
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "large_files/yearly_report.csv"}
  ],
  "thread_id": "analysis-session-789",
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

---

### 4. Custom Workflow with Decorator

Build custom workflows with the `@workflow` decorator and custom state definitions.

**Features demonstrated:**
- `@workflow` decorator pattern
- Custom state definition (ETLState with TypedDict)
- ETL pipeline pattern (Extract → Transform → Load)
- Error collection with `Annotated[list[str], add]`
- Linear workflow with sequential steps
- Type safety with typed state

**Start the worker:**
```bash
# Terminal 1
uv run python examples/langgraph/custom_workflow_decorator.py
```

**Send test jobs:**
```bash
# Terminal 2

# Process CSV file
aimq send etl-pipeline '{
  "source_path": "data/sales_2024.csv",
  "load_status": "",
  "errors": []
}'

# Process JSON data
aimq send etl-pipeline '{
  "source_path": "exports/user_data.json",
  "load_status": "",
  "errors": []
}'

# Process text file
aimq send etl-pipeline '{
  "source_path": "logs/application.log",
  "load_status": "",
  "errors": []
}'

# Resumable ETL with thread_id
aimq send etl-pipeline '{
  "source_path": "large_files/yearly_data.csv",
  "thread_id": "etl-batch-2024-10",
  "load_status": "",
  "errors": []
}'
```

---

## Common Patterns

### State Structures

Each workflow type requires specific state fields:

**AgentState (for ReAct and custom agents):**
```json
{
  "messages": [
    {"role": "user", "content": "Your query here"}
  ],
  "tools": ["tool_name_1", "tool_name_2"],
  "iteration": 0,
  "errors": []
}
```

**DocumentState (for document workflow):**
```json
{
  "document_path": "path/to/document.pdf",
  "metadata": {"key": "value"},
  "status": "pending"
}
```

**Custom State (ETL example):**
```json
{
  "source_path": "data/input.csv",
  "load_status": "",
  "errors": []
}
```

### Resumable Workflows (Thread ID)

For workflows with checkpointing enabled, add `thread_id` to resume from where you left off:

```bash
aimq send doc-qa '{
  "messages": [...],
  "thread_id": "user-123-session-456",
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

Later, send another message with the same `thread_id` to continue:

```bash
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "What were the conclusions?"}
  ],
  "thread_id": "user-123-session-456",  # Same thread
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

### Job-Level Configuration Overrides

Some agents support per-job configuration overrides:

```python
# In agent definition
agent = ReActAgent(
    tools=[...],
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
    },
    allow_system_prompt=True,
    allow_temperature=True,
)
```

```bash
# In job data
aimq send doc-qa '{
  "messages": [...],
  "llm": "small",  # Override to use smaller model
  "system_prompt": "Custom instructions for this specific task",
  "temperature": 0.7,
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

### Error Handling Pattern

Use `Annotated[list[str], add]` for error accumulation:

```python
from typing import Annotated
from operator import add

class MyState(TypedDict):
    errors: Annotated[list[str], add]  # Errors accumulate, not overwrite

def node1(state):
    return {"errors": ["Error from node1"]}

def node2(state):
    return {"errors": ["Error from node2"]}

# Final state will have: {"errors": ["Error from node1", "Error from node2"]}
```

---

## Debugging

### Enable Debug Logging

Add to your worker file:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check Checkpoints in Supabase

```sql
-- In Supabase SQL Editor
SELECT
    thread_id,
    checkpoint_id,
    created_at,
    metadata
FROM langgraph.checkpoints
ORDER BY created_at DESC
LIMIT 10;
```

### View Agent State During Execution

Add logging to your nodes:

```python
def my_node(state):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Current state: {state}")
    logger.info(f"Messages: {state.get('messages', [])}")
    # ... node logic
```

### Test Job Validation

Use Python to validate job structure before sending:

```python
from aimq.langgraph.states import AgentState
from langchain_core.messages import HumanMessage

# Validate job structure
job_data = {
    "messages": [HumanMessage(content="Test")],
    "tools": ["read_file"],
    "iteration": 0,
    "errors": [],
}

# This will raise TypeError if structure is invalid
state: AgentState = job_data  # type: ignore
```

---

## Troubleshooting

### "Module not found" errors

**Problem:** Import errors when running examples

**Solution:**
```bash
# Reinstall dependencies
uv sync

# Verify installation
uv run python -c "import langgraph; print(langgraph.__version__)"
```

### "Queue not found" errors

**Problem:** Worker can't find queue in pgmq

**Solution:**
```bash
# Enable queue first
aimq enable doc-qa

# Verify queue exists (in Supabase SQL Editor)
SELECT * FROM pgmq.list_queues();
```

### "Checkpoint schema not found" errors

**Problem:** Memory-enabled workflows fail with schema errors

**Solution:**
```bash
# Option 1: Run schema setup SQL
# Copy contents of docs/deployment/langgraph-schema.sql
# Run in Supabase SQL Editor

# Option 2: Disable checkpointing
# In your worker file:
agent = ReActAgent(
    tools=[...],
    memory=False,  # Disable checkpointing
)
```

### Agent gets stuck in infinite loop

**Problem:** Agent keeps iterating without finishing

**Solution:**
```python
# Set max_iterations limit
agent = ReActAgent(
    tools=[...],
    max_iterations=10,  # Prevent infinite loops
)

# Or check iteration count in custom nodes
def my_node(state):
    if state.get("iteration", 0) > 10:
        return {"final_answer": "Max iterations reached", "iteration": state["iteration"] + 1}
```

### Tool execution fails silently

**Problem:** Tools fail but no error is reported

**Solution:**
```python
# Wrap tool calls in try-except
def my_node(state):
    try:
        result = tool.invoke(input_data)
        return {"tool_output": result}
    except Exception as e:
        return {"errors": [f"Tool failed: {str(e)}"]}
```

### State structure mismatch

**Problem:** Job data doesn't match expected state structure

**Solution:**
```bash
# Always match the state class definition
# For AgentState:
{
  "messages": [...],  # Required
  "tools": [],        # Required
  "iteration": 0,     # Required
  "errors": []        # Required
}

# For DocumentState:
{
  "document_path": "...",  # Required
  "metadata": {},          # Required
  "status": "pending"      # Required
}
```

### Missing tool dependencies

**Problem:** OCR or PDF tools fail with import errors

**Solution:**
```bash
# Ensure all optional dependencies are installed
uv sync

# For OCR specifically (requires torch, easyocr)
# These are included in pyproject.toml dependencies
```

---

## Next Steps

### Learn More

- **Read the docs**: [`docs/user-guide/langgraph.md`](../../docs/user-guide/langgraph.md)
- **API Reference**: [`docs/api/langgraph.md`](../../docs/api/langgraph.md)
- **Architecture**: [`docs/architecture/langgraph.md`](../../docs/architecture/langgraph.md)

### Create Your Own

1. **Copy an example** that matches your use case
2. **Modify the state** to fit your data structure
3. **Add custom nodes** with your business logic
4. **Test locally** with `aimq send` before deploying
5. **Enable checkpointing** for long-running workflows

### Explore Tools

Available tools in `src/aimq/tools/`:

- **Supabase**: ReadFile, WriteFile, ReadRecord, WriteRecord, Enqueue, GetURL
- **OCR**: ImageOCR (text extraction from images)
- **PDF**: PageSplitter (split and extract PDF pages)
- **Mistral**: DocumentOCR, UploadFile (Mistral AI integration)
- **Docling**: Converter (advanced document conversion)

### Deploy to Production

```bash
# 1. Build Docker image
docker build -t my-aimq-worker .

# 2. Push to registry
docker push my-aimq-worker

# 3. Deploy with environment variables
docker run -e SUPABASE_URL=... -e MISTRAL_API_KEY=... my-aimq-worker
```

See [`docker/README.md`](../../docker/README.md) for deployment patterns.

---

## Performance Tips

### Optimize Tool Usage

```python
# Bad: Sequential tool calls
result1 = tool1.invoke(input1)
result2 = tool2.invoke(input2)

# Good: Batch operations when possible
results = batch_tool.invoke([input1, input2])
```

### Use Smaller Models for Simple Tasks

```python
# For classification or simple extraction
agent = ReActAgent(
    llm="mistral-small-latest",  # Faster, cheaper
    tools=[...],
)

# For complex reasoning
agent = ReActAgent(
    llm="mistral-large-latest",  # More capable
    tools=[...],
)
```

### Limit Context Size

```python
# Trim message history to prevent context overflow
def trim_messages(messages, max_messages=10):
    return messages[-max_messages:]

def my_node(state):
    trimmed = trim_messages(state["messages"])
    # Use trimmed messages for LLM call
```

### Enable Parallel Execution

```python
from langgraph.graph import StateGraph

# Add parallel branches
graph.add_node("fetch_data", fetch_data)
graph.add_node("fetch_metadata", fetch_metadata)

# These run in parallel
graph.add_edge("start", "fetch_data")
graph.add_edge("start", "fetch_metadata")

# Then merge results
graph.add_edge("fetch_data", "merge")
graph.add_edge("fetch_metadata", "merge")
```

---

## Contributing

Found a bug or have an improvement?

1. **Open an issue** describing the problem
2. **Submit a PR** with a new example or fix
3. **Add tests** for new functionality
4. **Update documentation** if needed

---

## License

MIT License - see [LICENSE](../../LICENSE) file.

---

**Need help?** Open an issue on GitHub or check the documentation at [`docs/`](../../docs/).
