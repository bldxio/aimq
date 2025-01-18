"""Tool for reading records from Supabase."""
from token import OP
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
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

    def _run(self, id: str, table: Optional[str] = None, select: Optional[str] = None) -> Dict[str, Any]:
        """Read a record from Supabase."""
        table = table or self.table
        select = select or self.select

        result = (supabase.client.schema('public').table(table)
                 .select(select)
                 .eq('id', id)
                 .limit(1)
                 .execute())
        
        if not result.data:
            raise ValueError(f"No record found with ID {id} in table {table}")
            
        return result.data[0]
