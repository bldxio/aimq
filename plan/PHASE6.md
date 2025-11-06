# Phase 6: Documentation

**Status**: ⏳ Not Started
**Priority**: 2 (High)
**Estimated**: 3-4 hours
**Dependencies**: Phases 1-5 (Complete)

---

## Objectives

Create comprehensive documentation for LangGraph integration:
1. Main LangGraph user guide
2. Agents user guide
3. Workflows user guide
4. API reference documentation

---

## Implementation Steps

### 6.1 LangGraph User Guide (1-1.5 hours)

**File**: `docs/user-guide/langgraph.md`

**Content Outline**:

```markdown
# LangGraph Integration

## Overview

AIMQ's LangGraph integration provides advanced stateful workflows and agents using a decorator-based architecture.

### Key Features

- **@workflow and @agent decorators** for reusable components
- **Built-in agents** (ReAct, Plan-Execute) and **workflows** (Document Processing, Multi-Agent)
- **LangChain LLM integration** - use any LangChain-compatible LLM
- **Three-level configuration** - defaults, factory overrides, job-level overrides
- **Built-in checkpointing** - resumable workflows with Supabase
- **Security controls** - whitelisted LLM overrides, controlled prompts

## Quick Start

[Installation, basic usage, first agent/workflow]

## Architecture

### Decorator Pattern

[Explain @workflow and @agent decorators, factory pattern]

### Three-Level Configuration

#### Level 1: Decorator Defaults
[Code example]

#### Level 2: Factory Overrides
[Code example]

#### Level 3: Job-Level Overrides
[Code example with security explanation]

## Using Built-in Agents

### ReActAgent

[Complete example with all options]

### PlanExecuteAgent

[Complete example with all options]

## Using Built-in Workflows

### DocumentWorkflow

[Complete example]

### MultiAgentWorkflow

[Complete example]

## Creating Custom Agents

[Step-by-step guide with @agent decorator]

## Creating Custom Workflows

[Step-by-step guide with @workflow decorator]

## Checkpointing & State Management

### Enabling Checkpointing

[Setup instructions, schema setup]

### Thread IDs for Resumable Workflows

[Example with thread_id]

### State Classes

[AgentState, WorkflowState, custom states]

## Security

### Job-Level Override Controls

[allowed_llms, allow_system_prompt explanation]

### Tool Input Validation

[How validation works, what it prevents]

## Configuration Reference

[All environment variables, config fields]

## Best Practices

- Use checkpointing for long-running workflows
- Validate tool inputs for security
- Set max_iterations to prevent infinite loops
- Use logger for debugging
- Test locally before deploying

## Troubleshooting

[Common issues and solutions]
```

**Action**: Write complete documentation with working code examples

---

### 6.2 Agents User Guide (45 minutes)

**File**: `docs/user-guide/agents.md`

**Content Outline**:

```markdown
# Agents Guide

## What Are Agents?

[Explanation of agent pattern, when to use]

## Built-in Agents

### ReActAgent

**Pattern**: Reasoning + Acting

[Complete example, configuration options, use cases]

### PlanExecuteAgent

**Pattern**: Planning then execution

[Complete example, configuration options, use cases]

## Creating Custom Agents

### Using @agent Decorator

[Step-by-step tutorial]

### Agent State

[Required fields, optional fields, custom state]

### Implementing Nodes

[Node function signature, state updates, error handling]

### Adding Tools

[Tool integration, validation]

### LLM Integration

[Using different LLMs, temperature, prompts]

## Configuration Options

### Tools
[List of BaseTool, validation]

### System Prompt
[Instructions, persona]

### LLM
[Model selection, temperature]

### Memory
[Checkpointing, thread_id]

### Reply Function
[Default behavior, custom callbacks]

### Security Controls
[allowed_llms, allow_system_prompt]

## Advanced Topics

### Multi-turn Conversations
[Managing message history]

### Tool Output Processing
[Handling tool results]

### Error Handling
[Errors list, recovery]

### Performance Tuning
[max_iterations, temperature]

## Examples

[Link to examples directory]

## API Reference

[Link to API docs]
```

---

### 6.3 Workflows User Guide (45 minutes)

**File**: `docs/user-guide/workflows.md`

**Content Outline**:

```markdown
# Workflows Guide

## What Are Workflows?

[Explanation of workflow pattern, when to use vs agents]

## Built-in Workflows

### DocumentWorkflow

**Pattern**: Multi-step document processing

[Complete example, features, use cases]

### MultiAgentWorkflow

**Pattern**: Supervisor-agent collaboration

[Complete example, features, use cases]

## Creating Custom Workflows

### Using @workflow Decorator

[Step-by-step tutorial]

### Workflow State

[Custom state classes, required fields]

### Implementing Nodes

[Node functions, state updates]

### Conditional Routing

[Conditional edges, routing logic]

### Linear Pipelines vs Branching

[Examples of both patterns]

## Configuration Options

### State Class
[TypedDict definitions]

### Checkpointer
[Enable/disable persistence]

## Advanced Topics

### Sub-workflows
[Composing workflows]

### Error Handling
[Error collection, recovery]

### Checkpointing Long Workflows
[Resume from interruption]

## Examples

[Link to examples directory]

## API Reference

[Link to API docs]
```

