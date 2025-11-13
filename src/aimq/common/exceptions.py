"""
Custom exceptions for agent and workflow functionality.

Provides specific exception types for better error handling and debugging.
"""


class GraphError(Exception):
    """Base exception for all graph-related errors."""

    pass


class GraphBuildError(GraphError):
    """Raised when graph building fails.

    Examples:
        - Invalid node configuration
        - Missing required nodes
        - Invalid edge connections
    """

    pass


class GraphCompileError(GraphError):
    """Raised when graph compilation fails.

    Examples:
        - Circular dependencies
        - Unreachable nodes
        - Invalid state schema
    """

    pass


class StateValidationError(GraphError):
    """Raised when state validation fails.

    Examples:
        - Missing required state fields
        - Invalid state type
        - State doesn't extend AgentState
    """

    pass


class CheckpointerError(GraphError):
    """Raised when checkpointer configuration or operation fails.

    Examples:
        - Invalid Supabase connection
        - Schema not initialized
        - Checkpoint save/load failure
    """

    pass


class OverrideSecurityError(GraphError):
    """Raised when job override violates security policy.

    Examples:
        - LLM key not in allowed_llms
        - system_prompt override when allow_system_prompt=False
        - Invalid override value type
    """

    pass


class LLMResolutionError(GraphError):
    """Raised when LLM resolution fails.

    Examples:
        - Invalid LLM parameter type
        - Failed to create LLM instance
        - Missing required LangChain package
    """

    pass


class ToolValidationError(GraphError):
    """Raised when tool input validation fails.

    Examples:
        - Tool input doesn't match schema
        - Unauthorized file path access
        - SQL injection attempt detected
    """

    pass
