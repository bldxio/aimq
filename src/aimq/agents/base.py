"""Base class for built-in agents."""

from langchain.tools import BaseTool
from langgraph.graph import StateGraph

from aimq.langgraph.checkpoint import get_checkpointer


class BaseAgent:
    """Base class for built-in agents.

    Provides common functionality for agent implementations:
    - Graph building and compilation
    - Checkpointing integration
    - Runnable interface (invoke, stream)

    Subclasses should override _build_graph() to define their specific logic.
    """

    def __init__(
        self,
        tools: list[BaseTool],
        system_prompt: str,
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
    ):
        """Initialize agent.

        Args:
            tools: List of LangChain tools the agent can use
            system_prompt: Agent instructions
            llm: LLM model name (default: "mistral-large-latest")
            temperature: LLM temperature (default: 0.1)
            memory: Enable conversation memory (default: False)
        """
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
        raise NotImplementedError(f"{self.__class__.__name__} must implement _build_graph()")

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
