import os

import pytest

from aimq.config import Config


@pytest.fixture
def clean_env():
    """Fixture to provide a clean environment."""
    old_env = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.update(old_env)


def test_default_values(clean_env):
    """Test default configuration values."""

    # Create a new config class that doesn't load from environment
    class TestConfig(Config):
        model_config = {
            "case_sensitive": False,
            "env_file": None,  # Don't load from .env file
            "use_enum_values": True,
            "extra": "ignore",
        }

    config = TestConfig()

    # Supabase Configuration
    assert config.supabase_url == ""
    assert config.supabase_key == ""

    # Worker Configuration
    assert config.worker_name == "peon"
    assert config.worker_log_level == "info"
    assert isinstance(config.worker_idle_wait, float)
    assert config.worker_idle_wait == 10.0

    # LangChain Configuration
    assert config.langchain_tracing_v2 is False
    assert config.langchain_endpoint == "https://api.smith.langchain.com"
    assert config.langchain_api_key == ""
    assert config.langchain_project == ""

    # OpenAI Configuration
    assert config.openai_api_key == ""


def test_environment_override(clean_env):
    """Test environment variable overrides."""

    # Create a new config class that doesn't load from .env file
    class TestConfig(Config):
        model_config = {
            "case_sensitive": False,
            "env_file": None,  # Don't load from .env file
            "use_enum_values": True,
            "extra": "ignore",
        }

    # Set environment variables
    env = {
        "WORKER_NAME": "test_worker",
        "WORKER_LOG_LEVEL": "debug",
        "WORKER_IDLE_WAIT": 5.0,
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test_key",
    }

    config = TestConfig(**env)

    assert config.worker_name == "test_worker"
    assert config.worker_log_level == "debug"
    assert config.worker_idle_wait == 5.0
    assert config.supabase_url == "https://test.supabase.co"
    assert config.supabase_key == "test_key"
