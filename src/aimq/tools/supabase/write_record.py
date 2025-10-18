"""Tool for writing records to Supabase."""

from typing import Any, Dict, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...clients.supabase import supabase


class WriteRecordInput(BaseModel):
    """Input for WriteRecord."""

    table: str = Field(..., description="The table to write to")
    data: Dict[str, Any] = Field(..., description="The data to write")
    id: str = Field(..., description="The ID of the record to update (if updating existing record)")


class WriteRecord(BaseTool):
    """Tool for writing records to Supabase."""

    name: str = "write_record"
    description: str = "Write a record to Supabase. If an ID is provided, updates existing record; otherwise creates new record."
    args_schema: Type[BaseModel] = WriteRecordInput

    def _run(self, table: str, data: Dict[str, Any], id: str) -> Dict[str, Any]:
        """Write a record to Supabase."""
        if id:
            # Update existing record
            result = supabase.client.table(table).update(data).eq("id", id).execute()

            if not result.data:
                raise ValueError(f"No record found with ID {id} in table {table}")
        else:
            # Insert new record
            result = supabase.client.table(table).insert(data).execute()

            if not result.data:
                raise ValueError(f"Failed to insert record into table {table}")

        return result.data[0]
