"""Standard state definitions for agents."""

from operator import add
from typing import Annotated, Any, NotRequired, Sequence, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Standard state for agents (Fix #3).

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """

    messages: Annotated[Sequence[BaseMessage], add]
    tools: list[str]
    iteration: int
    errors: Annotated[list[str], add]

    current_tool: NotRequired[str]
    tool_input: NotRequired[dict]
    tool_output: NotRequired[Any]
    final_answer: NotRequired[str]

    tenant_id: NotRequired[str]

    metadata: NotRequired[dict[str, Any]]
