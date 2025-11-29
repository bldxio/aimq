"""Tests for checkpointing functionality."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock langgraph.checkpoint modules before any imports
mock_checkpoint = MagicMock()
mock_checkpoint.base = MagicMock()
mock_checkpoint.postgres = MagicMock()
mock_checkpoint.serde = MagicMock()
mock_checkpoint.serde.base = MagicMock()
mock_checkpoint.serde.jsonplus = MagicMock()

sys.modules["langgraph.checkpoint"] = mock_checkpoint
sys.modules["langgraph.checkpoint.base"] = mock_checkpoint.base
sys.modules["langgraph.checkpoint.postgres"] = mock_checkpoint.postgres
sys.modules["langgraph.checkpoint.serde"] = mock_checkpoint.serde
sys.modules["langgraph.checkpoint.serde.base"] = mock_checkpoint.serde.base
sys.modules["langgraph.checkpoint.serde.jsonplus"] = mock_checkpoint.serde.jsonplus

# isort: off
from aimq.common.exceptions import CheckpointerError  # noqa: E402
from aimq.memory.checkpoint import (  # noqa: E402
    _build_connection_string,
    _extract_database_host,
    get_checkpointer,
)

# isort: on


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_success(mock_config):
    """Test connection string building with valid cloud config."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "postgresql://" in conn_str
    assert "postgres:" in conn_str
    assert "test-project" in conn_str
    assert "@db.test-project.supabase.co:5432/postgres" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_url_encoding(mock_config):
    """Test password URL encoding for special characters."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "key-with-special!@#$%chars"

    conn_str = _build_connection_string()

    # Special chars should be URL-encoded
    assert "%" in conn_str  # URL encoding produces % characters
    assert "!@#$%" not in conn_str  # Raw special chars shouldn't appear


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_missing_url(mock_config):
    """Test error when both SUPABASE_URL and DATABASE_HOST missing."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = ""
    mock_config.supabase_key = "test-key"

    with pytest.raises(CheckpointerError, match="Database host required"):
        _build_connection_string()


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_missing_password(mock_config):
    """Test error when both passwords missing."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = ""

    with pytest.raises(CheckpointerError, match="Database password required"):
        _build_connection_string()


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_invalid_url(mock_config):
    """Test error with invalid URL format."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "not-a-url"
    mock_config.supabase_key = "test-key"

    with pytest.raises(CheckpointerError, match="Invalid SUPABASE_URL format"):
        _build_connection_string()


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_extracts_project_ref(mock_config):
    """Test project reference extraction from URL."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://my-awesome-project.supabase.co"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "my-awesome-project" in conn_str
    assert "db.my-awesome-project.supabase.co" in conn_str


@patch("aimq.memory.checkpoint.ConnectionPool")
@patch("aimq.memory.checkpoint.PostgresSaver")
@patch("aimq.memory.checkpoint._build_connection_string")
@patch("aimq.memory.checkpoint._setup_schema")
def test_get_checkpointer_singleton(mock_setup, mock_build, mock_saver_class, mock_pool_class):
    """Test checkpointer singleton pattern.

    Updated to reflect ConnectionPool + direct PostgresSaver instantiation.
    """
    mock_build.return_value = "postgresql://test"
    mock_pool_instance = MagicMock()
    mock_saver_instance = MagicMock()

    # Mock ConnectionPool and PostgresSaver constructors
    mock_pool_class.return_value = mock_pool_instance
    mock_saver_class.return_value = mock_saver_instance

    # Reset singleton
    import aimq.memory.checkpoint as checkpoint_module

    checkpoint_module._checkpointer_instance = None

    # First call creates instance
    cp1 = get_checkpointer()
    assert cp1 is not None
    # Verify ConnectionPool was created
    mock_pool_class.assert_called_once()
    # Verify PostgresSaver was instantiated with pool
    mock_saver_class.assert_called_once_with(conn=mock_pool_instance)

    # Second call returns same instance
    cp2 = get_checkpointer()
    assert cp1 is cp2
    # Should only instantiate once due to singleton
    assert mock_pool_class.call_count == 1
    assert mock_saver_class.call_count == 1


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_with_trailing_slash(mock_config):
    """Test URL with trailing slash is handled correctly."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://test-project.supabase.co/"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "test-project" in conn_str
    assert "postgresql://" in conn_str


