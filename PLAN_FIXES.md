# PLAN.md Critical Fixes Document

**Created**: 2025-10-30
**Status**: Review Required
**Priority**: Must address before Phase 1 implementation

This document summarizes critical issues identified in the architectural and Python implementation reviews of PLAN.md. Each issue includes the problem, location, and specific fix needed.

---

## ✅ COMPLETED FIXES

### 1. BaseAgent Naming Collision
**Status**: ✅ FIXED
**Problem**: Two different `BaseAgent` classes caused naming collision
**Solution**: Renamed internal bases to `_AgentBase` and `_WorkflowBase`
**Files**: PLAN.md (decorators and base classes sections)

---

## 🔴 CRITICAL ISSUES (Must Fix Before Implementation)

### 2. Type Annotations - Invalid TypedDict Usage
**Priority**: CRITICAL
**Location**: `decorators.py` lines 316, 370, 387

**Problem**:
```python
# WRONG - Type[TypedDict] is invalid syntax
state_class: Type[TypedDict] | None = None
```

**Fix**:
```python
from typing import Any

# Option 1: Generic type
state_class: type[dict] | None = None

# Option 2: Any (more permissive)
state_class: Type[Any] | None = None

# Option 3: Protocol (best for validation)
from typing import Protocol

class StateProtocol(Protocol):
    """Protocol for state dictionaries."""
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...

state_class: Type[StateProtocol] | None = None
```

**Recommendation**: Use Option 1 (`type[dict]`) for simplicity

---

### 3. Missing NotRequired in State Definitions
**Priority**: CRITICAL
**Location**: `states.py` lines 694-712, 730-740

**Problem**:
```python
class AgentState(TypedDict):
    messages: Annotated[list[dict], add]
    tools: list[str]
    current_tool: str | None  # ❌ Should be NotRequired
    tool_input: dict | None   # ❌ Should be NotRequired
    # ... all optional fields need NotRequired
```

**Fix**:
```python
from typing import TypedDict, Annotated, NotRequired, Any, Sequence
from operator import add
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Standard state for agents.

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """
    # Required fields
    messages: Annotated[Sequence[BaseMessage], add]
    tools: list[str]
    iteration: int
    errors: Annotated[list[str], add]

    # Optional fields (use NotRequired)
    current_tool: NotRequired[str]
    tool_input: NotRequired[dict]
    tool_output: NotRequired[Any]
    final_answer: NotRequired[str]

    # Checkpointing fields (required if memory=True)
    thread_id: NotRequired[str]
    checkpoint_id: NotRequired[str]

    # Multi-tenancy
    tenant_id: NotRequired[str]

    # Extensibility
    metadata: NotRequired[dict[str, Any]]
```

**Key Changes**:
1. Use `Sequence[BaseMessage]` instead of `list[dict]` for LangChain compatibility
2. Add `NotRequired` to all optional fields
3. Add missing `thread_id` (required for checkpointing)
4. Add `metadata` for extensibility

---

### 4. Missing _resolve_llm() Helper Function
**Priority**: CRITICAL
**Location**: `decorators.py` lines 441-456, `utils.py` new section

**Problem**: String-to-LLM conversion has no error handling, type validation, or import guards

**Fix**: Add new helper function in `utils.py`:

```python
from langchain_core.language_models import BaseChatModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class LLMResolutionError(Exception):
    """Raised when LLM resolution fails."""
    pass

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
```

**Update decorator to use it**:
```python
# In @agent decorator factory function
from aimq.langgraph.utils import resolve_llm

llm_instance = resolve_llm(
    override_kwargs.get("llm", llm),
    default_model=override_kwargs.get("default_model", "mistral-large-latest")
)
```

---

### 5. Missing Config Field: mistral_model
**Priority**: CRITICAL
**Location**: `config.py`, `utils.py` line 650

**Problem**: `utils.py` references `config.MISTRAL_MODEL` but field doesn't exist

**Fix**: Add to Config class:
```python
# src/aimq/config.py
class Config(BaseSettings):
    # ... existing fields ...

    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    mistral_model: str = Field(
        default="mistral-large-latest",
        alias="MISTRAL_MODEL",
        description="Default Mistral model for LangGraph agents"
    )

    # Additional LangGraph config
    langgraph_checkpoint_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_CHECKPOINT_ENABLED"
    )
    langgraph_max_iterations: int = Field(
        default=20,
        alias="LANGGRAPH_MAX_ITERATIONS"
    )
```

