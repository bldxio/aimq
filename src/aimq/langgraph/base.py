"""
Base classes used internally by decorators.

Provides shared functionality for graph compilation, override processing,
and execution.

These classes are internal implementation details and should not be used
directly.
"""

import logging
from typing import Any, Callable

from langgraph.graph import StateGraph

logger = logging.getLogger(__name__)


class _AgentBase:
    """
    Internal base class used by @agent decorator.

    Handles graph compilation, job-level overrides, and Runnable interface.
    """

    def __init__(self, builder_func: Callable, config: dict[str, Any]):
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
        from aimq.langgraph.states import AgentState

        state_class = self.config.get("state_class", AgentState)
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

    def _process_overrides(  # noqa: C901
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
                    f"LLM override must be string, got {type(llm_key).__name__}, " f"ignoring"
                )
            elif not allowed_llms:
                logger.warning("LLM override attempted but allowed_llms not configured")
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
                    f"system_prompt must be string, got "
                    f"{type(prompt_override).__name__}, ignoring"
                )
            elif not self.config.get("allow_system_prompt"):
                logger.warning(
                    "system_prompt override attempted but allow_system_prompt=False " "(security)"
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
                    f"temperature must be numeric, got {type(temp_override).__name__}, " f"ignoring"
                )
            elif not 0.0 <= temp_override <= 2.0:
                # Clamp to valid range
                clamped = max(0.0, min(2.0, float(temp_override)))
                runtime_config["temperature"] = clamped
                applied_overrides.append(f"temperature={clamped}")
                logger.warning(
                    f"temperature {temp_override} out of range [0.0, 2.0], " f"clamped to {clamped}"
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

    def __init__(self, builder_func: Callable, config: dict[str, Any]):
        self.builder_func = builder_func
        self.config = config
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the workflow's StateGraph."""
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
