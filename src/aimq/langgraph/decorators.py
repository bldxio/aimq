"""
Decorators for defining LangGraph workflows and agents.
"""

from functools import wraps
from typing import Any, Callable

from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel


def workflow(
    state_class: type[dict] | None = None,  # Fix #2: use type[dict]
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
            from aimq.langgraph.base import _WorkflowBase

            # Merge config (decorator defaults + factory overrides)
            config = {"state_class": state_class, "checkpointer": checkpointer, **kwargs}

            # Use _WorkflowBase to handle compilation and execution
            return _WorkflowBase(builder_func, config)

        return factory

    return decorator


def agent(
    tools: list[BaseTool] | None = None,
    system_prompt: str | None = None,
    llm: BaseChatModel | str | None = None,
    temperature: float = 0.1,
    memory: bool = False,
    state_class: type[dict] | None = None,  # Fix #2: use type[dict]
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
            from aimq.langgraph.base import _AgentBase
            from aimq.langgraph.states import AgentState
            from aimq.langgraph.utils import default_reply_function, resolve_llm

            # Validate state_class if provided
            custom_state = override_kwargs.get("state_class", state_class)
            if custom_state and not issubclass(custom_state, dict):
                raise TypeError(f"state_class must be a dict subclass, got {custom_state}")

            # Process LLM using resolve_llm helper (Fix #4)
            llm_param = override_kwargs.get("llm", llm)
            llm_instance = resolve_llm(
                llm_param,
                default_model=override_kwargs.get("default_model", "mistral-large-latest"),
            )

            # Merge config (decorator defaults + factory overrides)
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

            # Use _AgentBase to handle graph compilation, overrides, execution
            return _AgentBase(builder_func, config)

        return factory

    return decorator