**Update get_default_llm()**:
```python
def get_default_llm(model: str | None = None) -> BaseChatModel:
    """Get default LLM from configuration with caching.

    Args:
        model: Override model name (optional)

    Returns:
        ChatMistralAI instance (cached singleton per model)
    """
    from langchain_mistralai import ChatMistralAI
    from aimq.config import config

    model_name = model or config.mistral_model

    # Cache LLM instances to prevent connection pool exhaustion
    cache_key = f"mistral_{model_name}"
    if cache_key not in _llm_cache:
        _llm_cache[cache_key] = ChatMistralAI(
            model=model_name,
            api_key=config.mistral_api_key,
            temperature=0.1,
        )

    return _llm_cache[cache_key]

# Module-level cache
_llm_cache: dict[str, BaseChatModel] = {}
```

---

### 6. Override Processing Needs Validation
**Priority**: CRITICAL
**Location**: `base.py` `_process_overrides()` lines 540-592

**Problem**: No type validation, no range checking, no proper logging

**Fix**: Complete rewrite with validation:

```python
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
```

---

### 7. Checkpointer Connection String Issues
**Priority**: CRITICAL
**Location**: `checkpoint.py` lines 739-748

**Problem**:
- Regex can crash with AttributeError
- Password not URL-encoded (special chars break)
- No validation

**Fix**:
```python
from urllib.parse import quote_plus
import re
import logging

logger = logging.getLogger(__name__)

class CheckpointerError(Exception):
    """Raised when checkpointer cannot be configured."""
    pass

def _build_connection_string() -> str:
    """Build PostgreSQL connection string from Supabase config.

    Returns:
        PostgreSQL connection URL with encoded credentials

    Raises:
        CheckpointerError: If Supabase config is invalid or missing

    Examples:
        postgresql://postgres:encoded_pw@db.project.supabase.co:5432/postgres
    """
    from aimq.config import config

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
```

---

### 8. Checkpointer Schema Creation Error Handling
**Priority**: CRITICAL
**Location**: `checkpoint.py` lines 751-783

**Problem**: Bare `except: pass` swallows all errors including connection failures

**Fix**:
```python
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
    import logging
    from postgrest.exceptions import APIError
    from aimq.clients.supabase import get_supabase_client

    logger = logging.getLogger(__name__)
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

---

### 9. Reply Function Missing Error Handling
**Priority**: HIGH
**Location**: `utils.py` `default_reply_function` lines 656-681

**Problem**: No error handling - failures crash agent execution

**Fix**:
```python
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
    import logging
    from datetime import datetime

    logger = logging.getLogger(__name__)

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

---

### 10. Missing Exception Types Module
**Priority**: HIGH
**Location**: New file needed

**Fix**: Create new section in PLAN.md:

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

**Update imports throughout**:
```python
from aimq.langgraph.exceptions import (
    CheckpointerError,
    LLMResolutionError,
    StateValidationError,
    OverrideSecurityError,
)
```

---

## 🟡 HIGH PRIORITY ISSUES

### 11. Missing Logger Integration
**Priority**: HIGH
**Location**: Throughout agent/workflow implementations

**Problem**: Agents don't receive or use AIMQ's Logger infrastructure

**Fix**: Add `logger` parameter to decorators and pass through config:

```python
from aimq.logger import Logger

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
    logger: Logger | None = None,  # NEW PARAMETER
):
    """Decorator for defining reusable LangGraph agents."""

    def decorator(builder_func: Callable) -> Callable:
        @wraps(builder_func)
        def factory(**override_kwargs) -> _AgentBase:
            # ... existing code ...

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
                "logger": logger or Logger(),  # Provide default logger
                **override_kwargs
            }

            return _AgentBase(builder_func, config)

        return factory

    return decorator
```

**Usage in nodes**:
```python
def reasoning_node(state):
    logger = config["logger"]
    logger.info("Starting reasoning step", {"iteration": state["iteration"]})

    try:
        # ... reasoning logic ...
        logger.info("Reasoning complete", {"decision": decision})
    except Exception as e:
        logger.error("Reasoning failed", {"error": str(e)})
        raise
```

---

### 12. Missing Tool Input Validation
**Priority**: HIGH
**Location**: New section needed + ReActAgent

**Problem**: Tool inputs from LLM not validated - security risk

**Fix**: Add new utility class:

**File**: `src/aimq/langgraph/validation.py`

