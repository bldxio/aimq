# Phase 1: Core Decorators & Infrastructure

**Status**: ⏳ Not Started
**Priority**: 1 (Critical)
**Estimated**: 5-6 hours
**Dependencies**: Phase 0 (Complete)

---

## Objectives

Implement the foundational infrastructure for LangGraph integration:
1. Add and verify all required dependencies
2. Implement `@workflow` and `@agent` decorators
3. Create internal base classes (`_AgentBase`, `_WorkflowBase`)
4. Implement utility functions for LLM resolution and reply handling
5. Define standard state classes with proper type annotations
6. Create custom exception types module
7. Implement Supabase-backed checkpointing

## Critical Fixes Applied

This phase incorporates **10 critical fixes** from PLAN_FIXES.md:

- **Fix #2**: Type annotations (use `type[dict]` instead of `Type[TypedDict]`)
- **Fix #3**: Add `NotRequired` markers to optional state fields
- **Fix #4**: Implement `resolve_llm()` helper with error handling
- **Fix #5**: Add `mistral_model` and LangGraph config fields
- **Fix #6**: Complete override validation with type checking and logging
- **Fix #7**: Fix checkpointer connection string with URL encoding
- **Fix #8**: Proper error handling in schema creation
- **Fix #9**: Add error handling to reply function
- **Fix #10**: Create `exceptions.py` module with all exception types
- **Fix #13**: Verify dependency versions before adding
- **Fix #14**: Add configuration validation function
- **Fix #15**: Implement error handling strategy

---

## Implementation Steps

### 1.1 Dependencies & Configuration (30 minutes)

#### 1.1.1 Verify Package Versions

**Action**: Check actual versions available on PyPI before adding dependencies.

```bash
# Verify each package exists and check latest versions
uv add --dry-run langgraph
uv add --dry-run langgraph-checkpoint-postgres
uv add --dry-run langchain-mistralai
uv add --dry-run langchain-openai
uv add --dry-run langchain-core
uv add --dry-run docling
```

**Expected Output**: Version information for each package

**Note**: The versions in pyproject.toml below are estimates. Update them based on `--dry-run` output.

#### 1.1.2 Add Dependencies to pyproject.toml

**File**: `pyproject.toml`

**Action**: Add the following to `[project.dependencies]`:

```toml
dependencies = [
    # ... existing dependencies ...
    "langgraph>=0.2.60,<0.3.0",
    "langgraph-checkpoint-postgres>=0.0.12,<0.1.0",
    "langchain-mistralai>=0.2.0,<0.3.0",
    "langchain-openai>=0.2.0,<0.3.0",
    "langchain-core>=0.3.0,<0.4.0",
    "docling>=1.15.0,<2.0.0",
]
```

**Rationale**:
- `langgraph` - Core StateGraph and workflow primitives
- `langgraph-checkpoint-postgres` - Supabase-compatible checkpointing
- `langchain-mistralai` - Primary LLM integration
- `langchain-openai` - Alternative LLM for examples
- `langchain-core` - Core LangChain types
- `docling` - Advanced document processing

**Action**: Install dependencies:

```bash
uv sync
```

#### 1.1.3 Add Configuration Fields

**File**: `src/aimq/config.py`

**Action**: Add new fields to the `Config` class (Fix #5):

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

**Validation**: Import config and verify new fields exist:

```bash
uv run python -c "from aimq.config import config; print(config.mistral_model)"
```

---

### 1.2 Decorator Implementation (1 hour)

#### 1.2.1 Create Module Structure

**Action**: Create the langgraph module directory:

```bash
mkdir -p src/aimq/langgraph
touch src/aimq/langgraph/__init__.py
```

#### 1.2.2 Implement Decorators

**File**: `src/aimq/langgraph/decorators.py`

**Action**: Create file with complete decorator implementations:

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
    state_class: type[dict] | None = None,  # Fix #2: use type[dict]
    checkpointer: bool = False,
):
    """
    Decorator for defining reusable LangGraph workflows.

    Returns a factory function that creates configured workflow instances.

    Args:
        state_class: Optional dict subclass defining workflow state
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
    state_class: type[dict] | None = None,  # Fix #2: use type[dict]
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

            # Process LLM using resolve_llm helper (Fix #4)
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

#### 1.2.3 Update Module Exports

**File**: `src/aimq/langgraph/__init__.py`

**Action**: Export decorators:

```python
"""
LangGraph integration for AIMQ.

