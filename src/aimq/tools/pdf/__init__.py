"""PDF tools for processing and manipulating PDF files."""

from typing import List

from langchain.tools import BaseTool

from .page_splitter import PageSplitter

__all__ = [
    "PageSplitter",
]


def get_tools() -> List[BaseTool]:
    """Get all PDF tools."""
    tools: List[BaseTool] = [
        PageSplitter(),
    ]
    return tools
