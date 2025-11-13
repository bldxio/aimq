"""Tool for detecting @mentions in message text."""

import re
from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class DetectMentionsInput(BaseModel):
    """Input for DetectMentions."""

    text: str = Field(..., description="The message text to scan for @mentions")


class DetectMentions(BaseTool):
    """Tool for detecting @mentions in message text.

    Extracts all @mention patterns from text (e.g., @react-assistant, @user123).
    Returns a list of mentions without the @ symbol.

    Example:
        tool = DetectMentions()
        result = tool.run("Hey @react-assistant can you help?")
        # Returns: ["react-assistant"]
    """

    name: str = "detect_mentions"
    description: str = (
        "Detect @mentions in message text. "
        "Returns a list of mentioned usernames/agents without the @ symbol."
    )
    args_schema: Type[BaseModel] = DetectMentionsInput

    def _run(self, text: str) -> list[str]:
        """Extract @mentions from text.

        Args:
            text: Message text to scan

        Returns:
            List of mentioned names (without @)
        """
        pattern = r"(?<![a-zA-Z0-9])@([\w\-_]+)"
        matches = re.findall(pattern, text)
        return matches
