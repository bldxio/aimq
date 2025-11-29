# LangGraph in AIMQ

How AIMQ uses LangGraph for agents, workflows, and decorators.

## Agent Implementations

AIMQ provides two agent types using LangGraph:

### 1. ReAct Agent (`agents/react.py`)

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

### 2. Plan-Execute Agent (`agents/plan_execute.py`)

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

## Workflow Implementations

### 1. Multi-Agent Workflow (`workflows/multi_agent.py`)

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

### 2. Document Workflow (`workflows/document.py`)

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

- [@.claude/architecture/langgraph-basics.md](./langgraph-basics.md) - LangGraph fundamentals
- [@.claude/architecture/langgraph-advanced.md](./langgraph-advanced.md) - Advanced features
- [@.claude/architecture/langgraph-integration.md](./langgraph-integration.md) - Complete guide
- [src/aimq/agents/](../../src/aimq/agents/) - Agent implementations
- [src/aimq/workflows/](../../src/aimq/workflows/) - Workflow implementations
- [src/aimq/memory/checkpoint.py](../../src/aimq/memory/checkpoint.py) - Checkpoint management

---

**Remember**: AIMQ's patterns are battle-tested—use them as starting points! 🚀✨
