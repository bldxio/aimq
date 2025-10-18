"""Supabase tools for interacting with Supabase services."""

from typing import List

from langchain.tools import BaseTool

from .enqueue import Enqueue
from .read_file import ReadFile
from .read_record import ReadRecord
from .write_file import WriteFile
from .write_record import WriteRecord

__all__ = [
    "ReadRecord",
    "WriteRecord",
    "ReadFile",
    "WriteFile",
    "Enqueue",
]


def get_tools() -> List[BaseTool]:
    """Get all Supabase tools."""
    tools: List[BaseTool] = [
        ReadRecord(),
        WriteRecord(),
        ReadFile(),
        WriteFile(),
    ]
    return tools
