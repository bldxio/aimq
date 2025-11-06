"""Base class for built-in workflows."""

from langgraph.graph import StateGraph

from aimq.langgraph.checkpoint import get_checkpointer


class BaseWorkflow:
    """Base class for built-in workflows.

    Provides graph building, compilation, and Runnable interface for workflows.
    Supports optional checkpointing for state persistence.
    """

    def __init__(self, checkpointer: bool = False):
        """Initialize workflow.

        Args:
            checkpointer: Enable state persistence (default: False)
        """
        self.checkpointer_enabled = checkpointer

        # Build and compile graph
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the workflow's graph. Override in subclasses.

        Returns:
            StateGraph instance with nodes and edges defined

        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _build_graph()")

    def _compile(self):
        """Compile the graph with optional checkpointing.

        Returns:
            Compiled graph ready for execution
        """
        checkpointer = get_checkpointer() if self.checkpointer_enabled else None
        return self._graph.compile(checkpointer=checkpointer)

    def invoke(self, input: dict, config: dict | None = None):
        """Invoke the workflow (implements Runnable interface).

        Args:
            input: Input data for the workflow
            config: Optional runtime configuration

        Returns:
            Final state after workflow execution
        """
        return self._compiled.invoke(input, config)

    def stream(self, input: dict, config: dict | None = None):
        """Stream workflow execution (implements Runnable interface).

        Args:
            input: Input data for the workflow
            config: Optional runtime configuration

        Yields:
            State updates as workflow executes
        """
        return self._compiled.stream(input, config)