```python
"""
Tool input validation for security.

Validates tool inputs before execution to prevent injection attacks.
"""

from typing import Any, Dict
from langchain.tools import BaseTool
from pydantic import ValidationError
import logging

from aimq.langgraph.exceptions import ToolValidationError

logger = logging.getLogger(__name__)

class ToolInputValidator:
    """Validates tool inputs against tool schemas for security."""

    def validate(self, tool: BaseTool, input_data: dict) -> dict:
        """Validate tool input against tool's args_schema.

        Args:
            tool: LangChain tool to validate against
            input_data: Input data from LLM or user

        Returns:
            Validated input dict

        Raises:
            ToolValidationError: If validation fails

        Examples:
            >>> validator = ToolInputValidator()
            >>> validated = validator.validate(read_file_tool, {"path": "file.txt"})
        """
        tool_name = tool.name

        try:
            # Use Pydantic schema validation if available
            if hasattr(tool, 'args_schema') and tool.args_schema:
                validated = tool.args_schema(**input_data)
                logger.debug(f"Tool '{tool_name}' input validated")
                return validated.dict()
            else:
                # No schema - log warning and pass through
                logger.warning(
                    f"Tool '{tool_name}' has no args_schema, "
                    f"input validation skipped"
                )
                return input_data

        except ValidationError as e:
            logger.error(
                f"Tool '{tool_name}' input validation failed: {e}",
                extra={"tool": tool_name, "input": input_data}
            )
            raise ToolValidationError(
                f"Invalid input for tool '{tool_name}': {e}"
            ) from e

        except Exception as e:
            logger.error(
                f"Unexpected error validating tool '{tool_name}': {e}",
                exc_info=True
            )
            raise ToolValidationError(
                f"Tool validation failed for '{tool_name}': {e}"
            ) from e

    def validate_file_path(self, path: str, allowed_patterns: list[str] | None = None) -> None:
        """Validate file path for security.

        Prevents:
        - Path traversal attacks (../)
        - Absolute paths outside allowed directories
        - Access to sensitive system files

        Args:
            path: File path to validate
            allowed_patterns: List of allowed path patterns (glob style)

        Raises:
            ToolValidationError: If path is invalid or unauthorized
        """
        import os
        from pathlib import Path

        # Normalize path
        normalized = os.path.normpath(path)

        # Check for path traversal
        if ".." in normalized:
            raise ToolValidationError(
                f"Path traversal not allowed: {path}"
            )

        # Check if absolute path
        if os.path.isabs(normalized):
            # Only allow if matches patterns
            if allowed_patterns:
                from fnmatch import fnmatch
                if not any(fnmatch(normalized, pattern) for pattern in allowed_patterns):
                    raise ToolValidationError(
                        f"Absolute path not in allowed patterns: {path}"
                    )

        # Check for sensitive files
        sensitive = ["/etc/passwd", "/etc/shadow", ".ssh/", ".env"]
        if any(s in normalized for s in sensitive):
            raise ToolValidationError(
                f"Access to sensitive file not allowed: {path}"
            )

        logger.debug(f"File path validated: {normalized}")
```

**Update ReActAgent to use validation**:
```python
def _action_node(self, state: AgentState) -> AgentState:
    """Action node: execute the chosen tool with validation."""
    from aimq.langgraph.validation import ToolInputValidator
    from aimq.langgraph.exceptions import ToolValidationError

    tool_name = state["current_tool"]
    tool_input = state["tool_input"]
    logger = self.config["logger"]

    # Find tool
    tool = next((t for t in self.tools if t.name == tool_name), None)
    if not tool:
        error_msg = f"Unknown tool: {tool_name}"
        logger.error(error_msg)
        return {
            "messages": [{"role": "system", "content": error_msg}],
            "tool_output": error_msg,
            "errors": [error_msg],
        }

    # Validate tool input
    validator = ToolInputValidator()
    try:
        validated_input = validator.validate(tool, tool_input)
        logger.info(f"Executing tool: {tool_name}", {"input": validated_input})
    except ToolValidationError as e:
        logger.error(f"Tool validation failed: {e}")
        return {
            "messages": [{"role": "system", "content": str(e)}],
            "tool_output": str(e),
            "errors": [str(e)],
        }

    # Execute tool
    try:
        result = tool.invoke(validated_input)
        logger.info(f"Tool execution successful: {tool_name}")
        return {
            "messages": [{"role": "system", "content": f"Tool result: {result}"}],
            "tool_output": str(result),
        }
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "messages": [{"role": "system", "content": error_msg}],
            "tool_output": error_msg,
            "errors": [str(e)],
        }
```

---

### 13. Dependencies Need Verification
**Priority**: HIGH
**Location**: Phase 1.1 Dependencies section

**Problem**: Package names and versions may be incorrect

