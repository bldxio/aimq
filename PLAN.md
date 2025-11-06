# LangGraph Integration Plan for AIMQ

**Status**: In Progress
**Started**: 2025-10-30
**Target Version**: 0.2.0
**Architecture**: Decorator-Based with Built-in Workflows & Agents + LangChain LLM Integration

## Overview

Add advanced LangGraph v1.0 support to AIMQ using a decorator-based architecture that provides:
1. **`@workflow` and `@agent` decorators** - Define reusable LangGraph components
2. **Built-in workflows & agents** - Pre-built patterns (ReAct, Plan-Execute, Document Pipeline, Multi-Agent)
3. **LangChain LLM integration** - Leverage full LangChain ecosystem for flexible LLM usage
4. **Three-level configuration** - Decorator defaults → Factory overrides → Job-level overrides (with security)
5. **Reply function** - Built-in response handling via queue or custom callback
6. **Existing `worker.assign()`** - Use familiar AIMQ pattern to register workflows to queues

### Goals

1. **Developer Experience**: Simple, declarative API for complex workflows
2. **Built-in Patterns**: Production-ready agents and workflows out-of-the-box
3. **Flexibility**: Support any LangChain-compatible LLM (Mistral, OpenAI, Anthropic, etc.)
4. **Security**: Controlled job-level overrides with explicit whitelisting
5. **Customization**: Users can configure built-ins or create custom workflows/agents
6. **Seamless Integration**: Works naturally with existing AIMQ architecture

### Target Users

- AI engineers building multi-agent systems
- Data scientists creating document processing pipelines
- Developers needing stateful, resumable workflows
- Teams building production RAG and agentic applications

---

## Applied Fixes Summary

**Date**: 2025-10-30
**Status**: Critical fixes applied to PLAN.md

The following critical fixes from PLAN_FIXES.md have been applied to this document:

### ✅ Completed Fixes

