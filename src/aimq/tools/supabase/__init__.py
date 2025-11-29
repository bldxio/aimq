"""Supabase tools for interacting with Supabase services."""

from typing import List

from langchain.tools import BaseTool

from .enqueue import Enqueue
from .query_table import QueryTable
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
    "QueryTable",
]


def get_tools() -> List[BaseTool]:
    """Get all Supabase tools."""
    tools: List[BaseTool] = [
        ReadRecord(),
        WriteRecord(),
        ReadFile(),  # type: ignore[call-arg]
        WriteFile(),  # type: ignore[call-arg]
    ]
    return tools