**Action Items**:
1. Verify actual package names on PyPI
2. Check latest stable versions
3. Verify compatibility with existing dependencies

**Current (possibly incorrect)**:
```toml
"langgraph>=0.2.0,<0.3.0",
"langgraph-checkpoint-postgres>=1.0.0,<2.0.0",  # May not exist
"langchain-mistralai>=0.2.0,<0.3.0",
"langchain-openai>=0.2.0,<0.3.0",
"langchain-core>=0.3.0,<0.4.0",
"docling>=2.58.0,<3.0.0",  # Version seems high
```

**TODO**: Run these commands to verify:
```bash
uv add --dry-run langgraph
uv add --dry-run "langgraph-checkpoint-postgres"
uv add --dry-run langchain-mistralai
uv add --dry-run docling
```

**Expected corrections** (need verification):
```toml
"langgraph>=0.2.60,<0.3.0",  # Check latest 0.2.x
"langgraph-checkpoint-postgres>=0.0.12,<0.1.0",  # Different versioning scheme
"docling>=1.15.0,<2.0.0",  # Check actual latest version
```

---

### 14. Missing Configuration Validation
**Priority**: HIGH
**Location**: Decorator factory functions

**Problem**: Invalid configurations accepted without validation

**Fix**: Add validation function and call in factories:

```python
def validate_agent_config(config: dict) -> None:
    """Validate agent configuration for common errors.

    Args:
        config: Agent configuration dict

    Raises:
        ValueError: If configuration is invalid

    Examples:
        >>> validate_agent_config({"memory": True, ...})
        >>> # Raises if memory=True but checkpointer unavailable
    """
    from aimq.langgraph.exceptions import CheckpointerError
    import logging

    logger = logging.getLogger(__name__)

    # Check: Memory requires checkpointer
    if config.get("memory"):
        try:
            from aimq.langgraph.checkpoint import get_checkpointer
            get_checkpointer()  # Will raise if not configured
        except CheckpointerError as e:
            raise ValueError(
                "memory=True requires LangGraph checkpoint schema. "
                "Run: psql -f scripts/setup_langgraph_schema.sql"
            ) from e

    # Check: LLM is BaseChatModel
    llm = config.get("llm")
    if llm is not None:
        from langchain_core.language_models import BaseChatModel
        if not isinstance(llm, BaseChatModel):
            raise TypeError(
                f"llm must be BaseChatModel, got {type(llm).__name__}"
            )

    # Check: allowed_llms structure
    allowed_llms = config.get("allowed_llms")
    if allowed_llms is not None:
        if not isinstance(allowed_llms, dict):
            raise TypeError("allowed_llms must be dict[str, BaseChatModel]")

        from langchain_core.language_models import BaseChatModel
        for key, value in allowed_llms.items():
            if not isinstance(key, str):
                raise TypeError(f"allowed_llms keys must be strings, got {type(key)}")
            if not isinstance(value, BaseChatModel):
                raise TypeError(
                    f"allowed_llms['{key}'] must be BaseChatModel, "
                    f"got {type(value).__name__}"
                )

    # Check: Tools are BaseTool instances
    tools = config.get("tools", [])
    if tools:
        from langchain.tools import BaseTool
        for i, tool in enumerate(tools):
            if not isinstance(tool, BaseTool):
                raise TypeError(
                    f"tools[{i}] must be BaseTool, got {type(tool).__name__}"
                )

    # Check: reply_function is callable
    reply_fn = config.get("reply_function")
    if reply_fn is not None and not callable(reply_fn):
        raise TypeError(
            f"reply_function must be callable, got {type(reply_fn).__name__}"
        )

    logger.debug("Agent configuration validated successfully")
```

**Call in decorator**:
```python
def factory(**override_kwargs) -> _AgentBase:
    # ... build config ...

    # Validate configuration
    validate_agent_config(config)

    return _AgentBase(builder_func, config)
```

---

### 15. Missing Error Handling Strategy
**Priority**: HIGH
**Location**: New section needed in PLAN.md

**Add new section after Phase 7**:

## Error Handling Strategy

### Error Categories

**1. Retryable Errors** (Transient failures)
- Network timeouts
- Rate limit errors (429)
- Database connection issues
- Checkpoint save failures

**2. Non-Retryable Errors** (Permanent failures)
- Invalid configuration
- Tool validation failures
- Authentication errors (401, 403)
- State validation errors

**3. Recoverable Errors** (Can continue with degradation)
- Reply function failures (log and continue)
- Optional tool failures (skip and continue)
- Logging failures (print to stderr)

