# Module Organization Pattern

## Overview

AIMQ uses a modular architecture where each top-level module has a clear, single responsibility. This pattern emerged from refactoring the monolithic `langgraph/` module into focused components.

## Structure

```
src/aimq/
├── agents/          # Agent implementations and agent-specific logic
├── workflows/       # Workflow implementations and workflow-specific logic
├── common/          # Shared utilities used across multiple modules
├── memory/          # Memory and checkpoint management
├── clients/         # External service clients
├── providers/       # Queue provider implementations
├── tools/           # LangChain tools
└── *.py             # Core components (worker, queue, job, config)
```

## Decision Tree: Where Does This Code Go?

### Is it agent-specific logic?
- **YES** → `agents/`
  - Examples: ReAct agent, Plan-Execute agent, agent decorators, agent states, agent validation

### Is it workflow-specific logic?
- **YES** → `workflows/`
  - Examples: Multi-agent workflow, document workflow, workflow decorators, workflow states

### Is it used by both agents AND workflows?
- **YES** → `common/`
  - Examples: LLM utilities, custom exceptions, shared decorators

### Is it about memory/checkpoints?
- **YES** → `memory/`
  - Examples: Checkpoint managers, memory stores, persistence logic

### Is it a client for an external service?
- **YES** → `clients/`
  - Examples: Supabase client, Mistral client

### Is it a queue provider implementation?
- **YES** → `providers/`
  - Examples: SupabaseQueueProvider, custom queue implementations

### Is it a LangChain tool?
- **YES** → `tools/`
  - Examples: OCR tools, PDF tools, Supabase tools

### Is it core infrastructure?
- **YES** → Root level (`src/aimq/*.py`)
  - Examples: Worker, Queue, Job, Config, Attachment

## Module Responsibilities

### agents/
**Purpose**: Agent implementations and agent-specific utilities

**Contains**:
- `base.py` - Base agent classes
- `react.py` - ReAct agent implementation
- `plan_execute.py` - Plan-Execute agent implementation
- `decorators.py` - Agent-specific decorators
- `states.py` - Agent state models
- `validation.py` - Agent validation logic

**Does NOT contain**: Workflow logic, shared utilities, memory management

### workflows/
**Purpose**: Workflow implementations and workflow-specific utilities

**Contains**:
- `base.py` - Base workflow classes
- `multi_agent.py` - Multi-agent workflow
- `document.py` - Document processing workflow
- `decorators.py` - Workflow-specific decorators
- `states.py` - Workflow state models

**Does NOT contain**: Agent logic, shared utilities, memory management

### common/
**Purpose**: Shared utilities used across multiple modules

**Contains**:
- `llm.py` - LLM utilities (model initialization, configuration)
- `exceptions.py` - Custom exception classes
- Shared decorators (if used by both agents and workflows)
- Shared utilities (if used by both agents and workflows)

**Does NOT contain**: Module-specific logic (agents, workflows, memory)

### memory/
**Purpose**: Memory and checkpoint management

**Contains**:
- `checkpoint.py` - Checkpoint managers
- Memory stores
- Persistence logic

**Does NOT contain**: Agent logic, workflow logic, business logic

## Anti-Patterns to Avoid

### ❌ Circular Dependencies
```python
# BAD: agents/ importing from workflows/
from aimq.workflows.base import WorkflowBase  # in agents/base.py
```

**Solution**: Extract shared code to `common/`

### ❌ Duplicated Code
```python
# BAD: Same utility in agents/ and workflows/
# agents/utils.py
def format_prompt(text): ...

# workflows/utils.py
def format_prompt(text): ...  # Duplicate!
```

**Solution**: Move to `common/` and import from both

### ❌ Module Bloat
```python
# BAD: agents/ containing workflow logic
# agents/document_workflow.py  # This is workflow logic!
```

**Solution**: Move to appropriate module (`workflows/`)

### ❌ Unclear Boundaries
```python
# BAD: Memory logic in agents/
# agents/checkpoint_manager.py  # This is memory logic!
```

**Solution**: Move to `memory/` module

## Migration Pattern

When refactoring code into modules:

1. **Identify the primary concern** (agent, workflow, shared, memory)
2. **Move the file** to the appropriate module
3. **Update imports** throughout the codebase
4. **Extract shared code** to `common/` if needed
5. **Update tests** to mirror the new structure
6. **Update documentation** (CLAUDE.md, agents.md)

## Real-World Example: Refactoring langgraph/

From commit c28cc52 (2025-11-12):

**Problem**: Monolithic `langgraph/` module with mixed concerns

**Before**:
```
src/aimq/langgraph/
├── agents.py          # Mixed agent implementations
├── workflows.py       # Mixed workflow implementations
├── decorators.py      # Mixed decorators
├── states.py          # Mixed states
├── validation.py      # Validation logic
├── memory.py          # Memory logic
└── utils.py           # Mixed utilities
```

**After**:
```
src/aimq/
├── agents/
│   ├── base.py        # From langgraph/agents.py
│   ├── react.py       # From langgraph/agents.py
│   ├── plan_execute.py # From langgraph/agents.py
│   ├── decorators.py  # Agent-specific from langgraph/decorators.py
│   ├── states.py      # Agent-specific from langgraph/states.py
│   └── validation.py  # From langgraph/validation.py
├── workflows/
│   ├── base.py        # From langgraph/workflows.py
│   ├── multi_agent.py # From langgraph/workflows.py
│   ├── document.py    # From langgraph/workflows.py
│   ├── decorators.py  # Workflow-specific from langgraph/decorators.py
│   └── states.py      # Workflow-specific from langgraph/states.py
├── common/
│   ├── llm.py         # Shared from langgraph/utils.py
│   └── exceptions.py  # Shared from langgraph/utils.py
└── memory/
    └── checkpoint.py  # From langgraph/memory.py
```

**Result**:
- Clearer module boundaries
- Easier to find code
- Better test organization
- Reduced coupling
- Easier to extend

## Benefits

1. **Clear boundaries**: Each module has a single, well-defined purpose
2. **Easy navigation**: Developers know exactly where to find code
3. **Reduced coupling**: Modules depend on `common/`, not each other
4. **Better testing**: Test structure mirrors source structure
5. **Scalability**: Easy to add new agents or workflows without bloat

## Related

- See `standards/code-organization.md` for file-level organization
- See `architecture/aimq-modules.md` for detailed module documentation
