# type: ignore  # mypy is configured to ignore test files in pyproject.toml
"""Tests for the configuration module.

This module contains test cases for the Config class, which handles
application configuration and environment variable management.
"""

import os
from typing import Generator

import pytest

from aimq.config import Config


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Fixture to provide a clean environment.

    Yields:
        None: This fixture doesn't yield any value.
    """
    old_env = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.update(old_env)


def test_default_values(clean_env: None) -> None:
    """Test default configuration values.

    Args:
        clean_env: Fixture that provides a clean environment.
    """

    class TestConfig(Config):
        model_config = {
            "case_sensitive": False,
            "env_file": None,  # Don't load from .env file
            "use_enum_values": True,
            "extra": "ignore",
        }

    config = TestConfig()

    # Supabase Configuration
    assert config.supabase_url == "http://127.0.0.1:54321"
    assert config.supabase_key == (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIs"
        "ImV4cCI6MTk4MzgxMjk5Nn0."
        "EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
    )

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


def test_environment_override(clean_env: None) -> None:
    """Test environment variable overrides.

    Args:
        clean_env: Fixture that provides a clean environment.
    """

    class TestConfig(Config):
        model_config = {
            "case_sensitive": False,
            "env_file": None,  # Don't load from .env file
            "use_enum_values": True,
            "extra": "ignore",
        }

    # Set environment variables with proper types
    os.environ.update(
        {
            "WORKER_NAME": "test_worker",
            "WORKER_LOG_LEVEL": "debug",
            "WORKER_IDLE_WAIT": "5.0",  # Must be string for env var
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test_key",
        }
    )

    config = TestConfig()

    assert config.worker_name == "test_worker"
    assert config.worker_log_level == "debug"
    assert config.worker_idle_wait == 5.0
    assert config.supabase_url == "https://test.supabase.co"
    assert config.supabase_key == "test_key"
