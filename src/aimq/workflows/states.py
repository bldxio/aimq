"""Standard state definitions for workflows."""

from operator import add
from typing import Annotated, Any, NotRequired, TypedDict


class WorkflowState(TypedDict):
    """Standard state for workflows (Fix #3).

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """

    input: dict
    errors: Annotated[list[str], add]

    current_step: NotRequired[str]
    step_results: NotRequired[Annotated[list[dict], add]]
    final_output: NotRequired[dict]
    metadata: NotRequired[dict[str, Any]]