@patch("aimq.memory.checkpoint.ConnectionPool")
@patch("aimq.memory.checkpoint._setup_schema")
@patch("aimq.memory.checkpoint._build_connection_string")
@patch("aimq.memory.checkpoint.PostgresSaver")
def test_get_checkpointer_calls_setup_schema(
    mock_saver_class, mock_build, mock_setup, mock_pool_class
):
    """Test get_checkpointer calls _setup_schema.

    Updated to reflect ConnectionPool + direct PostgresSaver instantiation.
    """
    mock_build.return_value = "postgresql://test"
    mock_pool_instance = MagicMock()
    mock_saver_instance = MagicMock()

    # Mock ConnectionPool and PostgresSaver constructors
    mock_pool_class.return_value = mock_pool_instance
    mock_saver_class.return_value = mock_saver_instance

    # Reset singleton
    import aimq.memory.checkpoint as checkpoint_module

    checkpoint_module._checkpointer_instance = None

    get_checkpointer()

    # Setup schema should be called with the saver instance
    mock_setup.assert_called_once_with(mock_saver_instance)


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_password_encoding_preserves_alphanumeric(mock_config):
    """Test password encoding preserves alphanumeric characters."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "abc123XYZ"

    conn_str = _build_connection_string()

    # Alphanumeric should be preserved
    assert "abc123XYZ" in conn_str
    assert "postgresql://postgres:abc123XYZ@" in conn_str


# ===== New flexible configuration tests =====


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_database_url_override(mock_config):
    """Test DATABASE_URL takes highest priority."""
    mock_config.database_url = "postgresql://custom:pass@custom-host:5433/custom_db"
    # These should be ignored when DATABASE_URL is set
    mock_config.database_host = "ignored"
    mock_config.database_port = 9999
    mock_config.supabase_url = "https://ignored.supabase.co"
    mock_config.supabase_key = "ignored"

    conn_str = _build_connection_string()

    # Should return DATABASE_URL directly
    assert conn_str == "postgresql://custom:pass@custom-host:5433/custom_db"


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_localhost(mock_config):
    """Test local development with localhost auto-detects port 54322 and password."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432  # Default port
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""  # Not set
    mock_config.supabase_url = "http://localhost:54321"
    mock_config.supabase_key = "jwt-token-not-used-for-localhost"

    conn_str = _build_connection_string()

    # Should auto-detect localhost and use port 54322 with password "postgres"
    assert conn_str == "postgresql://postgres:postgres@localhost:54322/postgres"


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_docker_service(mock_config):
    """Test Docker Compose with service name."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "http://supabase:8000"
    mock_config.supabase_key = "docker-key"

    conn_str = _build_connection_string()

    assert "postgresql://postgres:" in conn_str
    assert "@supabase:5432/postgres" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_self_hosted(mock_config):
    """Test self-hosted Supabase on custom domain."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://supabase.company.com"
    mock_config.supabase_key = "company-key"

    conn_str = _build_connection_string()

    assert "postgresql://postgres:" in conn_str
    # Domains with 'supabase' in name are returned as-is (no db. prefix)
    assert "@supabase.company.com:5432/postgres" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_pooler_port(mock_config):
    """Test connection pooler port configuration."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 6543  # Pooler port
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "@db.test-project.supabase.co:6543/postgres" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_explicit_host_override(mock_config):
    """Test DATABASE_HOST overrides SUPABASE_URL parsing."""
    mock_config.database_url = ""
    mock_config.database_host = "my-custom-db.example.com"
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = "explicit-password"
    mock_config.supabase_url = "https://should-be-ignored.supabase.co"
    mock_config.supabase_key = "ignored-key"

    conn_str = _build_connection_string()

    # Should use explicit DATABASE_HOST and DATABASE_PASSWORD
    assert "@my-custom-db.example.com:5432/postgres" in conn_str
    assert "explicit-password" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_database_password_fallback(mock_config):
    """Test DATABASE_PASSWORD falls back to SUPABASE_KEY."""
    mock_config.database_url = ""
    mock_config.database_host = "db.example.com"
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""  # Empty
    mock_config.supabase_url = ""
    mock_config.supabase_key = "fallback-key"

    conn_str = _build_connection_string()

    # Should use SUPABASE_KEY as fallback
    assert "fallback-key" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_custom_db_name(mock_config):
    """Test custom database name configuration."""
    mock_config.database_url = ""
    mock_config.database_host = "db.example.com"
    mock_config.database_port = 5432
    mock_config.database_name = "my_custom_db"
    mock_config.database_user = "postgres"
    mock_config.database_password = "password"
    mock_config.supabase_url = ""
    mock_config.supabase_key = ""

    conn_str = _build_connection_string()

    assert "@db.example.com:5432/my_custom_db" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_custom_user(mock_config):
    """Test custom database user configuration."""
    mock_config.database_url = ""
    mock_config.database_host = "db.example.com"
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "custom_user"
    mock_config.database_password = "password"
    mock_config.supabase_url = ""
    mock_config.supabase_key = ""

    conn_str = _build_connection_string()

    assert "postgresql://custom_user:password@" in conn_str


# ===== Tests for _extract_database_host function =====


def test_extract_database_host_cloud():
    """Test extracting host from Supabase Cloud URL."""
    host = _extract_database_host("https://my-project.supabase.co")
    assert host == "db.my-project.supabase.co"


def test_extract_database_host_cloud_with_trailing_slash():
    """Test extracting host from Cloud URL with trailing slash."""
    host = _extract_database_host("https://my-project.supabase.co/")
    assert host == "db.my-project.supabase.co"


def test_extract_database_host_localhost():
    """Test extracting host from localhost URL."""
    host = _extract_database_host("http://localhost:54321")
    assert host == "localhost"


def test_extract_database_host_localhost_https():
    """Test extracting host from localhost HTTPS URL."""
    host = _extract_database_host("https://localhost:54321")
    assert host == "localhost"


def test_extract_database_host_127_0_0_1():
    """Test extracting host from 127.0.0.1 URL."""
    host = _extract_database_host("http://127.0.0.1:54321")
    assert host == "127.0.0.1"


def test_extract_database_host_docker_service():
    """Test extracting host from Docker service name."""
    host = _extract_database_host("http://supabase:8000")
    # Docker service names (no dots) should be returned as-is
    assert host == "supabase"


def test_extract_database_host_self_hosted():
    """Test extracting host from self-hosted domain."""
    host = _extract_database_host("https://supabase.company.com")
    # Domains with 'supabase' in name are returned as-is (no db. prefix)
    assert host == "supabase.company.com"


def test_extract_database_host_self_hosted_with_port():
    """Test extracting host from self-hosted URL with port."""
    host = _extract_database_host("https://supabase.company.com:8443")
    assert host == "supabase.company.com"


def test_extract_database_host_custom_domain():
    """Test extracting host from generic custom domain."""
    host = _extract_database_host("https://api.example.com")
    # Generic domains should get db. prefix
    assert host == "db.api.example.com"


def test_extract_database_host_invalid_url():
    """Test error with invalid URL format."""
    with pytest.raises(CheckpointerError, match="Invalid SUPABASE_URL format"):
        _extract_database_host("not-a-url")


def test_extract_database_host_no_protocol():
    """Test error with URL missing protocol."""
    with pytest.raises(CheckpointerError, match="Invalid SUPABASE_URL format"):
        _extract_database_host("supabase.company.com")


# ===== Tests for localhost port auto-detection =====


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_localhost_127_0_0_1(mock_config):
    """Test 127.0.0.1 also auto-detects port 54322 and password."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432  # Default port
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "http://127.0.0.1:54321"
    mock_config.supabase_key = "jwt-token"

    conn_str = _build_connection_string()

    # Should auto-detect 127.0.0.1 and use port 54322 with password "postgres"
    assert conn_str == "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_localhost_password_override(mock_config):
    """Test explicit DATABASE_PASSWORD overrides smart default."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5432
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = "custom-password"  # Explicit password
    mock_config.supabase_url = "http://localhost:54321"
    mock_config.supabase_key = "jwt-token"

    conn_str = _build_connection_string()

    # Explicit password should be used, not "postgres"
    assert conn_str == "postgresql://postgres:custom-password@localhost:54322/postgres"


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_localhost_custom_port(mock_config):
    """Test explicit custom port on localhost (not 5432 or 54322)."""
    mock_config.database_url = ""
    mock_config.database_host = ""
    mock_config.database_port = 5433  # Custom port
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""
    mock_config.supabase_url = "http://localhost:54321"
    mock_config.supabase_key = "local-dev-key"

    conn_str = _build_connection_string()

    # Custom port should be preserved
    assert "@localhost:5433/postgres" in conn_str


@patch("aimq.memory.checkpoint.config")
def test_build_connection_string_explicit_localhost_host(mock_config):
    """Test explicit DATABASE_HOST=localhost also gets smart port and password."""
    mock_config.database_url = ""
    mock_config.database_host = "localhost"  # Explicitly set
    mock_config.database_port = 5432  # Default
    mock_config.database_name = "postgres"
    mock_config.database_user = "postgres"
    mock_config.database_password = ""  # Not set
    mock_config.supabase_url = ""
    mock_config.supabase_key = ""

    conn_str = _build_connection_string()

    # Should still detect localhost and use 54322 with password "postgres"
    assert conn_str == "postgresql://postgres:postgres@localhost:54322/postgres"
