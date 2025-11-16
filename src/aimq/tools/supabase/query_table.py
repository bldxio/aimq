"""Tool for querying Supabase tables."""

import logging
from typing import Any, Dict, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from aimq.clients.supabase import supabase

logger = logging.getLogger(__name__)


class QueryTableInput(BaseModel):
    """Input for QueryTable tool."""

    table: str = Field(..., description="Name of the table to query")
    columns: str = Field(
        default="*", description="Columns to select (comma-separated or '*' for all)"
    )
    filters: Optional[str] = Field(
        default=None,
        description="Filter conditions in format 'column:operator:value' (e.g., 'sport_code:eq:basketball')",
    )
    limit: int = Field(default=10, description="Maximum number of rows to return")


class QueryTable(BaseTool):
    """Tool for querying Supabase database tables.

    Supports filtering, column selection, and result limiting.
    Designed for read-only queries on the competitors table and other sports data.

    Example:
        tool = QueryTable()
        # Get all NBA teams
        result = tool.run(table="competitors", filters="sport_code:eq:basketball,entity_type:eq:team")
        # Get player names
        result = tool.run(table="competitors", columns="first_name,last_name,position", filters="entity_type:eq:player")
    """

    name: str = "query_table"
    description: str = (
        "Query Supabase database tables. "
        "Supports filtering by columns, selecting specific columns, and limiting results. "
        "Use for querying competitors (teams/players), sports data, and other tables. "
        "Filters format: 'column:operator:value' where operator can be eq, neq, gt, lt, gte, lte, like, ilike. "
        "Multiple filters separated by commas."
    )
    args_schema: Type[BaseModel] = QueryTableInput

    def _parse_filters(self, filters: Optional[str]) -> list[tuple[str, str, str]]:
        """Parse filter string into list of (column, operator, value) tuples.

        Args:
            filters: Filter string in format 'column:operator:value,column:operator:value'

        Returns:
            List of (column, operator, value) tuples
        """
        if not filters:
            return []

        parsed = []
        for filter_str in filters.split(","):
            parts = filter_str.strip().split(":")
            if len(parts) != 3:
                logger.warning(f"Invalid filter format: {filter_str}")
                continue

            column, operator, value = parts
            parsed.append((column.strip(), operator.strip(), value.strip()))

        return parsed

    def _apply_filters(self, query: Any, filters: list[tuple[str, str, str]]) -> Any:
        """Apply filters to a Supabase query.

        Args:
            query: Supabase query builder
            filters: List of (column, operator, value) tuples

        Returns:
            Query with filters applied
        """
        for column, operator, value in filters:
            if operator == "eq":
                query = query.eq(column, value)
            elif operator == "neq":
                query = query.neq(column, value)
            elif operator == "gt":
                query = query.gt(column, value)
            elif operator == "lt":
                query = query.lt(column, value)
            elif operator == "gte":
                query = query.gte(column, value)
            elif operator == "lte":
                query = query.lte(column, value)
            elif operator == "like":
                query = query.like(column, value)
            elif operator == "ilike":
                query = query.ilike(column, value)
            else:
                logger.warning(f"Unknown operator: {operator}")

        return query

    def _format_results(self, data: list[Dict[str, Any]], table: str, count: int) -> str:
        """Format query results as a readable string.

        Args:
            data: List of result rows
            table: Table name
            count: Number of results

        Returns:
            Formatted string representation
        """
        if not data:
            return f"No results found in table '{table}'"

        result = f"Found {count} result(s) in table '{table}':\n\n"

        for i, row in enumerate(data, 1):
            result += f"Row {i}:\n"
            for key, value in row.items():
                if isinstance(value, dict):
                    result += f"  {key}: {value}\n"
                elif value is not None:
                    result += f"  {key}: {value}\n"
            result += "\n"

        return result.strip()

    def _run(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        """Query a Supabase table.

        Args:
            table: Table name to query
            columns: Columns to select (comma-separated or '*')
            filters: Filter conditions
            limit: Maximum rows to return

        Returns:
            Formatted query results
        """
        try:
            client = supabase.client

            query = client.table(table).select(columns)

            parsed_filters = self._parse_filters(filters)
            if parsed_filters:
                query = self._apply_filters(query, parsed_filters)

            query = query.limit(limit)

            response = query.execute()

            if not response.data:
                return f"No results found in table '{table}'"

            return self._format_results(response.data, table, len(response.data))

        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            return f"Error querying table '{table}': {str(e)}"
