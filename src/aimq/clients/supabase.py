from typing import Optional

from supabase import Client, create_client

from ..config import config


class SupabaseError(Exception):
    """Base exception for Supabase-related errors."""

    pass


class SupabaseClient:
    """A wrapper class for Supabase operations."""

    def __init__(self):
        """Initialize the Supabase client."""
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get or create the Supabase client.

        Returns:
            Client: Configured Supabase client

        Raises:
            SupabaseError: If Supabase is not properly configured
        """
        if self._client is None:
            supabase_url = config.supabase_url
            supabase_key = config.supabase_key

            if (
                not supabase_url
                or not supabase_key
                or not supabase_url.strip()
                or not supabase_key.strip()
            ):
                raise SupabaseError("Supabase client not configured")

            self._client = create_client(supabase_url, supabase_key)

        return self._client


supabase = SupabaseClient()
