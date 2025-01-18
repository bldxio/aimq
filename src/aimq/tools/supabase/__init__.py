"""Supabase tools for interacting with Supabase services."""
from typing import List

from langchain.tools import BaseTool
from .read_record import ReadRecord
from .write_record import WriteRecord
from .read_file import ReadFile
from .write_file import WriteFile
from .enqueue import Enqueue

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
