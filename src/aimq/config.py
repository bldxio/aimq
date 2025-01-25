import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, get_type_hints
from pydantic import Field
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """Configuration class for the application."""
    model_config = {
        'case_sensitive': False,
        'env_file': '.env',
        'use_enum_values': True,
        'extra': 'ignore'
    }
    
    # Supabase Configuration
    # Defaults to local Supabase instance
    supabase_url: str = Field(default='http://127.0.0.1:54321', alias='SUPABASE_URL')
    supabase_key: str = Field(default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU', alias='SUPABASE_KEY')

    # Worker Configuration
    worker_name: str = Field(default='peon', alias='WORKER_NAME')
    worker_log_level: str = Field(default='info', alias='WORKER_LOG_LEVEL')
    worker_idle_wait: float = Field(default=10.0, alias='WORKER_IDLE_WAIT')
    
    # LangChain Configuration
    # Used for debugging and tracing using langsmith
    langchain_tracing_v2: bool = Field(default=False, alias='LANGCHAIN_TRACING_V2')
    langchain_endpoint: str = Field(default='https://api.smith.langchain.com', alias='LANGCHAIN_ENDPOINT')
    langchain_api_key: str = Field(default='', alias='LANGCHAIN_API_KEY')
    langchain_project: str = Field(default='', alias='LANGCHAIN_PROJECT')
    
    # OpenAI Configuration
    openai_api_key: str = Field(default='', alias='OPENAI_API_KEY')


@lru_cache()
def get_config() -> Config:
    """Get the configuration singleton."""
    return Config()

# Create a singleton config instance
config = get_config()
