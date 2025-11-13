# LangGraph Integration

## Overview

AIMQ uses LangGraph to build stateful, multi-step workflows with agents. LangGraph enables complex agent orchestration, memory management, and human-in-the-loop patterns.

## Core Concepts

### StateGraph

LangGraph workflows are defined as state graphs:

```python
from langgraph.graph import StateGraph, END

# Define workflow
workflow = StateGraph(StateType)

# Add nodes (steps)
workflow.add_node("step1", step1_function)
workflow.add_node("step2", step2_function)

# Add edges (transitions)
workflow.add_edge("step1", "step2")
workflow.add_edge("step2", END)

# Set entry point
workflow.set_entry_point("step1")

# Compile
app = workflow.compile()
```

### State Management

State is passed between nodes and persists across steps:

```python
from typing import TypedDict, Annotated
from langgraph.graph import MessagesState

class AgentState(TypedDict):
    messages: Annotated[list, "Messages in conversation"]
    current_step: str
    result: dict | None

def step1(state: AgentState) -> AgentState:
    # Modify state
    state["current_step"] = "step1"
    state["messages"].append({"role": "assistant", "content": "Processing..."})
    return state
```

### Checkpointing

LangGraph supports state persistence for long-running workflows:

```python
from langgraph.checkpoint.memory import MemorySaver

# In-memory checkpointing
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# Execute with thread_id for persistence
result = app.invoke(
    input_data,
    config={"configurable": {"thread_id": "conversation-123"}}
)

# Resume later with same thread_id
result = app.invoke(
    new_input,
    config={"configurable": {"thread_id": "conversation-123"}}
)
```

## AIMQ's LangGraph Usage

### Agent Implementations

AIMQ provides two agent types using LangGraph:

#### 1. ReAct Agent (`agents/react.py`)

Reasoning + Acting pattern:

```python
from aimq.agents.react import create_react_agent

agent = create_react_agent(
    llm=llm,
    tools=[ImageOCR(), ReadRecord(), WriteRecord()],
    system_prompt="You are a helpful assistant"
)

result = agent.invoke({"input": "Extract text from image.jpg"})
```

**Flow**:
1. Agent receives input
2. Agent reasons about what to do
3. Agent selects and executes tool
4. Agent processes tool output
5. Repeat until task complete

#### 2. Plan-Execute Agent (`agents/plan_execute.py`)

Planning + Execution pattern:

```python
from aimq.agents.plan_execute import create_plan_execute_agent

agent = create_plan_execute_agent(
    llm=llm,
    tools=[ImageOCR(), PageSplitter()],
)

result = agent.invoke({"input": "Process all PDFs in bucket"})
```

**Flow**:
1. Planner creates step-by-step plan
2. Executor runs each step
3. Replanner adjusts plan based on results
4. Repeat until plan complete

### Workflow Implementations

#### 1. Multi-Agent Workflow (`workflows/multi_agent.py`)

Orchestrates multiple specialized agents:

```python
from aimq.workflows.multi_agent import create_multi_agent_workflow

workflow = create_multi_agent_workflow(
    agents={
        "researcher": research_agent,
        "writer": writing_agent,
        "reviewer": review_agent,
    }
)

result = workflow.invoke({"task": "Write article about AI"})
```

**Flow**:
1. Supervisor routes task to appropriate agent
2. Agent processes and returns result
3. Supervisor decides next agent or completion
4. Repeat until task complete

#### 2. Document Workflow (`workflows/document.py`)

Processes documents through multiple stages:

```python
from aimq.workflows.document import create_document_workflow

workflow = create_document_workflow(
    llm=llm,
    tools=[ImageOCR(), PageSplitter()],
)

result = workflow.invoke({"document_url": "s3://bucket/doc.pdf"})
```

**Flow**:
1. Download document
2. Extract text (OCR if needed)
3. Chunk text
4. Generate embeddings
5. Store in vector database

## State Types

### MessagesState

Built-in state for message-based workflows:

```python
from langgraph.graph import MessagesState

class MyState(MessagesState):
    # Inherits 'messages' field
    custom_field: str

def node(state: MyState) -> MyState:
    state["messages"].append({"role": "assistant", "content": "Hello"})
    state["custom_field"] = "value"
    return state
```

### Custom State

Define custom state types:

```python
from typing import TypedDict, Annotated
from operator import add

class WorkflowState(TypedDict):
    input: str
    steps_completed: Annotated[list[str], add]  # Append to list
    result: dict | None

def step1(state: WorkflowState) -> WorkflowState:
    state["steps_completed"] = ["step1"]  # Will be appended
    return state
```

**Annotations**:
- `add`: Append to list
- `operator.or_`: Merge dicts
- Custom reducers: Define how to merge state updates

## Conditional Edges

Route based on state:

```python
def should_continue(state: AgentState) -> str:
    """Decide next step based on state"""
    if state.get("error"):
        return "handle_error"
    elif state.get("complete"):
        return END
    else:
        return "continue_processing"

workflow.add_conditional_edges(
    "process",
    should_continue,
    {
        "handle_error": "error_handler",
        "continue_processing": "next_step",
        END: END,
    }
)
```

## Human-in-the-Loop

Pause workflow for human input:

```python
from langgraph.checkpoint.memory import MemorySaver

workflow.add_node("human_review", human_review_node)
workflow.add_edge("process", "human_review")

app = workflow.compile(checkpointer=MemorySaver())

# Execute until human review
result = app.invoke(input_data, config={"configurable": {"thread_id": "123"}})

# Human provides feedback
feedback = get_human_feedback()

# Resume with feedback
result = app.invoke(
    {"feedback": feedback},
    config={"configurable": {"thread_id": "123"}}
)
```

