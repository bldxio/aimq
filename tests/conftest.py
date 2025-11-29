"""Pytest configuration and shared fixtures for test isolation."""

import importlib  # noqa: F401
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """Reset the config singleton between tests to prevent state leakage.

    The @lru_cache() decorator on get_config() caches the Config instance,
    which can cause test isolation issues when running tests in sequence.
    This fixture clears the cache after each test.
    """
    yield

    # Clear the lru_cache for get_config()
    from aimq.config import get_config

    get_config.cache_clear()


@pytest.fixture(autouse=True)
def reset_client_modules():
    """Reset client module-level singletons to prevent state leakage.

    This clears cached client instances without reloading modules,
    which prevents class identity issues with exception handling.
    """
    yield

    # Reset module-level singleton instances to clear any cached clients
    try:
        import aimq.clients.mistral

        # Reset the module-level mistral singleton
        aimq.clients.mistral.mistral._client = None
    except Exception:
        pass  # Module may not be imported yet

    try:
        import aimq.clients.supabase

        # Reset the module-level supabase singleton
        if hasattr(aimq.clients.supabase, "supabase"):
            aimq.clients.supabase.supabase._client = None
    except Exception:
        pass  # Module may not be imported yet


@pytest.fixture(autouse=True)
def cleanup_mocks():
    """Ensure all mocks are properly cleaned up after each test.

    This fixture ensures that any patches or mocks created during a test
    are fully cleaned up, preventing mock side effects from leaking into
    subsequent tests.
    """
    yield

    # Mock cleanup happens automatically via pytest-mock or unittest.mock
    # This is just a placeholder for any additional cleanup if needed


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset any environment variables or global state.

    This fixture ensures that tests don't interfere with each other
    through environment variable modifications or global state changes.
    """
    import os

    # Store original environment
    original_env = os.environ.copy()

    yield

    # Restore original environment after test
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_supabase_client():
    """Provide a mock Supabase client for testing.

    This fixture creates a properly configured mock Supabase client
    that can be used in tests without requiring actual Supabase credentials.

    Returns:
        MagicMock: A mock Supabase client with common methods pre-configured.
    """
    mock_client = MagicMock()

    # Configure common Supabase operations
    mock_client.table.return_value.select.return_value.execute.return_value.data = []
    mock_client.table.return_value.insert.return_value.execute.return_value.data = []
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = (
        []
    )
    mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = (
        []
    )

    # Configure storage operations
    mock_client.storage.from_.return_value.upload.return_value = {"path": "test/file.txt"}
    mock_client.storage.from_.return_value.download.return_value = b"test content"

    # Configure RPC for pgmq operations
    mock_client.rpc.return_value.execute.return_value.data = []

    return mock_client


@pytest.fixture
def mock_mistral_client():
    """Provide a mock Mistral client for testing.

    This fixture creates a properly configured mock Mistral AI client
    that can be used in tests without requiring actual API credentials.

    Returns:
        MagicMock: A mock Mistral client with chat completions pre-configured.
    """
    mock_client = MagicMock()

    # Configure chat completions
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Test response from Mistral", role="assistant"))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing.

    This fixture creates a Config instance with safe default values
    that don't require real credentials or external services.

    Returns:
        Config: A test configuration instance.
    """
    from aimq.config import Config

    return Config(
        supabase_url="http://test.supabase.co",
        supabase_key="test-key",
        worker_name="test-worker",
        mistral_api_key="test-mistral-key",
        openai_api_key="test-openai-key",
        langchain_tracing_v2=False,
    )


# Configure pytest-asyncio if needed
def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


# Add custom pytest collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and ordering."""
    for item in items:
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add slow marker to tests that might be slow
        if any(keyword in item.nodeid for keyword in ["e2e", "integration", "workflow"]):
            item.add_marker(pytest.mark.slow)
