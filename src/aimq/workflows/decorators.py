"""Decorator for defining LangGraph workflows."""

from functools import wraps
from typing import Any, Callable

from langgraph.graph import StateGraph

from aimq.memory.checkpoint import get_checkpointer
from aimq.workflows.states import WorkflowState


class _WorkflowBase:
    """
    Internal base class used by @workflow decorator.

    Similar to _AgentBase but for workflows.
    """

    def __init__(self, builder_func: Callable, config: dict[str, Any]):
        self.builder_func = builder_func
        self.config = config
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the workflow's StateGraph."""
        state_class = self.config.get("state_class") or WorkflowState
        graph = StateGraph(state_class)

        return self.builder_func(graph, self.config)

    def _compile(self):
        """Compile graph with optional checkpointing."""
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


def workflow(
    state_class: type[dict] | None = None,
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
            config = {"state_class": state_class, "checkpointer": checkpointer, **kwargs}

            return _WorkflowBase(builder_func, config)

        return factory

    return decorator
