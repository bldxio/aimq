# LangGraph Advanced Features

Advanced LangGraph features: human-in-the-loop, streaming, and complex patterns.

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

## Advanced Patterns

### Pattern: Multi-Stage Pipeline

```python
def stage1(state: State) -> State:
    state["stage1_result"] = process_stage1(state["input"])
    return state

def stage2(state: State) -> State:
    state["stage2_result"] = process_stage2(state["stage1_result"])
    return state

def stage3(state: State) -> State:
    state["final_result"] = process_stage3(state["stage2_result"])
    return state

workflow.add_node("stage1", stage1)
workflow.add_node("stage2", stage2)
workflow.add_node("stage3", stage3)

workflow.add_edge("stage1", "stage2")
workflow.add_edge("stage2", "stage3")
workflow.add_edge("stage3", END)
```

### Pattern: Retry with Backoff

```python
def process_with_retry(state: State) -> State:
    max_retries = 3
    attempt = state.get("attempt", 0)

    try:
        result = risky_operation(state["input"])
        state["result"] = result
        state["status"] = "success"
    except Exception as e:
        state["error"] = str(e)
        state["attempt"] = attempt + 1

        if attempt < max_retries:
            state["status"] = "retry"
        else:
            state["status"] = "failed"

    return state

def should_retry(state: State) -> str:
    if state["status"] == "retry":
        return "process_with_retry"
    elif state["status"] == "success":
        return END
    else:
        return "error_handler"

workflow.add_node("process_with_retry", process_with_retry)
workflow.add_conditional_edges("process_with_retry", should_retry)
```

### Pattern: Fan-Out/Fan-In

```python
def fan_out(state: State) -> State:
    """Split work into parallel tasks"""
    state["tasks"] = split_into_tasks(state["input"])
    return state

def process_task_1(state: State) -> State:
    state["result1"] = process(state["tasks"][0])
    return state

def process_task_2(state: State) -> State:
    state["result2"] = process(state["tasks"][1])
    return state

def process_task_3(state: State) -> State:
    state["result3"] = process(state["tasks"][2])
    return state

def fan_in(state: State) -> State:
    """Combine results from parallel tasks"""
    state["final_result"] = combine([
        state["result1"],
        state["result2"],
        state["result3"]
    ])
    return state

workflow.add_node("fan_out", fan_out)
workflow.add_node("task1", process_task_1)
workflow.add_node("task2", process_task_2)
workflow.add_node("task3", process_task_3)
workflow.add_node("fan_in", fan_in)

# Fan out to parallel tasks
workflow.add_edge("fan_out", "task1")
workflow.add_edge("fan_out", "task2")
workflow.add_edge("fan_out", "task3")

# Fan in to combine results
workflow.add_edge("task1", "fan_in")
workflow.add_edge("task2", "fan_in")
workflow.add_edge("task3", "fan_in")
```

### Pattern: Dynamic Routing

```python
def dynamic_router(state: State) -> State:
    """Analyze input and determine routing"""
    analysis = analyze_input(state["input"])
    state["route"] = analysis["recommended_route"]
    state["confidence"] = analysis["confidence"]
    return state

def route_decision(state: State) -> str:
    """Decide which path to take"""
    if state["confidence"] > 0.8:
        return state["route"]
    else:
        return "human_review"

workflow.add_node("router", dynamic_router)
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "path_a": "process_a",
        "path_b": "process_b",
        "path_c": "process_c",
        "human_review": "human_review_node",
    }
)
```

### Pattern: Iterative Refinement

```python
def generate_draft(state: State) -> State:
    state["draft"] = generate(state["input"])
    state["iteration"] = 0
    return state

def review_draft(state: State) -> State:
    review = evaluate(state["draft"])
    state["review"] = review
    state["score"] = review["score"]
    return state

def refine_draft(state: State) -> State:
    state["draft"] = refine(state["draft"], state["review"])
    state["iteration"] += 1
    return state

def should_continue_refining(state: State) -> str:
    if state["score"] >= 0.9:
        return END
    elif state["iteration"] >= 5:
        return END
    else:
        return "review_draft"

workflow.add_node("generate", generate_draft)
workflow.add_node("review", review_draft)
workflow.add_node("refine", refine_draft)

workflow.add_edge("generate", "review")
workflow.add_conditional_edges(
    "review",
    should_continue_refining,
    {
        "review_draft": "refine",
        END: END
    }
)
workflow.add_edge("refine", "review")
```

## Advanced State Management

### State Reducers

Custom logic for merging state updates:

```python
from typing import Annotated

def merge_lists(existing: list, new: list) -> list:
    """Custom reducer: merge and deduplicate"""
    return list(set(existing + new))

class AdvancedState(TypedDict):
    items: Annotated[list, merge_lists]
    metadata: dict

def node1(state: AdvancedState) -> AdvancedState:
    state["items"] = ["a", "b"]
    return state

def node2(state: AdvancedState) -> AdvancedState:
    state["items"] = ["b", "c"]  # Will merge with existing
    return state

# Final state["items"] = ["a", "b", "c"]
```

### Nested State

Complex state structures:

```python
class SubState(TypedDict):
    value: str
    timestamp: float

class ComplexState(TypedDict):
    main_data: str
    sub_states: dict[str, SubState]
    history: list[dict]

def process_complex(state: ComplexState) -> ComplexState:
    state["sub_states"]["task1"] = {
        "value": "completed",
        "timestamp": time.time()
    }
    state["history"].append({
        "action": "processed",
        "timestamp": time.time()
    })
    return state
```

## Performance Optimization

### Lazy Loading

```python
def lazy_load_node(state: State) -> State:
    """Only load data when needed"""
    if "heavy_data" not in state:
        state["heavy_data"] = load_heavy_data()
    return state
```

### Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(input_data: str) -> dict:
    """Cache expensive computations"""
    return compute_result(input_data)

def cached_node(state: State) -> State:
    state["result"] = expensive_operation(state["input"])
    return state
```

## Related

- [@.claude/architecture/langgraph-basics.md](./langgraph-basics.md) - LangGraph fundamentals
- [@.claude/architecture/langgraph-aimq.md](./langgraph-aimq.md) - AIMQ's usage
- [@.claude/architecture/langgraph-integration.md](./langgraph-integration.md) - Complete guide
- [@.claude/patterns/error-handling.md](../patterns/error-handling.md) - Error handling patterns

## Resources

- [LangGraph Advanced Patterns](https://langchain-ai.github.io/langgraph/concepts/advanced/)
- [Human-in-the-Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [Streaming](https://langchain-ai.github.io/langgraph/concepts/streaming/)

---

**Remember**: Advanced features are powerful, but start simple and add complexity only when needed! 🎯✨
