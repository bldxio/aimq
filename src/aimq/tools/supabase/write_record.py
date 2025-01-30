"""Tool for writing records to Supabase."""

from typing import Any, Dict, Optional, Type, cast

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...clients.supabase import supabase


class WriteRecordInput(BaseModel):
    """Input for WriteRecord."""

    data: Dict[str, Any] = Field(..., description="The data to write")
    table: Optional[str] = Field(..., description="The table to write to")
    id: Optional[str] = Field(None, description="The ID of the record to update")


class WriteRecord(BaseTool):
    """Tool for writing records to Supabase."""

    name: str = "write_record"
    description: str = (
        "Write a record to Supabase. If an ID is provided, updates existing record; "
        "otherwise creates new record."
    )
    args_schema: Type[BaseModel] = WriteRecordInput

    table: str = "records"
    id: Optional[str] = None

    def _run(
        self,
        data: Dict[str, Any],
        table: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Write a record to Supabase."""
        table = table or self.table
        id = id or self.id

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

        return cast(Dict[str, Any], result.data[0])
