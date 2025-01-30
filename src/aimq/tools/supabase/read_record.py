"""Tool for reading records from Supabase."""

from typing import Any, Dict, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...clients.supabase import supabase


class ReadRecordInput(BaseModel):
    """Input for ReadRecord."""

    id: str = Field(..., description="The ID of the record to read")
    table: Optional[str] = Field(None, description="The table to read from")
    select: Optional[str] = Field(None, description="The columns to select")


class ReadRecord(BaseTool):
    """Tool for reading records from Supabase."""

    name: str = "read_record"
    description: str = "Read a record from Supabase"
    args_schema: Type[BaseModel] = ReadRecordInput

    table: str = "records"
    select: str = "*"

    def _run(
        self, id: str, table: Optional[str] = None, select: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read a record from Supabase.

        Args:
            id: The ID of the record to read.
            table: Optional table name to override the default.
            select: Optional select query to override the default.

        Returns:
            Dict[str, Any]: The record data.

        Raises:
            ValueError: If no record is found or if response data is not a dictionary.
        """
        table = table or self.table
        select = select or self.select

        result = (
            supabase.client.schema("public")
            .table(table)
            .select(select)
            .eq("id", id)
            .limit(1)
            .execute()
        )

        if not result.data:
            msg = f"No record found with ID {id} in table {table}"
            raise ValueError(msg)

        record = result.data[0]
        if not isinstance(record, dict):
            msg = (
                f"Expected dictionary response from Supabase, "
                f"got {type(record).__name__}"
            )
            raise ValueError(msg)

        return record