1. **BaseAgent Naming Collision** (#1) - Renamed internal classes to `_AgentBase` and `_WorkflowBase`
2. **Type Annotations** (#2) - Fixed `Type[TypedDict]` → `type[dict]` throughout decorators
3. **NotRequired in States** (#3) - Added proper `NotRequired` markers to optional state fields
4. **Missing _resolve_llm()** (#4) - Added comprehensive LLM resolution helper with error handling
5. **Missing Config Fields** (#5) - Added `mistral_model` and LangGraph config fields
6. **Override Validation** (#6) - Complete rewrite with type validation, range checking, logging
7. **Checkpointer Connection** (#7) - Fixed regex crash, added URL encoding, validation
8. **Checkpointer Error Handling** (#8) - Replaced bare `except: pass` with proper error handling
9. **Reply Function Errors** (#9) - Added comprehensive error handling to `default_reply_function`
10. **Exception Types** (#10) - Created `exceptions.py` module with all custom exception types

### 📋 Remaining Tasks (Before Phase 1 Implementation)

The following items should be addressed during Phase 1 implementation:

- **Logger Integration** (#11) - Add logger parameter to decorators (implement in code)
- **Tool Validation** (#12) - Add `validation.py` module (implement in code)
- **Dependency Verification** (#13) - Verify actual PyPI package versions before `uv add`
- **Configuration Validation** (#14) - Add `validate_agent_config()` function (implement in code)

### Key Improvements

- **Type Safety**: All type annotations now properly use `type[dict]` and `NotRequired`
- **Security**: Enhanced override validation with whitelist checking and type validation
- **Error Handling**: Comprehensive error handling throughout with specific exception types
- **Logging**: Proper logging integration with context and debug information
- **Robustness**: URL encoding, regex safety, connection string validation

---

## Revised Architecture

### Decorator Pattern with LangChain Integration

```python
# Using built-in agent with LangChain LLM
from aimq.worker import Worker
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile
from aimq.tools.ocr import ImageOCR
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

worker = Worker()

# Create configured agent instance (factory pattern)
agent = ReActAgent(
    tools=[ReadFile(), ImageOCR()],
    system_prompt="You are a document processing assistant",
    llm=ChatMistralAI(model="mistral-large-latest"),  # LangChain LLM object
    temperature=0.1,
    memory=True,  # Enable checkpointing
    # Job-level overrides with security
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
        "gpt4": ChatOpenAI(model="gpt-4o"),
    },
    allow_system_prompt=True,  # Allow job to customize prompt
    # reply_function defaults to enqueue to "process_agent_response"
)

# Assign to queue using existing pattern
worker.assign(agent, queue="doc-agent", timeout=900)
```

```python
# Creating custom agent with decorator
from aimq.langgraph import agent
from langgraph.graph import StateGraph
from langchain_mistralai import ChatMistralAI

@agent(
    tools=[ReadFile(), WriteRecord()],
    system_prompt="You are a custom agent",
    llm=ChatMistralAI(model="mistral-large-latest"),
    memory=True
)
def custom_agent(graph: StateGraph, config: dict) -> StateGraph:
    """Define custom agent logic."""
    # config contains: tools, system_prompt, llm, temperature, memory, reply_function, etc.

    def reasoning_node(state):
        # Access LangChain LLM from config
        llm = config["llm"]
        response = llm.invoke(state["messages"])

        # Send intermediate update via reply_function
        if config["reply_function"]:
            config["reply_function"]("Reasoning complete", {"step": "reason"})

        return {"messages": [response]}

    def tool_node(state):
        # Custom tool execution
        pass

    graph.add_node("reason", reasoning_node)
    graph.add_node("act", tool_node)
    graph.add_edge("reason", "act")
    graph.add_edge("act", "reason")
    graph.set_entry_point("reason")

    return graph

# Use the custom agent
worker = Worker()
my_agent = custom_agent()  # Returns configured instance
worker.assign(my_agent, queue="custom-agent")
```

### Module Structure (NEW)

```
src/aimq/
├── langgraph/
│   ├── __init__.py           # Export @workflow, @agent decorators
│   ├── decorators.py         # Decorator implementations
│   ├── base.py               # _AgentBase, _WorkflowBase classes (internal)
│   ├── checkpoint.py         # Supabase checkpoint store with proper error handling
│   ├── states.py             # AgentState, WorkflowState definitions (with NotRequired)
│   ├── utils.py              # LLM helpers (resolve_llm, get_default_llm, default_reply_function)
│   ├── exceptions.py         # Custom exception types (LLMResolutionError, CheckpointerError, etc.)
│   └── visualization.py      # Mermaid diagram generation
├── agents/                   # Built-in agents (using @agent decorator)
│   ├── __init__.py           # Export ReActAgent, PlanExecuteAgent
│   ├── react.py              # ReActAgent defined with @agent
│   └── plan_execute.py       # PlanExecuteAgent defined with @agent
├── workflows/                # Built-in workflows (using @workflow decorator)
│   ├── __init__.py           # Export DocumentWorkflow, MultiAgentWorkflow
│   ├── document.py           # DocumentWorkflow defined with @workflow
│   └── multi_agent.py        # MultiAgentWorkflow defined with @workflow
└── tools/
    └── docling/              # Docling tool wrappers
        ├── __init__.py
        └── converter.py
```

**Key Points:**
- `base.py` contains BaseAgent and BaseWorkflow classes used internally by decorators
- Built-in agents/workflows are defined using decorators (readable examples)
- Decorators wrap base classes to provide shared functionality (DRY)

### Examples Structure (NEW)

```
examples/langgraph/
├── README.md                      # Overview and usage guide
├── using_builtin_react.py         # Using ReActAgent
├── using_builtin_document.py      # Using DocumentWorkflow
├── using_builtin_plan_execute.py  # Using PlanExecuteAgent
├── using_builtin_multi_agent.py   # Using MultiAgentWorkflow
├── custom_agent_decorator.py      # Creating custom agent with @agent
└── custom_workflow_decorator.py   # Creating custom workflow with @workflow
```

### Three-Level Configuration System

Configuration priority (highest to lowest):

#### Level 1: Job Data (Runtime - Highest Priority)
Job data can override certain parameters if explicitly allowed:

```json
{
    "messages": [...],
    "llm": "small",           // If allowed_llms provided
    "system_prompt": "...",   // If allow_system_prompt=True
    "temperature": 0.7        // Always allowed (safe parameter)
}
```

**Security Controls:**
- `llm`: Only values in `allowed_llms` dict are accepted
- `system_prompt`: Only if `allow_system_prompt=True`
- `temperature`: Always allowed (safe numeric parameter)

#### Level 2: Factory Call (tasks.py - Medium Priority)
Override decorator defaults when instantiating:

```python
# tasks.py
from aimq.agents import ReActAgent
from langchain_mistralai import ChatMistralAI

agent = ReActAgent(
    # Override built-in defaults
    tools=[ReadFile(), ImageOCR()],
    system_prompt="You are a document specialist.",
    llm=ChatMistralAI(model="mistral-large-latest"),
    temperature=0.3,
    memory=True,
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
    },
    allow_system_prompt=True,
)
```

#### Level 3: Decorator Defaults (Built-in Definition - Lowest Priority)
Sensible defaults in the built-in agent/workflow definition:

```python
# src/aimq/agents/react.py
@agent(
    system_prompt="You are a helpful AI assistant.",
    temperature=0.1,
    memory=False,
    allow_system_prompt=False,  # Secure by default
)
def ReActAgent(graph, config):
    # Implementation
    pass
```

### Reply Function System

**Default Behavior:**
When `reply_function=None`, automatically uses `default_reply_function` which enqueues responses to `process_agent_response` queue:

```python
# src/aimq/langgraph/utils.py
def default_reply_function(message: str, metadata: dict) -> None:
    """Default: enqueue response to process_agent_response queue."""
    from aimq.providers.supabase import SupabaseQueueProvider
    from datetime import datetime

    provider = SupabaseQueueProvider()
    provider.send("process_agent_response", {
        "message": message,
        "metadata": metadata,
        "timestamp": datetime.now().isoformat(),
    })
```

**Custom Reply Function:**
Users can provide their own:

```python
def webhook_reply(message: str, metadata: dict) -> None:
    import requests
    requests.post("https://api.example.com/webhook", json={
        "message": message,
        "metadata": metadata,
    })

agent = ReActAgent(
    tools=[...],
    reply_function=webhook_reply,
)
```

**Usage in Nodes:**
```python
def reasoning_node(state):
    # Send intermediate update
    if config["reply_function"]:
        config["reply_function"](
            "Processing step 1 complete",
            {"step": 1, "status": "success"}
        )

    return state
```

---

## Implementation Phases

### Phase 0: Setup ✅ (DONE)

- [x] Create PLAN.md
- [x] Update .gitignore to exclude PLAN.md
- [x] Revise architecture based on feedback

### Phase 1: Core Decorators & Infrastructure (Priority 1)

#### 1.1 Dependencies

Add to `pyproject.toml`:

```toml
dependencies = [
    # ... existing ...
    "langgraph>=0.2.0,<0.3.0",
    "langgraph-checkpoint-postgres>=1.0.0,<2.0.0",
    "langchain-mistralai>=0.2.0,<0.3.0",
    "langchain-openai>=0.2.0,<0.3.0",  # For examples/flexibility
    "langchain-core>=0.3.0,<0.4.0",
    "docling>=2.58.0,<3.0.0",
]
```

**Rationale:**
- `langgraph` - Core StateGraph and workflow primitives
- `langgraph-checkpoint-postgres` - Supabase-compatible checkpointing
- `langchain-mistralai` - Mistral AI LLM integration (primary LLM)
- `langchain-openai` - OpenAI LLM integration (for examples showing flexibility)
- `langchain-core` - Core LangChain types (BaseChatModel, etc.)
- `docling` - Advanced document processing (PDF, DOCX, tables, OCR)

**Note**: Dependency versions need verification before implementation:
```bash
# Verify actual versions available on PyPI
uv add --dry-run langgraph
uv add --dry-run langgraph-checkpoint-postgres
uv add --dry-run langchain-mistralai
uv add --dry-run docling
```

Potential corrections (verify before use):
- `langgraph-checkpoint-postgres` may have different versioning (e.g., `>=0.0.12,<0.1.0`)
- `docling` version may be lower than 2.58.0 (check latest stable)
- See PLAN_FIXES.md #13 for details

#### 1.1.1 Configuration Fields

Add to `src/aimq/config.py`:

```python
class Config(BaseSettings):
    # ... existing fields ...

    # Mistral AI configuration
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    mistral_model: str = Field(
        default="mistral-large-latest",
        alias="MISTRAL_MODEL",
        description="Default Mistral model for LangGraph agents"
    )

    # LangGraph configuration
    langgraph_checkpoint_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_CHECKPOINT_ENABLED",
        description="Enable LangGraph checkpointing (requires schema setup)"
    )
    langgraph_max_iterations: int = Field(
        default=20,
        alias="LANGGRAPH_MAX_ITERATIONS",
        description="Maximum iterations for agent loops (safety limit)"
    )
```

#### 1.2 Decorator Implementation

**File**: `src/aimq/langgraph/decorators.py`

```python
"""
Decorators for defining LangGraph workflows and agents.
"""

from typing import Callable, Any, List, Dict
from functools import wraps
from langgraph.graph import StateGraph
from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel

def workflow(
    state_class: type[dict] | None = None,
    checkpointer: bool = False,
):
    """
    Decorator for defining reusable LangGraph workflows.

    Returns a factory function that creates configured workflow instances.

    Args:
        state_class: Optional TypedDict class defining workflow state
        checkpointer: Whether to enable state persistence (default: False)

    Example:
        @workflow(state_class=MyState, checkpointer=True)
        def my_workflow(graph: StateGraph, config: dict) -> StateGraph:
            graph.add_node("step1", lambda s: {"result": "done"})
            graph.add_edge("step1", END)
            graph.set_entry_point("step1")
            return graph

        # Use it
        worker = Worker()
        wf = my_workflow()  # Create instance
        worker.assign(wf, queue="my-queue")
    """
    def decorator(builder_func: Callable) -> Callable:
        @wraps(builder_func)
        def factory(**kwargs) -> Any:
            """Factory function that creates configured workflow instances."""
            from aimq.langgraph.base import _WorkflowBase

            # Merge config (decorator defaults + factory overrides)
            config = {
                "state_class": state_class,
                "checkpointer": checkpointer,
                **kwargs
            }

            # Use _WorkflowBase to handle compilation and execution
            return _WorkflowBase(builder_func, config)

        return factory

    return decorator


def agent(
    tools: List[BaseTool] | None = None,
    system_prompt: str | None = None,
    llm: BaseChatModel | str | None = None,
    temperature: float = 0.1,
    memory: bool = False,
    state_class: type[dict] | None = None,
    reply_function: Callable[[str, dict], None] | None = None,
    allowed_llms: Dict[str, BaseChatModel] | None = None,
    allow_system_prompt: bool = False,
):
    """
    Decorator for defining reusable LangGraph agents.

    Provides agent-specific features like tools, prompts, LLM config, memory, and security.
    Returns a factory function that creates configured agent instances.

    Args:
        tools: List of LangChain tools the agent can use
        system_prompt: Agent instructions/persona
        llm: LangChain LLM object, string (model name), or None for default
        temperature: LLM temperature (default: 0.1)
        memory: Enable conversation memory and checkpointing (default: False)
        state_class: Custom state class (must extend AgentState)
        reply_function: Callback for sending responses (default: enqueue to process_agent_response)
        allowed_llms: Dict mapping string keys to LangChain LLM objects for job-level overrides
        allow_system_prompt: Allow job data to override system_prompt (default: False, secure)

    Example:
        @agent(
            tools=[ReadFile(), ImageOCR()],
            system_prompt="You are a helpful assistant",
            llm=ChatMistralAI(model="mistral-large-latest"),
            memory=True,
            allowed_llms={
                "small": ChatMistralAI(model="mistral-small-latest"),
                "large": ChatMistralAI(model="mistral-large-latest"),
            },
            allow_system_prompt=True,
        )
        def my_agent(graph: StateGraph, config: dict) -> StateGraph:
            # config contains: tools, system_prompt, llm, temperature, memory,
            #                  reply_function, allowed_llms, allow_system_prompt

            def reasoning_node(state):
                # Access LangChain LLM
                llm = config["llm"]
                response = llm.invoke(state["messages"])

                # Send update via reply_function
                if config["reply_function"]:
                    config["reply_function"]("Step complete", {"step": 1})

                return {"messages": [response]}

            graph.add_node("reason", reasoning_node)
            graph.set_entry_point("reason")
            return graph

        # Use it
        worker = Worker()
        my_agent_instance = my_agent()  # Create configured instance
        worker.assign(my_agent_instance, queue="agent-queue")
    """
    def decorator(builder_func: Callable) -> Callable:
        @wraps(builder_func)
        def factory(**override_kwargs) -> Any:
            """Factory function that creates configured agent instances."""
            from aimq.langgraph.base import _AgentBase
            from aimq.langgraph.utils import resolve_llm, default_reply_function
            from aimq.langgraph.states import AgentState

            # Validate state_class if provided
            custom_state = override_kwargs.get("state_class", state_class)
            if custom_state and not issubclass(custom_state, AgentState):
                raise TypeError(f"state_class must be a subclass of AgentState, got {custom_state}")

            # Process LLM using resolve_llm helper
            llm_param = override_kwargs.get("llm", llm)
            llm_instance = resolve_llm(
                llm_param,
                default_model=override_kwargs.get("default_model", "mistral-large-latest")
            )

            # Merge config (decorator defaults + factory overrides)
            config = {
                "tools": tools or [],
                "system_prompt": system_prompt or "You are a helpful AI assistant.",
                "llm": llm_instance,
                "temperature": temperature,
                "memory": memory,
                "state_class": custom_state or AgentState,
                "reply_function": reply_function or default_reply_function,
                "allowed_llms": allowed_llms,
                "allow_system_prompt": allow_system_prompt,
                **override_kwargs
            }

            # Use _AgentBase to handle graph compilation, overrides, and execution
            return _AgentBase(builder_func, config)

        return factory

    return decorator
```

#### 1.3 Base Classes (Internal)

**File**: `src/aimq/langgraph/base.py`

```python
"""
Base classes used internally by decorators.
Provides shared functionality for graph compilation, override processing, and execution.

These classes are internal implementation details and should not be used directly.
"""

from typing import Callable, Any, Dict
from langgraph.graph import StateGraph
from langchain_core.language_models import BaseChatModel
import logging

logger = logging.getLogger(__name__)

class _AgentBase:
    """
    Internal base class used by @agent decorator.
    Handles graph compilation, job-level overrides, and Runnable interface.
    """

    def __init__(self, builder_func: Callable, config: Dict[str, Any]):
        """
        Initialize agent with builder function and configuration.

        Args:
            builder_func: Function that builds the StateGraph
            config: Configuration dict with tools, llm, prompts, etc.
        """
        self.builder_func = builder_func
        self.config = config
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the agent's StateGraph."""
        from langgraph.graph import StateGraph

        state_class = self.config.get("state_class")
        graph = StateGraph(state_class)

        # Call user's builder function
        return self.builder_func(graph, self.config)

    def _compile(self):
        """Compile graph with optional checkpointing."""
        from aimq.langgraph.checkpoint import get_checkpointer

        checkpointer = None
        if self.config.get("memory"):
            checkpointer = get_checkpointer()

        return self._graph.compile(checkpointer=checkpointer)

    def invoke(self, input: dict, config: dict | None = None):
        """
        Invoke the agent (implements Runnable interface).
        Processes job-level overrides before execution.
        """
        # Process job-level overrides with security checks
        runtime_input, runtime_config = self._process_overrides(input, config)
        return self._compiled.invoke(runtime_input, runtime_config)

    def stream(self, input: dict, config: dict | None = None):
        """Stream agent execution (implements Runnable interface)."""
        runtime_input, runtime_config = self._process_overrides(input, config)
        return self._compiled.stream(runtime_input, runtime_config)

    def _process_overrides(
        self, input: dict, config: dict | None
    ) -> tuple[dict, dict]:
        """Process job-level overrides with security validation.

        Allowed overrides:
        - llm: If key exists in allowed_llms dict (whitelist)
        - system_prompt: If allow_system_prompt=True (explicit opt-in)
        - temperature: Always allowed, range validated [0.0, 2.0]

        Args:
            input: Job input data (copied, not mutated)
            config: Runtime config (optional)

        Returns:
            Tuple of (processed_input, runtime_config)

        Raises:
            ValueError: If override values are severely invalid
        """
        import logging

        logger = logging.getLogger(__name__)

        runtime_config = config.copy() if config else {}
        processed_input = input.copy()

        # Track which overrides were applied
        applied_overrides = []

        # Override: LLM (security-controlled)
        if "llm" in processed_input:
            llm_key = processed_input.pop("llm")
            allowed_llms = self.config.get("allowed_llms")

            if not isinstance(llm_key, str):
                logger.warning(
                    f"LLM override must be string, got {type(llm_key).__name__}, ignoring"
                )
            elif not allowed_llms:
                logger.warning(
                    "LLM override attempted but allowed_llms not configured"
                )
            elif llm_key in allowed_llms:
                runtime_config["llm"] = allowed_llms[llm_key]
                applied_overrides.append(f"llm={llm_key}")
                logger.info(f"Applied LLM override: {llm_key}")
            else:
                logger.warning(
                    f"LLM override '{llm_key}' not in allowed_llms "
                    f"({', '.join(allowed_llms.keys())}), using default"
                )

        # Override: system_prompt (security-controlled)
        if "system_prompt" in processed_input:
            prompt_override = processed_input.pop("system_prompt")

            if not isinstance(prompt_override, str):
                logger.warning(
                    f"system_prompt must be string, got {type(prompt_override).__name__}, ignoring"
                )
            elif not self.config.get("allow_system_prompt"):
                logger.warning(
                    "system_prompt override attempted but allow_system_prompt=False (security)"
                )
            else:
                runtime_config["system_prompt"] = prompt_override
                applied_overrides.append("system_prompt=<custom>")
                logger.info("Applied system_prompt override")

        # Override: temperature (always allowed, validated)
        if "temperature" in processed_input:
            temp_override = processed_input.pop("temperature")

            if not isinstance(temp_override, (int, float)):
                logger.warning(
                    f"temperature must be numeric, got {type(temp_override).__name__}, ignoring"
                )
            elif not 0.0 <= temp_override <= 2.0:
                # Clamp to valid range
                clamped = max(0.0, min(2.0, float(temp_override)))
                runtime_config["temperature"] = clamped
                applied_overrides.append(f"temperature={clamped}")
                logger.warning(
                    f"temperature {temp_override} out of range [0.0, 2.0], "
                    f"clamped to {clamped}"
                )
            else:
                runtime_config["temperature"] = float(temp_override)
                applied_overrides.append(f"temperature={temp_override}")
                logger.info(f"Applied temperature override: {temp_override}")

        # Log summary
        if applied_overrides:
            logger.info(f"Applied overrides: {', '.join(applied_overrides)}")
        else:
            logger.debug("No overrides applied")

        return processed_input, runtime_config


class _WorkflowBase:
    """
    Internal base class used by @workflow decorator.
    Similar to _AgentBase but for workflows.
    """

    def __init__(self, builder_func: Callable, config: Dict[str, Any]):
        self.builder_func = builder_func
        self.config = config
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the workflow's StateGraph."""
        from langgraph.graph import StateGraph
        from aimq.langgraph.states import WorkflowState

        state_class = self.config.get("state_class", WorkflowState)
        graph = StateGraph(state_class)

        return self.builder_func(graph, self.config)

    def _compile(self):
        """Compile graph with optional checkpointing."""
        from aimq.langgraph.checkpoint import get_checkpointer

        checkpointer = None
        if self.config.get("checkpointer"):
            checkpointer = get_checkpointer()

        return self._graph.compile(checkpointer=checkpointer)

    def invoke(self, input: dict, config: dict | None = None):
        """Invoke the workflow (implements Runnable interface)."""
        return self._compiled.invoke(input, config)

    def stream(self, input: dict, config: dict | None = None):
        """Stream workflow execution (implements Runnable interface)."""
        return self._compiled.stream(input, config)
```

#### 1.4 Utility Functions

**File**: `src/aimq/langgraph/utils.py`

```python
"""Utility functions for LangGraph integration."""

from langchain_core.language_models import BaseChatModel
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Module-level cache for LLM instances
_llm_cache: dict[str, BaseChatModel] = {}

class LLMResolutionError(Exception):
    """Raised when LLM resolution fails."""
    pass

def get_default_llm(model: str | None = None) -> BaseChatModel:
    """Get default LLM from configuration with caching.

    Args:
        model: Override model name (optional)

    Returns:
        ChatMistralAI instance (cached singleton per model)

    Examples:
        >>> llm = get_default_llm()  # Uses config.mistral_model
        >>> llm = get_default_llm("mistral-small-latest")  # Override
    """
    from langchain_mistralai import ChatMistralAI
    from aimq.config import config

    model_name = model or config.mistral_model

    # Cache LLM instances to prevent connection pool exhaustion
    cache_key = f"mistral_{model_name}"
    if cache_key not in _llm_cache:
        logger.debug(f"Creating cached LLM instance: {model_name}")
        _llm_cache[cache_key] = ChatMistralAI(
            model=model_name,
            api_key=config.mistral_api_key,
            temperature=0.1,
        )

    return _llm_cache[cache_key]

def resolve_llm(
    llm_param: BaseChatModel | str | None,
    default_model: str = "mistral-large-latest"
) -> BaseChatModel:
    """Resolve LLM parameter to BaseChatModel instance.

    Accepts:
    - BaseChatModel instance (returns as-is)
    - String model name (converts to ChatMistralAI)
    - None (returns default LLM from config)

    Args:
        llm_param: LLM object, model name string, or None
        default_model: Default model name if llm_param is None

    Returns:
        BaseChatModel instance

    Raises:
        TypeError: If llm_param is not a valid type
        LLMResolutionError: If LLM creation fails

    Examples:
        >>> from langchain_mistralai import ChatMistralAI
        >>> llm = resolve_llm(None)  # Uses default
        >>> llm = resolve_llm("mistral-small-latest")  # String conversion
        >>> llm = resolve_llm(ChatMistralAI(model="custom"))  # Pass-through
    """
    # None → default LLM from config
    if llm_param is None:
        logger.debug(f"Using default LLM: {default_model}")
        return get_default_llm(model=default_model)

    # BaseChatModel → pass through
    if isinstance(llm_param, BaseChatModel):
        logger.debug(f"Using provided LLM: {type(llm_param).__name__}")
        return llm_param

    # String → convert to ChatMistralAI
    if isinstance(llm_param, str):
        try:
            from langchain_mistralai import ChatMistralAI
            from aimq.config import config

            logger.info(f"Converting string '{llm_param}' to ChatMistralAI")
            return ChatMistralAI(
                model=llm_param,
                api_key=config.mistral_api_key,
                temperature=0.1,
            )
        except ImportError as e:
            raise LLMResolutionError(
                "langchain-mistralai is required for string LLM names. "
                "Install with: uv add langchain-mistralai"
            ) from e
        except Exception as e:
            raise LLMResolutionError(
                f"Failed to create ChatMistralAI with model='{llm_param}': {e}"
            ) from e

    # Invalid type
    raise TypeError(
        f"llm must be BaseChatModel, str, or None. Got {type(llm_param).__name__}"
    )


def default_reply_function(message: str, metadata: dict) -> None:
    """Default reply function: enqueues responses to process_agent_response queue.

    This allows agents to send responses/updates that can be processed by
    another worker (e.g., webhooks, notifications, logging).

    Errors are logged but do not propagate to prevent agent execution failure.

    Args:
        message: Response message from agent
        metadata: Additional metadata (step info, status, job_id, etc.)

    Examples:
        >>> default_reply_function("Task complete", {"step": 1, "status": "success"})
        >>> # Message sent to process_agent_response queue
    """
    from datetime import datetime

    try:
        from aimq.providers.supabase import SupabaseQueueProvider

        provider = SupabaseQueueProvider()
        provider.send("process_agent_response", {
            "message": message,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
        })

        logger.debug(f"Reply sent: {message[:100]}...")

    except ImportError as e:
        logger.error(
            "Cannot send reply: SupabaseQueueProvider import failed. "
            "Is Supabase configured?",
            exc_info=True
        )
    except Exception as e:
        logger.error(
            f"Failed to send reply via default_reply_function: {e}. "
            f"Message: {message[:100]}...",
            exc_info=True
        )
        # Don't raise - reply failure should not break agent execution
```

#### 1.5 Standard State Definitions

**File**: `src/aimq/langgraph/states.py`

```python
"""Standard state definitions for workflows and agents."""

from typing import TypedDict, Annotated, Any, NotRequired, Sequence
from operator import add
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Standard state for agents.

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """
    # Required fields
    messages: Annotated[Sequence[BaseMessage], add]  # Conversation history (LangChain messages)
    tools: list[str]                                 # Available tool names
    iteration: int                                   # Iteration counter (prevent infinite loops)
    errors: Annotated[list[str], add]                # Collected errors

    # Optional fields (use NotRequired)
    current_tool: NotRequired[str]                   # Tool being executed
    tool_input: NotRequired[dict]                    # Input for current tool
    tool_output: NotRequired[Any]                    # Output from tool
    final_answer: NotRequired[str]                   # Agent's final response

    # Checkpointing fields (required if memory=True)
    thread_id: NotRequired[str]                      # Thread ID for checkpointing
    checkpoint_id: NotRequired[str]                  # Checkpoint ID

    # Multi-tenancy
    tenant_id: NotRequired[str]                      # Tenant ID for isolation

    # Extensibility
    metadata: NotRequired[dict[str, Any]]            # Custom metadata

class WorkflowState(TypedDict):
    """Standard state for workflows.

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """
    # Required fields
    input: dict                                      # Original input
    errors: Annotated[list[str], add]                # Collected errors

    # Optional fields (use NotRequired)
    current_step: NotRequired[str]                   # Current step name
    step_results: Annotated[list[dict], add]         # Results from each step
    final_output: NotRequired[dict]                  # Final result
    metadata: NotRequired[dict[str, Any]]            # Custom metadata
```

#### 1.6 Exception Types

**File**: `src/aimq/langgraph/exceptions.py`

```python
"""
Custom exceptions for LangGraph integration.

Provides specific exception types for better error handling and debugging.
"""

class LangGraphError(Exception):
    """Base exception for all LangGraph-related errors."""
    pass

class GraphBuildError(LangGraphError):
    """Raised when graph building fails.

    Examples:
        - Invalid node configuration
        - Missing required nodes
        - Invalid edge connections
    """
    pass

class GraphCompileError(LangGraphError):
    """Raised when graph compilation fails.

    Examples:
        - Circular dependencies
        - Unreachable nodes
        - Invalid state schema
    """
    pass

class StateValidationError(LangGraphError):
    """Raised when state validation fails.

    Examples:
        - Missing required state fields
        - Invalid state type
        - State doesn't extend AgentState
    """
    pass

class CheckpointerError(LangGraphError):
    """Raised when checkpointer configuration or operation fails.

    Examples:
        - Invalid Supabase connection
        - Schema not initialized
        - Checkpoint save/load failure
    """
    pass

class OverrideSecurityError(LangGraphError):
    """Raised when job override violates security policy.

    Examples:
        - LLM key not in allowed_llms
        - system_prompt override when allow_system_prompt=False
        - Invalid override value type
    """
    pass

class LLMResolutionError(LangGraphError):
    """Raised when LLM resolution fails.

    Examples:
        - Invalid LLM parameter type
        - Failed to create LLM instance
        - Missing required LangChain package
    """
    pass

class ToolValidationError(LangGraphError):
    """Raised when tool input validation fails.

    Examples:
        - Tool input doesn't match schema
        - Unauthorized file path access
        - SQL injection attempt detected
    """
    pass
```

#### 1.7 Checkpointing Integration

**File**: `src/aimq/langgraph/checkpoint.py`

```python
"""Supabase-backed checkpointing for LangGraph workflows."""

from langgraph.checkpoint.postgres import PostgresSaver
from aimq.clients.supabase import get_supabase_client
from aimq.config import config
from urllib.parse import quote_plus
import re
import logging

logger = logging.getLogger(__name__)

_checkpointer_instance = None

class CheckpointerError(Exception):
    """Raised when checkpointer cannot be configured."""
    pass

def get_checkpointer() -> PostgresSaver:
    """Get or create Supabase checkpoint saver singleton.

    Returns:
        PostgresSaver instance connected to Supabase PostgreSQL

    Raises:
        CheckpointerError: If Supabase configuration is invalid
    """
    global _checkpointer_instance

    if _checkpointer_instance is None:
        # Build PostgreSQL connection string from Supabase config
        conn_string = _build_connection_string()
        _checkpointer_instance = PostgresSaver(conn_string)
        _ensure_schema()

    return _checkpointer_instance

def _build_connection_string() -> str:
    """Build PostgreSQL connection string from Supabase config.

    Returns:
        PostgreSQL connection URL with encoded credentials

    Raises:
        CheckpointerError: If Supabase config is invalid or missing

    Examples:
        postgresql://postgres:encoded_pw@db.project.supabase.co:5432/postgres
    """
    url = config.supabase_url
    password = config.supabase_key

    if not url:
        raise CheckpointerError(
            "SUPABASE_URL required for checkpointing. "
            "Set environment variable or .env file."
        )

    if not password:
        raise CheckpointerError(
            "SUPABASE_KEY required for checkpointing. "
            "Set environment variable or .env file."
        )

    # Extract project reference from URL
    match = re.search(r"https://(.+?)\.supabase\.co", url)
    if not match:
        raise CheckpointerError(
            f"Invalid SUPABASE_URL format: {url}. "
            f"Expected format: https://PROJECT.supabase.co"
        )

    project_ref = match.group(1)
    logger.debug(f"Extracted Supabase project: {project_ref}")

    # URL-encode password to handle special characters
    encoded_password = quote_plus(password)

    # Build connection string
    conn_string = (
        f"postgresql://postgres:{encoded_password}"
        f"@db.{project_ref}.supabase.co:5432/postgres"
    )

    logger.info("Built Supabase PostgreSQL connection string")
    return conn_string

def _ensure_schema() -> None:
    """Ensure langgraph schema and tables exist.

    WARNING: This requires database admin access. In production,
    create the schema manually via Supabase dashboard:

    1. Go to SQL Editor in Supabase
    2. Run the schema creation SQL (see below)
    3. Set LANGGRAPH_CHECKPOINT_ENABLED=true

    This function will check if schema exists and warn if it needs setup.

    Raises:
        CheckpointerError: If schema creation fails with unexpected error
    """
    from postgrest.exceptions import APIError
    from aimq.clients.supabase import get_supabase_client

    client = get_supabase_client()

    schema_sql = """
    -- LangGraph Checkpoint Schema
    CREATE SCHEMA IF NOT EXISTS langgraph;

    -- Checkpoints table
    CREATE TABLE IF NOT EXISTS langgraph.checkpoints (
        thread_id TEXT NOT NULL,
        checkpoint_id TEXT NOT NULL,
        parent_checkpoint_id TEXT,
        checkpoint JSONB NOT NULL,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (thread_id, checkpoint_id)
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
        ON langgraph.checkpoints(thread_id);
    CREATE INDEX IF NOT EXISTS idx_checkpoints_created
        ON langgraph.checkpoints(created_at);
    CREATE INDEX IF NOT EXISTS idx_checkpoints_parent
        ON langgraph.checkpoints(parent_checkpoint_id);
    """

    try:
        # Attempt to create schema
        client.rpc("exec_sql", {"sql": schema_sql}).execute()
        logger.info("LangGraph checkpoint schema initialized successfully")

    except APIError as e:
        error_msg = str(e).lower()

        # Check if error is benign (schema already exists)
        if any(phrase in error_msg for phrase in ["already exists", "duplicate"]):
            logger.debug("LangGraph schema already exists")

        # Permission error - provide instructions
        elif "permission denied" in error_msg or "access denied" in error_msg:
            logger.warning(
                "Cannot create checkpoint schema (permission denied). "
                "Please create manually via Supabase SQL Editor. "
                "SQL script available in docs/deployment/langgraph-schema.sql"
            )

        # Other API errors
        else:
            logger.error(f"Failed to create checkpoint schema: {e}")
            raise CheckpointerError(
                "Checkpoint schema setup failed. "
                "Create manually via Supabase dashboard or disable checkpointing."
            ) from e

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error during schema setup: {e}", exc_info=True)
        raise CheckpointerError(
            f"Failed to initialize checkpoint schema: {e}"
        ) from e
```

### Phase 2: Built-in Agents (Priority 1)

#### 2.1 Base Agent Class

**File**: `src/aimq/agents/base.py`

```python
"""Base class for built-in agents."""

from typing import List, Any
from langchain.tools import BaseTool
from langgraph.graph import StateGraph
from aimq.langgraph.checkpoint import get_checkpointer
from aimq.langgraph.states import AgentState

class BaseAgent:
    """Base class for built-in agents."""

    def __init__(
        self,
        tools: List[BaseTool],
        system_prompt: str,
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
    ):
        self.tools = tools
        self.system_prompt = system_prompt
        self.llm = llm
        self.temperature = temperature
        self.memory = memory

        # Build and compile graph
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the agent's graph. Override in subclasses."""
        raise NotImplementedError

    def _compile(self):
        """Compile the graph with optional checkpointing."""
        checkpointer = get_checkpointer() if self.memory else None
        return self._graph.compile(checkpointer=checkpointer)

    def invoke(self, input: dict, config: dict | None = None):
        """Invoke the agent (implements Runnable interface)."""
        return self._compiled.invoke(input, config)

    def stream(self, input: dict, config: dict | None = None):
        """Stream agent execution (implements Runnable interface)."""
        return self._compiled.stream(input, config)
```

#### 2.2 ReActAgent

**File**: `src/aimq/agents/react.py`

```python
"""ReAct (Reasoning + Acting) Agent implementation."""

from typing import List, Literal
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END
from aimq.agents.base import BaseAgent
from aimq.langgraph.states import AgentState

class ReActAgent(BaseAgent):
    """
    ReAct agent that reasons about actions and executes tools iteratively.

    Pattern:
    1. Reason about what to do
    2. Execute tool if needed
    3. Observe results
    4. Repeat until done

    Args:
        tools: List of LangChain tools the agent can use
        system_prompt: Agent instructions
        llm: LLM model name (default: "mistral-large-latest")
        temperature: LLM temperature (default: 0.1)
        memory: Enable conversation memory (default: False)
        max_iterations: Max reasoning loops (default: 10)

    Example:
        from aimq.agents import ReActAgent
        from aimq.tools.supabase import ReadFile
        from aimq.tools.ocr import ImageOCR

        agent = ReActAgent(
            tools=[ReadFile(), ImageOCR()],
            system_prompt="You are a document assistant",
            memory=True
        )

        worker.assign(agent, queue="doc-agent")
    """

    def __init__(
        self,
        tools: List[BaseTool],
        system_prompt: str = "You are a helpful AI assistant.",
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
        max_iterations: int = 10,
    ):
        self.max_iterations = max_iterations
        super().__init__(tools, system_prompt, llm, temperature, memory)

    def _build_graph(self) -> StateGraph:
        """Build ReAct agent graph."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("reason", self._reasoning_node)
        graph.add_node("act", self._action_node)

        # Add conditional routing
        graph.add_conditional_edges(
            "reason",
            self._should_continue,
            {
                "act": "act",
                "reason": "reason",
                "end": END,
            }
        )

        # After action, go back to reasoning
        graph.add_edge("act", "reason")

        # Start with reasoning
        graph.set_entry_point("reason")

        return graph

    def _reasoning_node(self, state: AgentState) -> AgentState:
        """Reasoning node: decide what to do next."""
        from aimq.clients.mistral import get_mistral_client

        client = get_mistral_client()

        # Build ReAct prompt
        prompt = self._build_react_prompt(state)

        # Get LLM decision
        response = client.chat.completions.create(
            model=self.llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )

        # Parse action from response
        action = self._parse_action(response.choices[0].message.content)

        return {
            "messages": [{"role": "assistant", "content": response.choices[0].message.content}],
            "current_tool": action.get("tool"),
            "tool_input": action.get("input"),
            "final_answer": action.get("answer"),
            "iteration": state["iteration"] + 1,
        }

    def _action_node(self, state: AgentState) -> AgentState:
        """Action node: execute the chosen tool."""
        tool_name = state["current_tool"]
        tool_input = state["tool_input"]

        # Find tool
        tool = next((t for t in self.tools if t.name == tool_name), None)

        if not tool:
            return {
                "messages": [{"role": "system", "content": f"Error: Unknown tool {tool_name}"}],
                "tool_output": f"Error: Unknown tool {tool_name}",
                "errors": [f"Unknown tool: {tool_name}"],
            }

        # Execute tool
        try:
            result = tool.invoke(tool_input)
            return {
                "messages": [{"role": "system", "content": f"Tool result: {result}"}],
                "tool_output": str(result),
            }
        except Exception as e:
            return {
                "messages": [{"role": "system", "content": f"Tool error: {str(e)}"}],
                "tool_output": f"Error: {str(e)}",
                "errors": [str(e)],
            }

    def _should_continue(self, state: AgentState) -> Literal["act", "reason", "end"]:
        """Decide next step based on state."""
        # Stop if we have an answer or hit max iterations
        if state.get("final_answer") or state["iteration"] >= self.max_iterations:
            return "end"

        # Execute tool if one was chosen
        if state.get("current_tool"):
            return "act"

        # Continue reasoning
        return "reason"

    def _build_react_prompt(self, state: AgentState) -> str:
        """Build ReAct prompt with history."""
        system = f"""{self.system_prompt}

You have access to these tools:
{self._format_tools()}

Respond in this format:
THOUGHT: <your reasoning>
ACTION: <tool_name>
INPUT: <tool input as JSON>

OR if you have the final answer:
THOUGHT: <your reasoning>
ANSWER: <final answer>
"""

        history = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in state.get("messages", [])
        ])

        return f"{system}\n\n{history}"

    def _format_tools(self) -> str:
        """Format tool descriptions."""
        return "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])

    def _parse_action(self, content: str) -> dict:
        """Parse LLM response into action dict."""
        import json

        lines = content.strip().split("\n")
        action = {}

        for line in lines:
            if line.startswith("ACTION:"):
                action["tool"] = line.replace("ACTION:", "").strip()
            elif line.startswith("INPUT:"):
                try:
                    action["input"] = json.loads(line.replace("INPUT:", "").strip())
                except:
                    action["input"] = {}
            elif line.startswith("ANSWER:"):
                action["answer"] = line.replace("ANSWER:", "").strip()

        return action
```

#### 2.3 PlanExecuteAgent

**File**: `src/aimq/agents/plan_execute.py`

```python
"""Plan-and-Execute Agent implementation."""

from typing import List
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END
from aimq.agents.base import BaseAgent

class PlanExecuteState(TypedDict):
    """State for plan-execute agent."""
    input: str
    plan: list[str]
    current_step: int
    step_results: Annotated[list[dict], add]
    final_output: dict | None
    needs_replan: bool

class PlanExecuteAgent(BaseAgent):
    """
    Plan-and-Execute agent that creates a plan then executes steps sequentially.

    Pattern:
    1. Create execution plan
    2. Execute each step
    3. Collect results
    4. Replan if needed

    Args:
        tools: List of LangChain tools
        system_prompt: Agent instructions
        llm: LLM model name
        temperature: LLM temperature
        memory: Enable checkpointing

    Example:
        agent = PlanExecuteAgent(
            tools=[ReadFile(), WriteRecord()],
            system_prompt="You are a task planner",
            memory=True
        )

        worker.assign(agent, queue="planner")
    """

    def _build_graph(self) -> StateGraph:
        """Build plan-execute graph."""
        graph = StateGraph(PlanExecuteState)

        graph.add_node("plan", self._plan_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("finalize", self._finalize_node)

        graph.add_edge("plan", "execute")
        graph.add_conditional_edges(
            "execute",
            self._should_continue,
            {
                "execute": "execute",
                "replan": "plan",
                "finalize": "finalize",
            }
        )
        graph.add_edge("finalize", END)

        graph.set_entry_point("plan")

        return graph

    def _plan_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Generate execution plan."""
        from aimq.clients.mistral import get_mistral_client

        client = get_mistral_client()

        prompt = f"""{self.system_prompt}

Task: {state['input']}

Available tools: {self._format_tools()}

Create a step-by-step plan. Respond with a numbered list:
1. <step 1>
2. <step 2>
...
"""

        response = client.chat.completions.create(
            model=self.llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )

        # Parse plan
        steps = self._parse_plan(response.choices[0].message.content)

        return {
            "plan": steps,
            "current_step": 0,
        }

    def _execute_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Execute current step."""
        current = state["plan"][state["current_step"]]

        # Execute with tools (simplified)
        result = self._execute_step_with_tools(current)

        return {
            "step_results": [{
                "step": current,
                "result": result,
                "step_number": state["current_step"],
            }],
            "current_step": state["current_step"] + 1,
        }

    def _finalize_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Compile final output."""
        return {
            "final_output": {
                "task": state["input"],
                "plan": state["plan"],
                "results": state["step_results"],
                "status": "completed",
            }
        }

    def _should_continue(self, state: PlanExecuteState):
        """Decide next step."""
        if state["current_step"] >= len(state["plan"]):
            return "finalize"
        if state.get("needs_replan"):
            return "replan"
        return "execute"

    # ... helper methods ...
```

### Phase 3: Built-in Workflows (Priority 1)

#### 3.1 DocumentWorkflow

**File**: `src/aimq/workflows/document.py`

```python
"""Document processing workflow."""

from typing import Literal
from langgraph.graph import StateGraph, END
from aimq.workflows.base import BaseWorkflow

class DocumentState(TypedDict):
    """State for document workflow."""
    document_path: str
    raw_content: bytes | None
    document_type: Literal["image", "pdf", "docx"] | None
    text: str | None
    metadata: dict
    status: str

class DocumentWorkflow(BaseWorkflow):
    """
    Multi-step document processing pipeline.

    Steps:
    1. Fetch document from storage
    2. Detect document type
    3. Route to appropriate processor (OCR, PDF, etc.)
    4. Extract metadata
    5. Store results

    Args:
        storage_tool: Tool for reading files (e.g., ReadFile())
        ocr_tool: Tool for OCR processing (e.g., ImageOCR())
        pdf_tool: Tool for PDF processing (e.g., PageSplitter())
        checkpointer: Enable state persistence

    Example:
        from aimq.workflows import DocumentWorkflow
        from aimq.tools.supabase import ReadFile, WriteRecord
        from aimq.tools.ocr import ImageOCR

        workflow = DocumentWorkflow(
            storage_tool=ReadFile(),
            ocr_tool=ImageOCR(),
            checkpointer=True
        )

        worker.assign(workflow, queue="documents")
    """

    def __init__(
        self,
        storage_tool,
        ocr_tool,
        pdf_tool=None,
        checkpointer: bool = False,
    ):
        self.storage_tool = storage_tool
        self.ocr_tool = ocr_tool
        self.pdf_tool = pdf_tool
        super().__init__(checkpointer=checkpointer)

    def _build_graph(self) -> StateGraph:
        """Build document processing graph."""
        graph = StateGraph(DocumentState)

        graph.add_node("fetch", self._fetch_node)
        graph.add_node("detect", self._detect_type_node)
        graph.add_node("process_image", self._process_image_node)
        graph.add_node("process_pdf", self._process_pdf_node)
        graph.add_node("store", self._store_node)

        graph.add_edge("fetch", "detect")
        graph.add_conditional_edges(
            "detect",
            self._route_by_type,
            {
                "process_image": "process_image",
                "process_pdf": "process_pdf",
                "error": END,
            }
        )
        graph.add_edge("process_image", "store")
        graph.add_edge("process_pdf", "store")
        graph.add_edge("store", END)

        graph.set_entry_point("fetch")

        return graph

    def _fetch_node(self, state: DocumentState) -> DocumentState:
        """Fetch document from storage."""
        content = self.storage_tool.invoke({"path": state["document_path"]})
        return {
            "raw_content": content,
            "status": "fetched",
        }

    def _detect_type_node(self, state: DocumentState) -> DocumentState:
        """Detect document type."""
        import magic
        mime = magic.from_buffer(state["raw_content"], mime=True)

        if mime.startswith("image/"):
            doc_type = "image"
        elif mime == "application/pdf":
            doc_type = "pdf"
        else:
            doc_type = "unknown"

        return {
            "document_type": doc_type,
            "metadata": {"mime_type": mime},
            "status": "typed",
        }

    def _process_image_node(self, state: DocumentState) -> DocumentState:
        """Process image with OCR."""
        from aimq.attachment import Attachment

        attachment = Attachment(state["raw_content"])
        result = self.ocr_tool.invoke({"image": attachment})

        return {
            "text": result["text"],
            "metadata": {**state["metadata"], "ocr_confidence": result.get("confidence")},
            "status": "processed",
        }

    def _process_pdf_node(self, state: DocumentState) -> DocumentState:
        """Process PDF."""
        if not self.pdf_tool:
            return {"status": "error", "text": "No PDF tool configured"}

        pages = self.pdf_tool.invoke({"pdf": state["raw_content"]})
        text = "\n\n".join([p["text"] for p in pages])

        return {
            "text": text,
            "metadata": {**state["metadata"], "page_count": len(pages)},
            "status": "processed",
        }

    def _store_node(self, state: DocumentState) -> DocumentState:
        """Store results."""
        from aimq.tools.supabase import WriteRecord

        write_tool = WriteRecord()
        write_tool.invoke({
            "table": "processed_documents",
            "data": {
                "path": state["document_path"],
                "text": state["text"],
                "metadata": state["metadata"],
            }
        })

        return {"status": "stored"}

    def _route_by_type(self, state: DocumentState) -> str:
        """Route based on document type."""
        doc_type = state.get("document_type")
        if doc_type == "image":
            return "process_image"
        elif doc_type == "pdf":
            return "process_pdf"
        return "error"
```

#### 3.2 MultiAgentWorkflow

**File**: `src/aimq/workflows/multi_agent.py`

```python
"""Multi-agent collaboration workflow."""

from typing import List, Dict
from langgraph.graph import StateGraph, END
from aimq.workflows.base import BaseWorkflow

class MultiAgentWorkflow(BaseWorkflow):
    """
    Multi-agent collaboration with supervisor pattern.

    Pattern:
    1. Supervisor assigns work to specialized agents
    2. Each agent completes their portion
    3. Supervisor coordinates and decides next steps
    4. Process continues until task complete

    Args:
        agents: Dict of agent_name -> agent_function
        supervisor_llm: LLM for supervisor decisions
        checkpointer: Enable state persistence

    Example:
        from aimq.workflows import MultiAgentWorkflow

        workflow = MultiAgentWorkflow(
            agents={
                "researcher": researcher_func,
                "analyst": analyst_func,
                "writer": writer_func,
            },
            supervisor_llm="mistral-large-latest",
            checkpointer=True
        )

        worker.assign(workflow, queue="multi-agent")
    """

    def __init__(
        self,
        agents: Dict[str, callable],
        supervisor_llm: str = "mistral-large-latest",
        checkpointer: bool = False,
    ):
        self.agents = agents
        self.supervisor_llm = supervisor_llm
        super().__init__(checkpointer=checkpointer)

    def _build_graph(self) -> StateGraph:
        """Build multi-agent graph."""
        from aimq.langgraph.states import AgentState

        graph = StateGraph(AgentState)

        # Add supervisor
        graph.add_node("supervisor", self._supervisor_node)

        # Add agent nodes
        for agent_name, agent_func in self.agents.items():
            graph.add_node(agent_name, agent_func)
            # Each agent reports back to supervisor
            graph.add_edge(agent_name, "supervisor")

        # Supervisor routes to agents or ends
        graph.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {**{name: name for name in self.agents.keys()}, "end": END}
        )

        graph.set_entry_point("supervisor")

        return graph

    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor decides which agent to invoke."""
        from aimq.clients.mistral import get_mistral_client

        client = get_mistral_client()

        # Build coordination prompt
        prompt = self._build_supervisor_prompt(state)

        response = client.chat.completions.create(
            model=self.supervisor_llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        next_agent = response.choices[0].message.content.strip().lower()

        return {
            "messages": [{"role": "supervisor", "content": f"Routing to: {next_agent}"}],
            "current_tool": next_agent,  # Reuse field for next agent
            "iteration": state["iteration"] + 1,
        }

    def _route_to_agent(self, state: AgentState) -> str:
        """Route to next agent."""
        next_agent = state.get("current_tool", "end")

        # Safety: prevent infinite loops
        if state["iteration"] >= 20:
            return "end"

        return next_agent

    def _build_supervisor_prompt(self, state: AgentState) -> str:
        """Build supervisor coordination prompt."""
        agent_list = ", ".join(self.agents.keys())

        return f"""You are coordinating a team of agents.

Available agents: {agent_list}

Task progress:
{self._format_progress(state)}

Which agent should work next? Respond with just the agent name, or "end" if complete.
"""

    def _format_progress(self, state: AgentState) -> str:
        """Format task progress from state."""
        messages = state.get("messages", [])
        return "\n".join([
            f"{msg['role']}: {msg['content'][:100]}..."
            for msg in messages[-5:]  # Last 5 messages
        ])
```

### Phase 4: Tools & Checkpointing (Priority 1)

#### 4.1 Docling Tool

**File**: `src/aimq/tools/docling/converter.py`

```python
"""Docling document converter tool."""

from langchain.tools import BaseTool
from docling.document_converter import DocumentConverter

class DoclingConverter(BaseTool):
    """
    Convert documents using Docling.

    Supports: PDF, DOCX, PPTX, XLSX, images
    Features: Layout analysis, table extraction, OCR

    Example:
        tool = DoclingConverter()
        result = tool.invoke({
            "file_path": "report.pdf",
            "export_format": "markdown"
        })
    """

    name = "docling_convert"
    description = """Convert documents (PDF, DOCX, PPTX, XLSX, images) to structured format.
    Supports layout analysis, table extraction, OCR for scanned documents."""

    def _run(self, file_path: str, export_format: str = "markdown") -> dict:
        """Convert document."""
        converter = DocumentConverter()
        result = converter.convert(file_path)

        if export_format == "markdown":
            content = result.document.export_to_markdown()
        elif export_format == "html":
            content = result.document.export_to_html()
        else:  # json
            content = result.document.export_to_dict()

        return {
            "content": content,
            "format": export_format,
            "metadata": result.document.metadata,
        }
```

### Phase 5: Examples (Priority 1)

#### 5.1 Using Built-in ReActAgent

**File**: `examples/langgraph/using_builtin_react.py`

```python
"""
Example: Using built-in ReActAgent

Demonstrates how to configure and use the pre-built ReAct agent
for document question answering with tools.
"""

from aimq.worker import Worker
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile, ReadRecord
from aimq.tools.ocr import ImageOCR

# Initialize worker
worker = Worker()

# Configure ReAct agent with tools
agent = ReActAgent(
    tools=[
        ReadFile(),    # Read files from Supabase storage
        ReadRecord(),  # Read records from Supabase database
        ImageOCR(),    # Extract text from images
    ],
    system_prompt="""You are a helpful document assistant.
    You can read files, extract text from images, and query databases.
    Always provide clear, concise answers.""",
    llm="mistral-large-latest",
    temperature=0.1,
    memory=True,  # Enable checkpointing for resumable workflows
    max_iterations=10,
)

# Assign to queue
worker.assign(agent, queue="doc-qa", timeout=900, delete_on_finish=False)

if __name__ == "__main__":
    print("Starting ReAct agent worker...")
    print("Queue: doc-qa")
    print("Tools: ReadFile, ReadRecord, ImageOCR")
    print("\nSend jobs with:")
    print('aimq send doc-qa \'{"messages": [{"role": "user", "content": "What is in documents/report.pdf?"}], "iteration": 0}\'')

    worker.start()
```

#### 5.2 Using Built-in DocumentWorkflow

**File**: `examples/langgraph/using_builtin_document.py`

```python
"""
Example: Using built-in DocumentWorkflow

Demonstrates automated document processing pipeline
with type detection and conditional routing.
"""

from aimq.worker import Worker
from aimq.workflows import DocumentWorkflow
from aimq.tools.supabase import ReadFile, WriteRecord
from aimq.tools.ocr import ImageOCR
from aimq.tools.pdf import PageSplitter

# Initialize worker
worker = Worker()

# Configure document workflow
workflow = DocumentWorkflow(
    storage_tool=ReadFile(),
    ocr_tool=ImageOCR(),
    pdf_tool=PageSplitter(),
    checkpointer=True,  # Enable checkpointing for long documents
)

# Assign to queue
worker.assign(workflow, queue="doc-pipeline", timeout=900)

if __name__ == "__main__":
    print("Starting Document workflow worker...")
    print("Queue: doc-pipeline")
    print("\nSend jobs with:")
    print('aimq send doc-pipeline \'{"document_path": "uploads/report.pdf", "metadata": {}, "status": "pending"}\'')

    worker.start()
```

#### 5.3 Custom Agent with @agent Decorator

**File**: `examples/langgraph/custom_agent_decorator.py`

```python
"""
Example: Creating custom agent with @agent decorator

Demonstrates how to define a custom agent using the decorator pattern.
"""

from aimq.worker import Worker
from aimq.langgraph import agent
from aimq.tools.supabase import ReadFile, WriteRecord
from langgraph.graph import StateGraph, END

# Define custom agent using decorator
@agent(
    tools=[ReadFile(), WriteRecord()],
    system_prompt="You are a data processing specialist",
    llm="mistral-large-latest",
    memory=True
)
def data_processor_agent(graph: StateGraph, config: dict) -> StateGraph:
    """
    Custom agent that processes data files and stores results.

    The config dict contains:
    - tools: List of available tools
    - system_prompt: Agent instructions
    - llm: LLM model name
    - temperature: LLM temperature
    - memory: Whether checkpointing is enabled
    """

    def read_and_analyze(state):
        """Read file and analyze data."""
        from aimq.clients.mistral import get_mistral_client

        # Get tools from config
        read_tool = next(t for t in config["tools"] if t.name == "read_file")

        # Read file
        content = read_tool.invoke({"path": state["messages"][0]["content"]})

        # Analyze with LLM
        client = get_mistral_client()
        response = client.chat.completions.create(
            model=config["llm"],
            messages=[
                {"role": "system", "content": config["system_prompt"]},
                {"role": "user", "content": f"Analyze this data: {content}"}
            ],
            temperature=config["temperature"],
        )

        return {
            "messages": [{"role": "assistant", "content": response.choices[0].message.content}],
            "tool_output": response.choices[0].message.content,
        }

    def store_results(state):
        """Store analysis results."""
        write_tool = next(t for t in config["tools"] if t.name == "write_record")

        write_tool.invoke({
            "table": "analysis_results",
            "data": {
                "analysis": state["tool_output"],
                "timestamp": "NOW()",
            }
        })

        return {
            "final_answer": "Analysis complete and stored",
        }

    # Build graph
    graph.add_node("analyze", read_and_analyze)
    graph.add_node("store", store_results)
    graph.add_edge("analyze", "store")
    graph.add_edge("store", END)
    graph.set_entry_point("analyze")

    return graph

# Use the custom agent
worker = Worker()
agent_instance = data_processor_agent()
worker.assign(agent_instance, queue="data-processor", timeout=600)

if __name__ == "__main__":
    print("Starting custom data processor agent...")
    worker.start()
```

#### 5.4 Custom Workflow with @workflow Decorator

**File**: `examples/langgraph/custom_workflow_decorator.py`

```python
"""
Example: Creating custom workflow with @workflow decorator

Demonstrates how to define a custom multi-step workflow.
"""

from typing import TypedDict, Annotated
from operator import add
from aimq.worker import Worker
from aimq.langgraph import workflow
from langgraph.graph import StateGraph, END

# Define custom state
class ETLState(TypedDict):
    source_path: str
    extracted_data: dict | None
    transformed_data: dict | None
    load_status: str
    errors: Annotated[list[str], add]

# Define custom workflow
@workflow(state_class=ETLState, checkpointer=True)
def etl_workflow(graph: StateGraph, config: dict) -> StateGraph:
    """
    Custom ETL (Extract-Transform-Load) workflow.

    Steps:
    1. Extract data from source
    2. Transform data
    3. Load into database
    """

    def extract(state: ETLState) -> ETLState:
        """Extract data from source."""
        from aimq.tools.supabase import ReadFile

        tool = ReadFile()
        try:
            data = tool.invoke({"path": state["source_path"]})
            return {"extracted_data": {"raw": data}}
        except Exception as e:
            return {"errors": [f"Extract failed: {str(e)}"]}

    def transform(state: ETLState) -> ETLState:
        """Transform extracted data."""
        if not state.get("extracted_data"):
            return {"errors": ["No data to transform"]}

        # Custom transformation logic
        raw = state["extracted_data"]["raw"]
        transformed = {
            "processed": raw.upper(),  # Example transformation
            "length": len(raw),
        }

        return {"transformed_data": transformed}

    def load(state: ETLState) -> ETLState:
        """Load transformed data."""
        from aimq.tools.supabase import WriteRecord

        if not state.get("transformed_data"):
            return {"errors": ["No data to load"]}

        tool = WriteRecord()
        try:
            tool.invoke({
                "table": "etl_results",
                "data": state["transformed_data"],
            })
            return {"load_status": "success"}
        except Exception as e:
            return {"errors": [f"Load failed: {str(e)}"]}

    # Build graph
    graph.add_node("extract", extract)
    graph.add_node("transform", transform)
    graph.add_node("load", load)

    graph.add_edge("extract", "transform")
    graph.add_edge("transform", "load")
    graph.add_edge("load", END)

    graph.set_entry_point("extract")

    return graph

# Use the custom workflow
worker = Worker()
workflow_instance = etl_workflow()
worker.assign(workflow_instance, queue="etl-pipeline", timeout=600)

if __name__ == "__main__":
    print("Starting custom ETL workflow...")
    print('Send jobs: aimq send etl-pipeline \'{"source_path": "data/input.csv", "errors": []}\'')
    worker.start()
```

### Phase 6: Documentation (Priority 2)

Create comprehensive docs:
- `docs/user-guide/langgraph.md` - Complete LangGraph guide
- `docs/user-guide/agents.md` - Using and customizing agents
- `docs/user-guide/workflows.md` - Building workflows
- `docs/api/langgraph.md` - API reference

### Phase 7: Testing (Priority 1)

```
tests/aimq/langgraph/
├── test_decorators.py         # Test @workflow and @agent
├── test_checkpoint.py         # Test checkpointing
tests/aimq/agents/
├── test_react.py             # Test ReActAgent
├── test_plan_execute.py      # Test PlanExecuteAgent
tests/aimq/workflows/
├── test_document.py          # Test DocumentWorkflow
├── test_multi_agent.py       # Test MultiAgentWorkflow
tests/integration/langgraph/
├── test_react_e2e.py        # End-to-end ReAct test
├── test_document_e2e.py     # End-to-end doc workflow test
└── test_custom_decorator.py # Test custom decorators
```

---

## Progress Tracking

### Phase 0: Setup ✅
- [x] Create PLAN.md
- [x] Update .gitignore
- [x] Revise architecture

### Phase 1: Core (Pending)
- [ ] Add dependencies
- [ ] Implement @workflow decorator
- [ ] Implement @agent decorator
- [ ] Implement checkpointing
- [ ] Standard state definitions

### Phase 2: Agents (Pending)
- [ ] BaseAgent class
- [ ] ReActAgent
- [ ] PlanExecuteAgent

### Phase 3: Workflows (Pending)
- [ ] BaseWorkflow class
- [ ] DocumentWorkflow
- [ ] MultiAgentWorkflow

### Phase 4: Tools (Pending)
- [ ] Docling tool wrapper
- [ ] Test tool compatibility

### Phase 5: Examples (Pending)
- [ ] Using ReActAgent
- [ ] Using DocumentWorkflow
- [ ] Custom agent decorator
- [ ] Custom workflow decorator

### Phase 6: Docs (Pending)
- [ ] User guides
- [ ] API reference
- [ ] Tutorials

### Phase 7: Tests (Pending)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Coverage >89%

---

## Key Design Decisions

**2025-10-30 - Decorator-Based Architecture**
- **Decision**: Use `@workflow` and `@agent` decorators instead of `worker.graph()`
- **Rationale**: More flexible, allows built-in patterns and custom definitions
- **Impact**: Users can use pre-built agents/workflows OR create custom ones

**Built-ins Use Decorators with Base Classes**
- **Decision**: Built-in agents/workflows defined using decorators, but decorators use BaseAgent/BaseWorkflow internally
- **Rationale**: Clean decorator-based API (readable examples) + DRY principle via base classes
- **Impact**: Users see decorator usage, implementation reuses shared logic

**LangChain LLM Integration**
- **Decision**: Accept LangChain LLM objects instead of strings
- **Rationale**: Leverage full LangChain ecosystem (any LLM: Mistral, OpenAI, Anthropic, etc.)
- **Convenience**: Also accept strings, auto-convert to ChatMistralAI
- **Impact**: Maximum flexibility while maintaining ease of use

**Three-Level Configuration**
- **Decision**: Decorator defaults → Factory overrides → Job-level overrides (with security)
- **Rationale**: Progressive enhancement - simple by default, powerful when needed
- **Impact**: Built-ins work out-of-box, fully customizable in tasks.py, job-specific tuning

**Security-First Job Overrides**
- **Decision**: Job data can only override whitelisted LLMs via `allowed_llms` dict
- **Rationale**: Prevent injection attacks, explicit control over allowed models
- **Keys**: Simple names (`llm`, `system_prompt`, `temperature` not `_override` suffix)
- **Impact**: Secure by default (no overrides unless explicitly enabled)

**Default Reply Function**
- **Decision**: Agents default to enqueuing responses to `process_agent_response` queue
- **Rationale**: Common pattern for async response handling, webhook notifications, logging
- **Impact**: Works out-of-box, users can provide custom reply_function if needed

**Custom Agent State with Safety**
- **Decision**: Allow custom state_class but require it extends AgentState
- **Rationale**: Flexibility for specialized agents while maintaining type safety
- **Impact**: Standard fields always available, custom fields when needed

**Factory Pattern**
- **Decision**: Decorators return factories that create configured instances
- **Rationale**: Allows parameterization (tools, prompts, LLM settings) at runtime
- **Example**: `agent = ReActAgent(tools=[...])` then `worker.assign(agent, queue="q")`

**Built-in vs Custom**
- **Decision**: Provide built-in agents/workflows, users can customize via config or decorators
- **Rationale**: Best of both worlds - convenience for common patterns, flexibility for custom needs

**Examples Show Usage**
- **Decision**: Examples demonstrate using built-ins and creating customs
- **Rationale**: Faster onboarding, shows both simple and advanced patterns

---

## Estimated Effort

- Phase 1: Core Decorators - 4-5 hours
- Phase 2: Built-in Agents - 4-5 hours
- Phase 3: Built-in Workflows - 3-4 hours
- Phase 4: Tools - 2-3 hours
- Phase 5: Examples - 3-4 hours
- Phase 6: Documentation - 3-4 hours
- Phase 7: Testing - 4-5 hours
- **Total: ~23-30 hours**

---

**Last Updated**: 2025-10-30
**Next Review**: After Phase 1 completion
