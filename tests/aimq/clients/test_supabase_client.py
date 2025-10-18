import os
from unittest.mock import patch

import pytest

from aimq.clients.supabase import SupabaseClient, SupabaseError


@pytest.fixture
def supabase_client():
    """Fixture for SupabaseClient with mocked environment variables."""
    original_url = os.environ.get("SUPABASE_URL")
    original_key = os.environ.get("SUPABASE_KEY")

    os.environ["SUPABASE_URL"] = "http://test.url"
    os.environ["SUPABASE_KEY"] = "test-key"

    # Clear the config cache to ensure it picks up new env vars
    from aimq.config import get_config

    get_config.cache_clear()

    client = SupabaseClient()
    yield client

    # Restore original environment
    if original_url:
        os.environ["SUPABASE_URL"] = original_url
    else:
        del os.environ["SUPABASE_URL"]

    if original_key:
        os.environ["SUPABASE_KEY"] = original_key
    else:
        del os.environ["SUPABASE_KEY"]

    # Clear the config cache again
    get_config.cache_clear()


class TestSupabaseClient:
    def test_client_initialization_with_missing_config(self):
        """Test client initialization fails when config is missing."""
        from aimq.config import config

        with patch.object(config, "supabase_url", ""), patch.object(config, "supabase_key", ""):
            client = SupabaseClient()
            with pytest.raises(SupabaseError, match="Supabase client not configured"):
                _ = client.client

    def test_client_initialization_success(self, supabase_client):
        """Test successful client initialization."""
        assert supabase_client.client is not None
        # Verify client is cached
        assert supabase_client._client is not None