## Streaming

Stream intermediate results:

```python
# Stream events
for event in app.stream(input_data):
    print(f"Node: {event['node']}")
    print(f"State: {event['state']}")

# Stream with updates
for chunk in app.stream(input_data, stream_mode="updates"):
    print(chunk)
```

## Memory Management

### In-Memory Checkpointing

For development and testing:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

### Persistent Checkpointing

For production (see `memory/checkpoint.py`):

```python
from aimq.memory.checkpoint import SupabaseCheckpointer

checkpointer = SupabaseCheckpointer(
    supabase_client=client,
    table_name="checkpoints"
)
app = workflow.compile(checkpointer=checkpointer)
```

## Decorators

AIMQ provides decorators for agents and workflows:

### Agent Decorator

```python
from aimq.agents.decorators import agent

@agent(
    name="my_agent",
    tools=[ImageOCR(), ReadRecord()],
    system_prompt="You are a helpful assistant"
)
def my_agent_logic(state: AgentState) -> AgentState:
    # Custom agent logic
    return state
```

### Workflow Decorator

```python
from aimq.workflows.decorators import workflow

@workflow(name="my_workflow")
def my_workflow_logic(state: WorkflowState) -> WorkflowState:
    # Custom workflow logic
    return state
```

## Best Practices

### 1. Keep Nodes Small
```python
# ✅ Good: Small, focused nodes
def extract_text(state: State) -> State:
    state["text"] = ocr_tool.run(state["image"])
    return state

def chunk_text(state: State) -> State:
    state["chunks"] = split_text(state["text"])
    return state

# ❌ Bad: Large, monolithic node
def process_document(state: State) -> State:
    # 100+ lines of logic
    ...
```

### 2. Use Type Hints
```python
# ✅ Good: Type hints for state
class MyState(TypedDict):
    input: str
    result: dict | None

def node(state: MyState) -> MyState:
    return state

# ❌ Bad: No type hints
def node(state):
    return state
```

### 3. Handle Errors Gracefully
```python
# ✅ Good: Error handling in nodes
def process_node(state: State) -> State:
    try:
        result = risky_operation(state["input"])
        state["result"] = result
    except Exception as e:
        state["error"] = str(e)
        state["status"] = "failed"
    return state

# Add conditional edge for error handling
workflow.add_conditional_edges(
    "process_node",
    lambda s: "error_handler" if s.get("error") else "next_step"
)
```

### 4. Use Checkpointing for Long Workflows
```python
# ✅ Good: Checkpoint for resumability
app = workflow.compile(checkpointer=MemorySaver())

result = app.invoke(
    input_data,
    config={"configurable": {"thread_id": "unique-id"}}
)

# ❌ Bad: No checkpointing for long workflow
app = workflow.compile()  # Lost if crashes
```

## Common Patterns

### Pattern: Agent Loop
```python
def agent_loop(state: AgentState) -> AgentState:
    """Agent reasoning loop"""
    # 1. Reason about next action
    action = agent.plan(state)

    # 2. Execute action
    result = execute_action(action, state)

    # 3. Update state
    state["messages"].append(result)
    state["iteration"] += 1

    return state

def should_continue(state: AgentState) -> str:
    if state["iteration"] >= MAX_ITERATIONS:
        return END
    if state.get("task_complete"):
        return END
    return "agent_loop"

workflow.add_node("agent_loop", agent_loop)
workflow.add_conditional_edges("agent_loop", should_continue)
```

### Pattern: Parallel Execution
```python
from langgraph.graph import StateGraph

def parallel_node_1(state: State) -> State:
    state["result1"] = process_1(state["input"])
    return state

def parallel_node_2(state: State) -> State:
    state["result2"] = process_2(state["input"])
    return state

def merge_results(state: State) -> State:
    state["final"] = combine(state["result1"], state["result2"])
    return state

workflow.add_node("parallel1", parallel_node_1)
workflow.add_node("parallel2", parallel_node_2)
workflow.add_node("merge", merge_results)

# Both run in parallel, then merge
workflow.add_edge("parallel1", "merge")
workflow.add_edge("parallel2", "merge")
```

### Pattern: Supervisor Pattern
```python
def supervisor(state: State) -> State:
    """Route to appropriate agent"""
    task_type = classify_task(state["input"])
    state["next_agent"] = task_type
    return state

def route_to_agent(state: State) -> str:
    return state["next_agent"]

workflow.add_node("supervisor", supervisor)
workflow.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {
        "researcher": "research_agent",
        "writer": "writing_agent",
        "reviewer": "review_agent",
    }
)
```

## Testing LangGraph Workflows

```python
def test_workflow():
    """Test workflow execution"""
    workflow = create_test_workflow()
    app = workflow.compile()

    result = app.invoke({"input": "test"})

    assert result["status"] == "success"
    assert "result" in result

def test_workflow_with_checkpointing():
    """Test workflow resumability"""
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    # First execution
    result1 = app.invoke(
        {"input": "test"},
        config={"configurable": {"thread_id": "test-123"}}
    )

    # Resume execution
    result2 = app.invoke(
        {"continue": True},
        config={"configurable": {"thread_id": "test-123"}}
    )

    assert result2["state_preserved"]
```

## Related

- See `agents/` for agent implementations
- See `workflows/` for workflow implementations
- See `memory/checkpoint.py` for checkpoint management
- See `architecture/langchain-integration.md` for Runnable patterns

## Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