### Error Handling Patterns

**Pattern 1: Error State Node**
```python
@agent(tools=[...], error_handler=handle_error)
def resilient_agent(graph, config):
    def handle_error(state):
        """Handle errors gracefully."""
        errors = state.get("errors", [])
        logger = config["logger"]

        # Log all errors
        for error in errors:
            logger.error(f"Agent error: {error}")

        # Attempt recovery or graceful shutdown
        return {
            "final_answer": f"Failed after {state['iteration']} iterations. Errors: {errors}",
            "errors": errors,
        }

    # Add error handling to graph
    graph.add_node("error_handler", handle_error)

    # Route errors to handler
    graph.add_conditional_edges(
        "reason",
        lambda s: "error_handler" if s.get("errors") else "act",
        {"error_handler": END, "act": "act"}
    )
```

**Pattern 2: Retry with Backoff**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class _AgentBase:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def invoke(self, input: dict, config: dict | None = None):
        """Invoke with automatic retry for transient failures."""
        return super().invoke(input, config)
```

**Pattern 3: Circuit Breaker**
```python
class _AgentBase:
    def __init__(self, builder_func, config):
        self.failure_count = 0
        self.max_failures = config.get("max_failures", 5)
        self.circuit_open = False
        # ... existing init ...

    def invoke(self, input, config=None):
        if self.circuit_open:
            raise RuntimeError(
                f"Circuit breaker open after {self.failure_count} failures. "
                f"Wait before retrying."
            )

        try:
            result = self._compiled.invoke(input, config)
            self.failure_count = 0  # Reset on success
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.max_failures:
                self.circuit_open = True
            raise
```

---

## 🟢 MEDIUM PRIORITY IMPROVEMENTS

### 16. LLM Client Caching
Already addressed in Fix #5 (get_default_llm with caching)

### 17. Lazy Graph Compilation
**Location**: `base.py` __init__ methods

**Current**: Compiles immediately
**Improvement**: Use `@cached_property` for lazy compilation

```python
from functools import cached_property

class _AgentBase:
    def __init__(self, builder_func: Callable, config: Dict[str, Any]):
        self.builder_func = builder_func
        self.config = config
        # Don't compile immediately

    @cached_property
    def _graph(self) -> StateGraph:
        """Build graph (lazy, cached)."""
        return self._build_graph()

    @cached_property
    def _compiled(self):
        """Compile graph (lazy, cached)."""
        return self._compile()
```

### 18. Add Metrics/Observability Hooks
**Location**: New section in PLAN.md

```python
class _AgentBase:
    def invoke(self, input, config=None):
        import time

        start_time = time.time()
        metrics = {
            "agent_name": self.__class__.__name__,
            "start_time": start_time,
        }

        try:
            result = self._compiled.invoke(input, config)

            metrics["duration"] = time.time() - start_time
            metrics["success"] = True
            metrics["tokens"] = result.get("usage", {})

            self._record_metrics(metrics)
            return result

        except Exception as e:
            metrics["duration"] = time.time() - start_time
            metrics["success"] = False
            metrics["error"] = str(e)

            self._record_metrics(metrics)
            raise

    def _record_metrics(self, metrics: dict):
        """Record metrics (override for custom telemetry)."""
        logger = self.config.get("logger")
        if logger:
            logger.info("Agent execution metrics", metrics)
```

---

## 📋 SUMMARY

### Critical Issues (Must Fix): 14
1. ✅ BaseAgent naming collision (FIXED)
2. Type annotations invalid
3. Missing NotRequired in states
4. Missing _resolve_llm() helper
5. Missing config fields
6. Override processing needs validation
7. Checkpointer connection string fragile
8. Checkpointer error handling broken
9. Reply function no error handling
10. Missing exception types
11. Missing logger integration
12. Missing tool input validation
13. Dependencies need verification
14. Missing configuration validation
15. Missing error handling strategy

### Estimated Fix Time
- **Critical issues**: 6-8 hours
- **High priority**: 3-4 hours
- **Medium priority**: 2-3 hours
- **Total**: 11-15 hours

### Recommended Approach
1. Fix critical issues #2-10 (type safety, validation, error handling)
2. Verify dependencies (#13)
3. Add logger integration (#11)
4. Add tool validation (#12)
5. Add config validation (#14)
6. Document error strategy (#15)
7. Implement in code during Phase 1

### Next Steps
1. Review this document
2. Prioritize which fixes to apply to PLAN.md
3. Decide: Fix in PLAN.md vs fix during implementation
4. Begin Phase 1 with fixes in place
