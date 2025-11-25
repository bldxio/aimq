from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Configuration class for the application."""

    model_config = {
        "case_sensitive": False,
        "env_file": ".env",
        "use_enum_values": True,
        "extra": "ignore",
    }

    # Supabase Configuration
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")

    # Supabase Realtime Configuration
    supabase_realtime_channel: str = Field(
        default="aimq:jobs",
        alias="SUPABASE_REALTIME_CHANNEL",
        description="Realtime channel name for worker notifications",
    )
    supabase_realtime_event: str = Field(
        default="job_enqueued",
        alias="SUPABASE_REALTIME_EVENT",
        description="Realtime event name for job notifications",
    )

    # Database Configuration (for LangGraph checkpointing and direct DB access)
    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
        description="Direct PostgreSQL connection string (overrides all other database settings)",
    )
    database_host: str = Field(
        default="",
        alias="DATABASE_HOST",
        description="Database host (overrides host extracted from SUPABASE_URL)",
    )
    database_port: int = Field(
        default=5432,
        alias="DATABASE_PORT",
        description="Database port (5432 for direct, 6543 for connection pooler)",
    )
    database_name: str = Field(
        default="postgres",
        alias="DATABASE_NAME",
        description="Database name",
    )
    database_user: str = Field(
        default="postgres",
        alias="DATABASE_USER",
        description="Database user",
    )
    database_password: str = Field(
        default="",
        alias="DATABASE_PASSWORD",
        description="Database password (falls back to SUPABASE_KEY if not set)",
    )

    # Worker Configuration
    worker_name: str = Field(default="peon", alias="WORKER_NAME")
    worker_path: Path = Field(default=Path("./tasks.py"), alias="WORKER_PATH")

    worker_log_level: str = Field(default="info", alias="WORKER_LOG_LEVEL")
    worker_idle_wait: float = Field(default=10.0, alias="WORKER_IDLE_WAIT")

    # Queue Error Handling & Retry Configuration
    queue_max_retries: int = Field(
        default=5,
        alias="QUEUE_MAX_RETRIES",
        description="Default maximum retry attempts for failed jobs",
    )
    queue_backoff_multiplier: float = Field(
        default=2.0,
        alias="QUEUE_BACKOFF_MULTIPLIER",
        description="Multiplier for exponential backoff on repeated failures",
    )
    queue_max_backoff: float = Field(
        default=300.0,
        alias="QUEUE_MAX_BACKOFF",
        description="Maximum backoff time in seconds (5 minutes default)",
    )

    # LangChain Configuration
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com", alias="LANGCHAIN_ENDPOINT"
    )
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="", alias="LANGCHAIN_PROJECT")

    # OpenAI Configuration
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    # Resend Configuration
    resend_api_key: str = Field(default="", alias="RESEND_API_KEY")
    inbound_mail_host: str = Field(
        default="",
        alias="INBOUND_MAIL_HOST",
        description="Root domain for inbound email (e.g., 'acme.bldx.run')",
    )

    # Mistral Configuration
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    mistral_model: str = Field(
        default="mistral-large-latest",
        alias="MISTRAL_MODEL",
        description="Default Mistral model for LangGraph agents",
    )

    # LangGraph Configuration
    langgraph_checkpoint_enabled: bool = Field(
        default=False,
        alias="LANGGRAPH_CHECKPOINT_ENABLED",
        description="Enable LangGraph checkpointing (requires schema setup)",
    )
    langgraph_max_iterations: int = Field(
        default=20,
        alias="LANGGRAPH_MAX_ITERATIONS",
        description="Maximum iterations for agent loops (safety limit)",
    )

    @property
    def supabase_realtime_enabled(self) -> bool:
        """Check if Supabase Realtime should be enabled.

        Realtime is auto-enabled when Supabase is properly configured.
        """
        return bool(self.supabase_url and self.supabase_key)


@lru_cache()
def get_config() -> Config:
    """Get the configuration singleton."""
    return Config()


# Create a singleton config instance
config = get_config()
