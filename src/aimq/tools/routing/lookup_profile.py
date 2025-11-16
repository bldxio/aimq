"""Tool for looking up user profiles in Supabase."""

from typing import Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...clients.supabase import supabase


class LookupProfileInput(BaseModel):
    """Input for LookupProfile."""

    profile_id: str = Field(..., description="The profile ID to lookup")
    table: str = Field("profiles", description="The table to query")


class LookupProfile(BaseTool):
    """Tool for looking up user profiles in Supabase.

    Queries the profiles table to get user information by profile_id.
    Useful for resolving user mentions to actual user data.

    Example:
        tool = LookupProfile()
        result = tool.run(profile_id="user_123")
        # Returns: {"id": "user_123", "name": "John", "queue": "john-assistant"}
    """

    name: str = "lookup_profile"
    description: str = (
        "Look up a user profile in Supabase by profile_id. "
        "Returns profile data including name, queue, and other metadata."
    )
    args_schema: Type[BaseModel] = LookupProfileInput

    table: str = "profiles"

    def _run(self, profile_id: str, table: Optional[str] = None) -> dict[str, Any]:
        """Look up a profile by ID.

        Args:
            profile_id: The profile ID to lookup
            table: Optional table name override

        Returns:
            Profile data dictionary

        Raises:
            ValueError: If profile not found
        """
        table = table or self.table

        result = (
            supabase.client.schema("public")
            .table(table)
            .select("*")
            .eq("id", profile_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            raise ValueError(f"No profile found with ID {profile_id} in table {table}")

        return result.data[0]