---

### 6.4 API Reference (1 hour)

**File**: `docs/api/langgraph.md`

**Content Outline**:

```markdown
# LangGraph API Reference

## Decorators

### @workflow

```python
@workflow(
    state_class: type[dict] | None = None,
    checkpointer: bool = False,
)
```

[Full parameter documentation, returns, examples]

### @agent

```python
@agent(
    tools: List[BaseTool] | None = None,
    system_prompt: str | None = None,
    llm: BaseChatModel | str | None = None,
    temperature: float = 0.1,
    memory: bool = False,
    state_class: type[dict] | None = None,
    reply_function: Callable[[str, dict], None] | None = None,
    allowed_llms: Dict[str, BaseChatModel] | None = None,
    allow_system_prompt: bool = False,
)
```

[Full parameter documentation, returns, examples]

## Built-in Agents

### ReActAgent

[Class signature, parameters, methods, examples]

### PlanExecuteAgent

[Class signature, parameters, methods, examples]

## Built-in Workflows

### DocumentWorkflow

[Class signature, parameters, methods, examples]

### MultiAgentWorkflow

[Class signature, parameters, methods, examples]

## State Classes

### AgentState

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add]
    tools: list[str]
    iteration: int
    errors: Annotated[list[str], add]
    current_tool: NotRequired[str]
    tool_input: NotRequired[dict]
    tool_output: NotRequired[Any]
    final_answer: NotRequired[str]
    thread_id: NotRequired[str]
    checkpoint_id: NotRequired[str]
    tenant_id: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]
```

[Field descriptions]

### WorkflowState

[Class definition, field descriptions]

## Utility Functions

### resolve_llm()

[Signature, parameters, returns, raises, examples]

### get_default_llm()

[Signature, parameters, returns, examples]

### default_reply_function()

[Signature, parameters, behavior, examples]

## Exception Types

### LangGraphError
[Base exception]

### GraphBuildError
[When raised, examples]

### GraphCompileError
[When raised, examples]

### StateValidationError
[When raised, examples]

### CheckpointerError
[When raised, examples]

### OverrideSecurityError
[When raised, examples]

### LLMResolutionError
[When raised, examples]

### ToolValidationError
[When raised, examples]

## Checkpointing

### get_checkpointer()

[Signature, returns, raises, examples]

## Tool Validation

### ToolInputValidator

[Class signature, methods, examples]
```

**Action**: Write complete API reference with type signatures and examples

---

## Definition of Done

### Documentation Complete

- [ ] `docs/user-guide/langgraph.md` written
- [ ] `docs/user-guide/agents.md` written
- [ ] `docs/user-guide/workflows.md` written
- [ ] `docs/api/langgraph.md` written

### Content Quality

- [ ] All code examples tested and working
- [ ] All links functional
- [ ] No broken references
- [ ] Consistent formatting

### Technical Accuracy

- [ ] All API signatures match implementation
- [ ] All configuration options documented
- [ ] All exception types documented
- [ ] Security features explained

### Build & Deploy

- [ ] MkDocs builds without errors
- [ ] Documentation viewable locally (`just docs-serve`)
- [ ] All pages linked in navigation
- [ ] Search indexing works

---

## Testing Documentation

### Build Test

```bash
# Test MkDocs build
just docs-build

# Serve locally
just docs-serve

# Visit http://localhost:8000
# Check all LangGraph pages
```

### Link Check

```bash
# Check for broken links (if tool available)
find docs -name "*.md" -exec grep -H "\[.*\](.*)" {} \;
```

### Code Example Validation

Test all code examples from documentation:

```bash
# Extract code blocks
# Run each example
# Verify no errors
```

---

## Common Pitfalls

### Outdated Code Examples

**Pitfall**: Documentation examples don't match actual API

**Solution**: Copy-paste from working examples, test all code

### Missing Type Annotations

**Pitfall**: API reference without type signatures

**Solution**: Include full signatures from source
```python
# Good
def resolve_llm(
    llm_param: BaseChatModel | str | None,
    default_model: str = "mistral-large-latest"
) -> BaseChatModel:

# Bad
def resolve_llm(llm_param, default_model):
```

### Broken Internal Links

**Pitfall**: Links to non-existent pages

**Solution**: Use relative paths, verify all exist
```markdown
# Good
See [Agents Guide](./agents.md)

# Bad
See [Agents Guide](agents.md)  # May not work
```

---

## Next Phase

Once Phase 6 is complete:
- [ ] Update PROGRESS.md
- [ ] Move to **Phase 7: Testing** ([PHASE7.md](./PHASE7.md))

---

**Phase Owner**: Documentation Team
**Started**: ___________
**Completed**: ___________
**Actual Hours**: ___________
