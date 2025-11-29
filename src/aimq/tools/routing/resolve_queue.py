"""Tool for resolving mentions to queue names."""

from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class ResolveQueueInput(BaseModel):
    """Input for ResolveQueue."""

    mentions: list[str] = Field(..., description="List of mentions to resolve")
    default_queue: str = Field(
        "default-assistant", description="Default queue if no valid mentions found"
    )


class ResolveQueue(BaseTool):
    """Tool for resolving @mentions to queue names.

    Supports patterns:
    - Mentions ending in -assistant or _assistant
    - Mentions ending in -bot or _bot
    - Falls back to default queue if no valid mentions

    Example:
        tool = ResolveQueue()
        result = tool.run(mentions=["react-assistant", "user123"])
        # Returns: "react-assistant"

        result = tool.run(mentions=["user123"])
        # Returns: "default-assistant"
    """

    name: str = "resolve_queue"
    description: str = (
        "Resolve @mentions to queue names. "
        "Looks for mentions ending in -assistant, _assistant, -bot, or _bot. "
        "Returns the first valid queue name or default queue."
    )
    args_schema: Type[BaseModel] = ResolveQueueInput

    valid_suffixes: list[str] = ["-assistant", "_assistant", "-bot", "_bot"]

    def _run(self, mentions: list[str], default_queue: str = "default-assistant") -> str:
        """Resolve mentions to a queue name.

        Args:
            mentions: List of mention names (without @)
            default_queue: Fallback queue name

        Returns:
            Queue name to route message to
        """
        for mention in mentions:
            if any(mention.endswith(suffix) for suffix in self.valid_suffixes):
                return mention

        return default_queue
