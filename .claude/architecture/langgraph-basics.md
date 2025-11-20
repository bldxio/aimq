# LangGraph Basics

Core concepts and fundamentals of LangGraph for building stateful workflows.

## Overview

LangGraph enables building stateful, multi-step workflows with agents. It provides state management, checkpointing, and complex orchestration patterns.

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

## Related

- [@.claude/architecture/langgraph-aimq.md](./langgraph-aimq.md) - AIMQ's LangGraph usage
- [@.claude/architecture/langgraph-advanced.md](./langgraph-advanced.md) - Advanced features
- [@.claude/architecture/langgraph-integration.md](./langgraph-integration.md) - Complete guide
- [@.claude/architecture/langchain-integration.md](./langchain-integration.md) - LangChain Runnable patterns

## Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)

---

**Remember**: LangGraph is all about state—keep it simple, typed, and checkpointed! 🔄✨
