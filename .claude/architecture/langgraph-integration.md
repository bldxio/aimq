# LangGraph Integration

Complete guide to using LangGraph in AIMQ for stateful, multi-step workflows with agents.

## Overview

AIMQ uses LangGraph to build stateful, multi-step workflows with agents. LangGraph enables complex agent orchestration, memory management, and human-in-the-loop patterns.

This guide is split into focused topics:

- **[LangGraph Basics](./langgraph-basics.md)** - Core concepts, state management, checkpointing, best practices
- **[LangGraph in AIMQ](./langgraph-aimq.md)** - AIMQ's agents, workflows, decorators, and patterns
- **[LangGraph Advanced](./langgraph-advanced.md)** - Human-in-the-loop, streaming, advanced patterns

## Quick Reference

### Core Concepts
- **StateGraph** - Define workflows as state graphs
- **State Management** - Pass state between nodes
- **Checkpointing** - Persist state for resumability
- **Conditional Edges** - Route based on state
- **Type Hints** - Use TypedDict for state

### AIMQ Implementations
- **ReAct Agent** - Reasoning + Acting pattern
- **Plan-Execute Agent** - Planning + Execution pattern
- **Multi-Agent Workflow** - Orchestrate specialized agents
- **Document Workflow** - Process documents through stages

### Advanced Features
- **Human-in-the-Loop** - Pause for human input
- **Streaming** - Stream intermediate results
- **Memory Management** - In-memory or persistent checkpointing
- **Advanced Patterns** - Retry, fan-out/fan-in, dynamic routing

## Getting Started

### 1. Learn the Basics
Start with [@.claude/architecture/langgraph-basics.md](./langgraph-basics.md) to understand:
- How to create StateGraphs
- State management and types
- Checkpointing for persistence
- Best practices

### 2. Explore AIMQ's Usage
See [@.claude/architecture/langgraph-aimq.md](./langgraph-aimq.md) for:
- Agent implementations (ReAct, Plan-Execute)
- Workflow implementations (Multi-Agent, Document)
- Decorators and patterns
- Testing workflows

### 3. Advanced Features
Check [@.claude/architecture/langgraph-advanced.md](./langgraph-advanced.md) for:
- Human-in-the-loop patterns
- Streaming results
- Complex routing and refinement
- Performance optimization

## Common Use Cases

### Build a Simple Agent
```python
from aimq.agents.react import create_react_agent

agent = create_react_agent(
    llm=llm,
    tools=[ImageOCR(), ReadRecord()],
    system_prompt="You are a helpful assistant"
)

result = agent.invoke({"input": "Extract text from image.jpg"})
```

### Build a Multi-Agent Workflow
```python
from aimq.workflows.multi_agent import create_multi_agent_workflow

workflow = create_multi_agent_workflow(
    agents={
        "researcher": research_agent,
        "writer": writing_agent,
    }
)

result = workflow.invoke({"task": "Write article about AI"})
```

### Add Checkpointing
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

result = app.invoke(
    input_data,
    config={"configurable": {"thread_id": "conversation-123"}}
)
```

## Related

- [@.claude/architecture/langchain-integration.md](./langchain-integration.md) - LangChain Runnable patterns
- [@.claude/patterns/error-handling.md](../patterns/error-handling.md) - Error handling patterns
- [@.claude/patterns/testing-strategy.md](../patterns/testing-strategy.md) - Testing strategies
- [src/aimq/agents/](../../src/aimq/agents/) - Agent implementations
- [src/aimq/workflows/](../../src/aimq/workflows/) - Workflow implementations

## Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)

---

**Remember**: LangGraph makes complex workflows manageable—start simple and build up! 🚀✨
