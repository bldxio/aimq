"""Configuration module for AIMQ.

This module provides configuration classes and utilities for AIMQ.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Default Supabase configuration for local development
LOCAL_SUPABASE_URL = "http://127.0.0.1:54321"
LOCAL_SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6"
    "MTk4MzgxMjk5Nn0."
    "EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
)


class Config(BaseSettings):
    """AIMQ configuration settings.

    Attributes:
        supabase_url: URL of the Supabase project.
        supabase_key: API key for the Supabase project.
        worker_name: Name of the worker instance.
        worker_log_level: Log level for the worker.
        worker_idle_wait: Time to wait between polling for new jobs.
        langchain_tracing_v2: Enable LangChain tracing v2.
        langchain_endpoint: LangChain API endpoint.
        langchain_api_key: LangChain API key.
        langchain_project: LangChain project name.
        openai_api_key: OpenAI API key.
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        use_enum_values=True,
        extra="ignore",
    )

    # Supabase Configuration
    supabase_url: str = Field(
        default=LOCAL_SUPABASE_URL,
        description="Supabase project URL",
        alias="SUPABASE_URL",
    )
    supabase_key: str = Field(
        default=LOCAL_SUPABASE_KEY,
        description="Supabase project API key",
        alias="SUPABASE_KEY",
    )

    # Worker Configuration
    worker_name: str = Field(
        default="peon",
        description="Name of the worker instance",
        alias="WORKER_NAME",
    )
    worker_log_level: str = Field(
        default="info",
        description="Log level for the worker",
        alias="WORKER_LOG_LEVEL",
    )
    worker_idle_wait: float = Field(
        default=10.0,
        description="Time to wait between polling for new jobs",
        alias="WORKER_IDLE_WAIT",
    )

    # LangChain Configuration
    langchain_tracing_v2: bool = Field(
        default=False,
        description="Enable LangChain tracing v2",
        alias="LANGCHAIN_TRACING_V2",
    )
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        description="LangChain API endpoint",
        alias="LANGCHAIN_ENDPOINT",
    )
    langchain_api_key: str = Field(
        default="",
        description="LangChain API key",
        alias="LANGCHAIN_API_KEY",
    )
    langchain_project: str = Field(
        default="",
        description="LangChain project name",
        alias="LANGCHAIN_PROJECT",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key",
        alias="OPENAI_API_KEY",
    )


@lru_cache()
def get_config() -> Config:
    """Get the configuration singleton.

    Returns:
        Config: The configuration singleton.
    """
    return Config()


# Create a config singleton
config = get_config()
