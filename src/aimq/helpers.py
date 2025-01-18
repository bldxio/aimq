from graphlib import TopologicalSorter
from langchain_core.runnables import RunnableConfig, RunnableParallel, RunnablePassthrough, RunnableSequence, chain
from langchain_core.runnables.passthrough import RunnableAssign, RunnablePick
from langchain_core.runnables.base import Runnable, RunnableEach, RunnableLambda 
from typing import Any, Callable, TypeVar

from langchain_core.tools import tool

T = TypeVar("T")

@chain
def echo(input: T) -> T:
    print(input)
    return input

def select(key: str | list[str] | dict[str, str] | None = None) -> Runnable:
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
    return lambda x: value

def assign(runnables: dict[str, Any] = {}) -> RunnableAssign:
    for k, v in runnables.items():
        if not isinstance(v, RunnableAssign):
            runnables[k] = const(v)
    return RunnableAssign(RunnableParallel(runnables))

def pick(key: str | list[str]) -> RunnablePick:
    return RunnablePick(key)

def orig(key: str | list[str] | None = None) -> Runnable:
    def _orig(input: Any, config: RunnableConfig) -> dict[str, Any]:
        return config.get("configurable", {})
    runnable = RunnableLambda(_orig)

    if key is not None:
        runnable = runnable | pick(key)
    return runnable

