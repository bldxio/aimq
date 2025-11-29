"""Decorator for defining LangGraph agents."""

import logging
from functools import wraps
from typing import Any, Callable

from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph

from aimq.agents.states import AgentState
from aimq.common.llm import default_reply_function, resolve_llm
from aimq.memory.checkpoint import get_checkpointer

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
        state_class = self.config.get("state_class") or AgentState
        graph = StateGraph(state_class)

        return self.builder_func(graph, self.config)

    def _compile(self):
        """Compile graph with optional checkpointing."""
        checkpointer = None
        if self.config.get("memory"):
            checkpointer = get_checkpointer()

        return self._graph.compile(checkpointer=checkpointer)

    def invoke(self, input: dict, config: dict | None = None):
        """
        Invoke the agent (implements Runnable interface).

        Processes job-level overrides before execution.
        """
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

        applied_overrides = []

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

        if "temperature" in processed_input:
            temp_override = processed_input.pop("temperature")

            if not isinstance(temp_override, (int, float)):
                logger.warning(
                    f"temperature must be numeric, got {type(temp_override).__name__}, " f"ignoring"
                )
            elif not 0.0 <= temp_override <= 2.0:
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

        if applied_overrides:
            logger.info(f"Applied overrides: {', '.join(applied_overrides)}")
        else:
            logger.debug("No overrides applied")

        return processed_input, runtime_config


def agent(
    tools: list[BaseTool] | None = None,
    system_prompt: str | None = None,
    llm: BaseChatModel | str | None = None,
    temperature: float = 0.1,
    memory: bool = False,
    state_class: type[dict] | None = None,
    reply_function: Callable[[str, dict], None] | None = None,
    allowed_llms: dict[str, BaseChatModel] | None = None,
    allow_system_prompt: bool = False,
):
    """
    Decorator for defining reusable LangGraph agents.

    Provides agent-specific features like tools, prompts, LLM config, memory,
    and security. Returns a factory function that creates configured agent
    instances.

    Args:
        tools: List of LangChain tools the agent can use
        system_prompt: Agent instructions/persona
        llm: LangChain LLM object, string (model name), or None for default
        temperature: LLM temperature (default: 0.1)
        memory: Enable conversation memory and checkpointing (default: False)
        state_class: Custom state class (must extend AgentState)
        reply_function: Callback for sending responses
        allowed_llms: Dict mapping string keys to LangChain LLM objects
        allow_system_prompt: Allow job data to override system_prompt

    Example:
        @agent(
            tools=[ReadFile(), ImageOCR()],
            system_prompt="You are a helpful assistant",
            llm=ChatMistralAI(model="mistral-large-latest"),
            memory=True,
            allowed_llms={
                "small": ChatMistralAI(model="mistral-small-latest"),
                "large": ChatMistralAI(model="mistral-large-latest"),
            },
            allow_system_prompt=True,
        )
        def my_agent(graph: StateGraph, config: dict) -> StateGraph:
            # config contains: tools, system_prompt, llm, temperature, memory,
            #                  reply_function, allowed_llms, allow_system_prompt

            def reasoning_node(state):
                # Access LangChain LLM
                llm = config["llm"]
                response = llm.invoke(state["messages"])

                # Send update via reply_function
                if config["reply_function"]:
                    config["reply_function"]("Step complete", {"step": 1})

                return {"messages": [response]}

            graph.add_node("reason", reasoning_node)
            graph.set_entry_point("reason")
            return graph

        # Use it
        worker = Worker()
        my_agent_instance = my_agent()  # Create configured instance
        worker.assign(my_agent_instance, queue="agent-queue")
    """

    def decorator(builder_func: Callable) -> Callable:
        @wraps(builder_func)
        def factory(**override_kwargs) -> Any:
            """Factory function that creates configured agent instances."""
            custom_state = override_kwargs.get("state_class", state_class)
            if custom_state and not issubclass(custom_state, dict):
                raise TypeError(f"state_class must be a dict subclass, got {custom_state}")

            llm_param = override_kwargs.get("llm", llm)
            llm_instance = resolve_llm(
                llm_param,
                default_model=override_kwargs.get("default_model", "mistral-large-latest"),
            )

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
                **override_kwargs,
            }

            return _AgentBase(builder_func, config)

        return factory

    return decorator
