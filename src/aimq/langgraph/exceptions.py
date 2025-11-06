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
