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

    # Worker Configuration
    worker_name: str = Field(default="peon", alias="WORKER_NAME")
    worker_path: Path = Field(default=Path("./tasks.py"), alias="WORKER_PATH")

    worker_log_level: str = Field(default="info", alias="WORKER_LOG_LEVEL")
    worker_idle_wait: float = Field(default=10.0, alias="WORKER_IDLE_WAIT")

    # LangChain Configuration
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com", alias="LANGCHAIN_ENDPOINT"
    )
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="", alias="LANGCHAIN_PROJECT")

    # OpenAI Configuration
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    # Mistral Configuration
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")


@lru_cache()
def get_config() -> Config:
    """Get the configuration singleton."""
    return Config()


# Create a singleton config instance
config = get_config()
