from unittest.mock import patch

import pytest

from aimq.clients.supabase import SupabaseClient, SupabaseError


@pytest.fixture
def supabase_client():
    """Fixture for SupabaseClient with mocked environment variables."""
    from aimq.config import config

    # Patch the config singleton directly
    with (
        patch.object(config, "supabase_url", "http://test.url"),
        patch.object(config, "supabase_key", "test-key"),
    ):
        client = SupabaseClient()
        yield client


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