Provides @workflow and @agent decorators for defining reusable LangGraph components.
"""

from aimq.langgraph.decorators import workflow, agent

__all__ = ["workflow", "agent"]
```

**Validation**: Test import:

```bash
uv run python -c "from aimq.langgraph import workflow, agent; print('Decorators imported successfully')"
```

---

### 1.3 Base Classes (1 hour)

**File**: `src/aimq/langgraph/base.py`

**Action**: Create internal base classes with complete override processing:

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
        """Process job-level overrides with security validation (Fix #6).

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

**Validation**: Test import:

```bash
uv run python -c "from aimq.langgraph.base import _AgentBase, _WorkflowBase; print('Base classes imported')"
```

---

### 1.4 Utility Functions (1 hour)

**File**: `src/aimq/langgraph/utils.py`

**Action**: Create utility functions with complete error handling (Fix #4, Fix #9):

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
    """Get default LLM from configuration with caching (Fix #5).

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
    """Resolve LLM parameter to BaseChatModel instance (Fix #4).

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
    """Default reply function: enqueues responses to process_agent_response queue (Fix #9).

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

**Validation**: Test import and basic functionality:

```bash
uv run python -c "
from aimq.langgraph.utils import resolve_llm, get_default_llm, default_reply_function
print('Utils imported successfully')
"
```

---

### 1.5 State Definitions (30 minutes)

**File**: `src/aimq/langgraph/states.py`

**Action**: Create state classes with proper type annotations (Fix #3):

```python
"""Standard state definitions for workflows and agents."""

from typing import TypedDict, Annotated, Any, NotRequired, Sequence
from operator import add
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Standard state for agents (Fix #3).

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
    """Standard state for workflows (Fix #3).

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """
    # Required fields
    input: dict                                      # Original input
    errors: Annotated[list[str], add]                # Collected errors

    # Optional fields (use NotRequired)
    current_step: NotRequired[str]                   # Current step name
    step_results: Annotated[list[dict], add]         # Results from each step (use NotRequired if optional)
    final_output: NotRequired[dict]                  # Final result
    metadata: NotRequired[dict[str, Any]]            # Custom metadata
```

**Validation**: Test import and type checking:

```bash
uv run python -c "
from aimq.langgraph.states import AgentState, WorkflowState
print('States imported successfully')
print(f'AgentState fields: {AgentState.__annotations__.keys()}')
print(f'WorkflowState fields: {WorkflowState.__annotations__.keys()}')
"
```

---

### 1.6 Exception Types (30 minutes)

**File**: `src/aimq/langgraph/exceptions.py`

**Action**: Create comprehensive exception hierarchy (Fix #10):

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

**Validation**: Test import:

```bash
uv run python -c "
from aimq.langgraph.exceptions import (
    LangGraphError, CheckpointerError, LLMResolutionError,
    StateValidationError, OverrideSecurityError, ToolValidationError
)
print('All exceptions imported successfully')
"
```

---

### 1.7 Checkpointing (1.5 hours)

**File**: `src/aimq/langgraph/checkpoint.py`

**Action**: Create Supabase-backed checkpointing with proper error handling (Fix #7, Fix #8):

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
    """Build PostgreSQL connection string from Supabase config (Fix #7).

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

    # URL-encode password to handle special characters (Fix #7)
    encoded_password = quote_plus(password)

    # Build connection string
    conn_string = (
        f"postgresql://postgres:{encoded_password}"
        f"@db.{project_ref}.supabase.co:5432/postgres"
    )

    logger.info("Built Supabase PostgreSQL connection string")
    return conn_string


def _ensure_schema() -> None:
    """Ensure langgraph schema and tables exist (Fix #8).

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

**Validation**: Test connection string building (without actually connecting):

```bash
uv run python -c "
from aimq.langgraph.checkpoint import _build_connection_string, CheckpointerError
import os

# Test with mock env vars
os.environ['SUPABASE_URL'] = 'https://test-project.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key-with-special-chars!@#'

try:
    conn_str = _build_connection_string()
    print('Connection string built successfully')
    assert 'test-key-with-special-chars' in conn_str or '%' in conn_str
    print('URL encoding working')
except CheckpointerError as e:
    print(f'Error: {e}')
"
```

---

## Testing & Validation

### Unit Tests to Create

**File**: `tests/aimq/langgraph/test_decorators.py`

Basic smoke tests:

```python
from aimq.langgraph import workflow, agent
from langgraph.graph import StateGraph


def test_workflow_decorator():
    """Test @workflow decorator creates factory."""
    @workflow()
    def my_workflow(graph, config):
        return graph

    # Should return factory function
    assert callable(my_workflow)

    # Should create instance
    instance = my_workflow()
    assert instance is not None


def test_agent_decorator():
    """Test @agent decorator creates factory."""
    @agent()
    def my_agent(graph, config):
        return graph

    # Should return factory function
    assert callable(my_agent)

    # Should create instance
    instance = my_agent()
    assert instance is not None
```

### Manual Validation Checklist

- [ ] All modules import without errors
- [ ] Dependencies installed successfully
- [ ] Config fields accessible
- [ ] Decorators create factory functions
- [ ] Base classes instantiate
- [ ] resolve_llm() handles all input types
- [ ] State classes have correct fields with NotRequired
- [ ] Exception types importable
- [ ] Checkpointer connection string builds correctly

---

## Definition of Done

### Code Complete

- [ ] All 7 files created (`__init__.py`, `decorators.py`, `base.py`, `utils.py`, `states.py`, `exceptions.py`, `checkpoint.py`)
- [ ] All functions implemented with docstrings
- [ ] All critical fixes (#2-10, #13-15) applied
- [ ] Type annotations correct (`type[dict]`, `NotRequired`)
- [ ] Error handling comprehensive

### Dependencies

- [ ] Dependencies verified on PyPI (Fix #13)
- [ ] All packages added to pyproject.toml with correct versions
- [ ] `uv sync` successful
- [ ] No import errors

### Configuration

- [ ] Config fields added to src/aimq/config.py (Fix #5)
- [ ] Fields accessible via config singleton
- [ ] Environment variables work

### Validation

- [ ] All imports successful
- [ ] Basic smoke tests pass
- [ ] No syntax errors
- [ ] Type checker (mypy) passes
- [ ] Linter (flake8) passes

### Documentation

- [ ] All functions have docstrings
- [ ] Examples included in docstrings
- [ ] Error types documented
- [ ] Configuration options documented

---

## Common Pitfalls

### Type Annotations

**Pitfall**: Using `Type[TypedDict]` which is invalid syntax

**Solution**: Use `type[dict]` (Fix #2)
```python
# Wrong
state_class: Type[TypedDict] | None = None

# Correct
state_class: type[dict] | None = None
```

### Missing NotRequired

**Pitfall**: Optional fields in TypedDict without NotRequired causes type errors

**Solution**: Wrap optional fields (Fix #3)
```python
# Wrong
class AgentState(TypedDict):
    current_tool: str | None  # Still required!

# Correct
class AgentState(TypedDict):
    current_tool: NotRequired[str]  # Actually optional
```

### LLM String Conversion

**Pitfall**: No error handling when converting string to LLM

**Solution**: Use resolve_llm() helper (Fix #4)
```python
# Wrong
llm = ChatMistralAI(model=llm_param)  # Fails if llm_param is None or invalid

# Correct
llm = resolve_llm(llm_param, default_model="mistral-large-latest")
```

### Checkpointer Connection String

**Pitfall**: Special characters in password break connection string

**Solution**: URL-encode password (Fix #7)
```python
# Wrong
conn_str = f"postgresql://postgres:{password}@..."  # Breaks with !@#$

# Correct
from urllib.parse import quote_plus
encoded = quote_plus(password)
conn_str = f"postgresql://postgres:{encoded}@..."
```

### Error Handling

**Pitfall**: Bare `except: pass` swallows all errors including critical ones

**Solution**: Catch specific exceptions and log (Fix #8)
```python
# Wrong
try:
    create_schema()
except:
    pass  # Swallows everything!

# Correct
try:
    create_schema()
except APIError as e:
    if "already exists" in str(e):
        logger.debug("Schema exists")
    else:
        logger.error(f"Failed: {e}")
        raise CheckpointerError(...) from e
```

---

## Next Phase

Once Phase 1 is complete:
- [ ] Update PROGRESS.md with completion status
- [ ] Move to **Phase 2: Built-in Agents** ([PHASE2.md](./PHASE2.md))
- [ ] ReActAgent and PlanExecuteAgent implementations will use this infrastructure

---

**Phase Owner**: Implementation Team
**Started**: ___________
**Completed**: ___________
**Actual Hours**: ___________
