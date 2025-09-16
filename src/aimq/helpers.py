"""Helper functions for building and composing runnables in the AIMQ framework.

This module provides utility functions for working with LangChain runnables,
including functions for chaining, selecting, and transforming data through
the runnable pipeline.
"""

from graphlib import TopologicalSorter
from langchain_core.runnables import RunnableConfig, RunnableParallel, RunnablePassthrough, RunnableSequence, chain, RunnableSerializable
from langchain_core.runnables.passthrough import RunnableAssign, RunnablePick
from langchain_core.runnables.base import Runnable, RunnableEach, RunnableLambda 
from typing import Any, Callable, TypeVar

from langchain_core.tools import tool

T = TypeVar("T")

@chain
def echo(input: T) -> T:
    """Echo the input value back while also printing it to stdout.

    Args:
        input: Any value to be echoed.

    Returns:
        The same value that was passed in.
    """
    print(input)
    return input

def select(key: str | list[str] | dict[str, str] | None = None) -> Runnable:
    """Create a runnable that selects specific keys from the input.

    Args:
        key: Specifies what to select from the input:
            - None: Pass through the entire input
            - str: Select a single key
            - list[str]: Select multiple keys
            - dict[str, str]: Map old keys to new keys

    Returns:
        A runnable that performs the selection operation.

    Raises:
        ValueError: If the key type is not one of the supported types.
    """
    if key is None:
        return RunnablePassthrough()
    elif isinstance(key, str):
        return RunnableParallel({key: RunnablePassthrough()})
    elif isinstance(key, list):
        return RunnablePick(key)
    elif isinstance(key, dict):
        return RunnableParallel({
            new_key: RunnablePassthrough() if old_key == "*" else RunnablePick(old_key)
            for old_key, new_key in key.items()
        })
    else:
        raise ValueError(f"Invalid key type: {type(key)}")

def const(value: T) -> Callable[[Any], T]:
    """Create a function that always returns a constant value.

    Args:
        value: The constant value to be returned.

    Returns:
        A function that takes any input and returns the constant value.
    """
    return lambda x: value

def assign(runnables: dict[str, Any] = {}) -> RunnableAssign:
    """Create a RunnableAssign from a dictionary of runnables or constant values.

    Args:
        runnables: Dictionary mapping keys to either runnables or constant values.
            Constant values will be wrapped in a const function.

    Returns:
        A RunnableAssign that assigns the results of the runnables to their respective keys.
    """
    for k, v in runnables.items():
        if not isinstance(v, RunnableAssign):
            runnables[k] = const(v)
    return RunnableAssign(RunnableParallel(runnables))

def pick(key: str | list[str]) -> RunnablePick:
    """Create a RunnablePick to select specific keys from the input.

    Args:
        key: Either a single key or list of keys to select from the input.

    Returns:
        A RunnablePick configured to select the specified key(s).
    """
    return RunnablePick(key)

def orig(key: str | list[str] | None = None) -> Runnable[Any, dict[str, Any]]:
    """Create a runnable that retrieves the original configuration.

    Args:
        key: Optional key or list of keys to select from the configuration.
            If None, returns the entire configuration.

    Returns:
        A runnable that returns the selected configuration values.
    """
    def _orig(input: Any, config: RunnableConfig) -> dict[str, Any]:
        return config.get("configurable", {})
    runnable = RunnableLambda(_orig)

    if key is not None:
        runnable = runnable | pick(key) # type: ignore
    return runnable