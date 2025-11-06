"""Standard state definitions for workflows and agents."""

from operator import add
from typing import Annotated, Any, NotRequired, Sequence, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Standard state for agents (Fix #3).

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """

    # Required fields
    messages: Annotated[Sequence[BaseMessage], add]  # Conversation history
    tools: list[str]  # Available tool names
    iteration: int  # Iteration counter (prevent infinite loops)
    errors: Annotated[list[str], add]  # Collected errors

    # Optional fields (use NotRequired)
    current_tool: NotRequired[str]  # Tool being executed
    tool_input: NotRequired[dict]  # Input for current tool
    tool_output: NotRequired[Any]  # Output from tool
    final_answer: NotRequired[str]  # Agent's final response

    # Multi-tenancy
    tenant_id: NotRequired[str]  # Tenant ID for isolation

    # Extensibility
    metadata: NotRequired[dict[str, Any]]  # Custom metadata


class WorkflowState(TypedDict):
    """Standard state for workflows (Fix #3).

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """

    # Required fields
    input: dict  # Original input
    errors: Annotated[list[str], add]  # Collected errors

    # Optional fields (use NotRequired)
    current_step: NotRequired[str]  # Current step name
    step_results: NotRequired[Annotated[list[dict], add]]  # Results from steps
    final_output: NotRequired[dict]  # Final result
    metadata: NotRequired[dict[str, Any]]  # Custom metadata
