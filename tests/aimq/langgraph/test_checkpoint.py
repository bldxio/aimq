"""Tests for checkpointing functionality."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock langgraph.checkpoint.postgres before importing checkpoint module
sys.modules["langgraph.checkpoint"] = MagicMock()
sys.modules["langgraph.checkpoint.postgres"] = MagicMock()

# isort: off
from aimq.langgraph.checkpoint import _build_connection_string, get_checkpointer  # noqa: E402
from aimq.langgraph.exceptions import CheckpointerError  # noqa: E402

# isort: on


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_success(mock_config):
    """Test connection string building with valid config."""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "postgresql://" in conn_str
    assert "postgres:" in conn_str
    assert "test-project" in conn_str
    assert "@db.test-project.supabase.co:5432/postgres" in conn_str


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_url_encoding(mock_config):
    """Test password URL encoding for special characters."""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "key-with-special!@#$%chars"

    conn_str = _build_connection_string()

    # Special chars should be URL-encoded
    assert "%" in conn_str  # URL encoding produces % characters
    assert "!@#$%" not in conn_str  # Raw special chars shouldn't appear


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_missing_url(mock_config):
    """Test error when SUPABASE_URL missing."""
    mock_config.supabase_url = ""
    mock_config.supabase_key = "test-key"

    with pytest.raises(CheckpointerError, match="SUPABASE_URL required"):
        _build_connection_string()


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_missing_key(mock_config):
    """Test error when SUPABASE_KEY missing."""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = ""

    with pytest.raises(CheckpointerError, match="SUPABASE_KEY required"):
        _build_connection_string()


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_invalid_url(mock_config):
    """Test error with invalid URL format."""
    mock_config.supabase_url = "https://invalid-url.com"
    mock_config.supabase_key = "test-key"

    with pytest.raises(CheckpointerError, match="Invalid SUPABASE_URL format"):
        _build_connection_string()


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_extracts_project_ref(mock_config):
    """Test project reference extraction from URL."""
    mock_config.supabase_url = "https://my-awesome-project.supabase.co"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "my-awesome-project" in conn_str
    assert "db.my-awesome-project.supabase.co" in conn_str


@patch("aimq.langgraph.checkpoint.PostgresSaver")
@patch("aimq.langgraph.checkpoint._build_connection_string")
@patch("aimq.langgraph.checkpoint._ensure_schema")
def test_get_checkpointer_singleton(mock_ensure, mock_build, mock_saver_class):
    """Test checkpointer singleton pattern."""
    mock_build.return_value = "postgresql://test"
    mock_saver_instance = MagicMock()

    # Mock the context manager behavior
    mock_context = MagicMock()
    mock_context.__enter__ = MagicMock(return_value=mock_saver_instance)
    mock_context.__exit__ = MagicMock(return_value=False)
    mock_saver_class.from_conn_string.return_value = mock_context

    # Reset singleton
    import aimq.langgraph.checkpoint as checkpoint_module

    checkpoint_module._checkpointer_instance = None

    # First call creates instance
    cp1 = get_checkpointer()
    assert cp1 is not None
    assert mock_saver_class.from_conn_string.called

    # Second call returns same instance
    cp2 = get_checkpointer()
    assert cp1 is cp2
    # Should only call from_conn_string once due to singleton
    assert mock_saver_class.from_conn_string.call_count == 1


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_none_values(mock_config):
    """Test error when config values are None."""
    mock_config.supabase_url = None
    mock_config.supabase_key = None

    with pytest.raises(CheckpointerError, match="SUPABASE_URL required"):
        _build_connection_string()


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_with_trailing_slash(mock_config):
    """Test URL with trailing slash is handled correctly."""
    mock_config.supabase_url = "https://test-project.supabase.co/"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "test-project" in conn_str
    assert "postgresql://" in conn_str


@patch("aimq.langgraph.checkpoint._ensure_schema")
@patch("aimq.langgraph.checkpoint._build_connection_string")
@patch("aimq.langgraph.checkpoint.PostgresSaver")
def test_get_checkpointer_calls_ensure_schema(mock_saver_class, mock_build, mock_ensure):
    """Test get_checkpointer calls _ensure_schema."""
    mock_build.return_value = "postgresql://test"
    mock_saver_instance = MagicMock()

    # Mock the context manager
    mock_context = MagicMock()
    mock_context.__enter__ = MagicMock(return_value=mock_saver_instance)
    mock_context.__exit__ = MagicMock(return_value=False)
    mock_saver_class.from_conn_string.return_value = mock_context

    # Reset singleton
    import aimq.langgraph.checkpoint as checkpoint_module

    checkpoint_module._checkpointer_instance = None

    get_checkpointer()

    # Ensure schema should be called
    mock_ensure.assert_called_once()


@patch("aimq.langgraph.checkpoint.config")
def test_build_connection_string_password_encoding_preserves_alphanumeric(mock_config):
    """Test password encoding preserves alphanumeric characters."""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "abc123XYZ"

    conn_str = _build_connection_string()

    # Alphanumeric should be preserved
    assert "abc123XYZ" in conn_str
    assert "postgresql://postgres:abc123XYZ@" in conn_str
