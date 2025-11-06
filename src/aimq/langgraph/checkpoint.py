"""Supabase-backed checkpointing for LangGraph workflows."""

import logging
import re
from urllib.parse import quote_plus

from langgraph.checkpoint.postgres import PostgresSaver

from aimq.config import config
from aimq.langgraph.exceptions import CheckpointerError

logger = logging.getLogger(__name__)

_checkpointer_instance: PostgresSaver | None = None


def get_checkpointer() -> PostgresSaver:
    """Get or create Supabase checkpoint saver singleton.

    Returns:
        PostgresSaver instance connected to Supabase PostgreSQL

    Raises:
        CheckpointerError: If Supabase configuration is invalid
    """
    global _checkpointer_instance

    if _checkpointer_instance is None:
        # Build PostgreSQL connection string from Supabase config
        conn_string = _build_connection_string()
        # PostgresSaver.from_conn_string is a context manager, we use sync mode
        with PostgresSaver.from_conn_string(conn_string) as saver:  # type: ignore
            _ensure_schema()
            # Store the saver for reuse (note: in production you'd manage lifecycle)
            _checkpointer_instance = saver

    # At this point, _checkpointer_instance is guaranteed to be PostgresSaver
    assert _checkpointer_instance is not None
    return _checkpointer_instance


def _build_connection_string() -> str:
    """Build PostgreSQL connection string from Supabase config (Fix #7).

    Returns:
        PostgreSQL connection URL with encoded credentials

    Raises:
        CheckpointerError: If Supabase config is invalid or missing

    Examples:
        postgresql://postgres:encoded_pw@db.project.supabase.co:5432/postgres
    """
    url = config.supabase_url
    password = config.supabase_key

    if not url:
        raise CheckpointerError(
            "SUPABASE_URL required for checkpointing. " "Set environment variable or .env file."
        )

    if not password:
        raise CheckpointerError(
            "SUPABASE_KEY required for checkpointing. " "Set environment variable or .env file."
        )

    # Extract project reference from URL
    match = re.search(r"https://(.+?)\.supabase\.co", url)
    if not match:
        raise CheckpointerError(
            f"Invalid SUPABASE_URL format: {url}. " f"Expected format: https://PROJECT.supabase.co"
        )

    project_ref = match.group(1)
    logger.debug(f"Extracted Supabase project: {project_ref}")

    # URL-encode password to handle special characters (Fix #7)
    encoded_password = quote_plus(password)

    # Build connection string
    conn_string = (
        f"postgresql://postgres:{encoded_password}" f"@db.{project_ref}.supabase.co:5432/postgres"
    )

    logger.info("Built Supabase PostgreSQL connection string")
    return conn_string


def _ensure_schema() -> None:
    """Ensure langgraph schema and tables exist (Fix #8).

    WARNING: This requires database admin access. In production,
    create the schema manually via Supabase dashboard:

    1. Go to SQL Editor in Supabase
    2. Run the schema creation SQL (see below)
    3. Set LANGGRAPH_CHECKPOINT_ENABLED=true

    This function will check if schema exists and warn if it needs setup.

    Raises:
        CheckpointerError: If schema creation fails with unexpected error
    """
    try:
        from postgrest.exceptions import APIError

        from aimq.clients.supabase import supabase
    except ImportError:
        logger.warning(
            "Cannot verify checkpoint schema: Supabase client not available. "
            "Ensure schema exists manually.",
            exc_info=True,
        )
        return

    client = supabase.client

    schema_sql = """
    -- LangGraph Checkpoint Schema
    CREATE SCHEMA IF NOT EXISTS langgraph;

    -- Checkpoints table
    CREATE TABLE IF NOT EXISTS langgraph.checkpoints (
        thread_id TEXT NOT NULL,
        checkpoint_id TEXT NOT NULL,
        parent_checkpoint_id TEXT,
        checkpoint JSONB NOT NULL,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (thread_id, checkpoint_id)
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
        ON langgraph.checkpoints(thread_id);
    CREATE INDEX IF NOT EXISTS idx_checkpoints_created
        ON langgraph.checkpoints(created_at);
    CREATE INDEX IF NOT EXISTS idx_checkpoints_parent
        ON langgraph.checkpoints(parent_checkpoint_id);
    """

    try:
        # Attempt to create schema
        client.rpc("exec_sql", {"sql": schema_sql}).execute()
        logger.info("LangGraph checkpoint schema initialized successfully")

    except APIError as e:
        error_msg = str(e).lower()

        # Check if error is benign (schema already exists)
        if any(phrase in error_msg for phrase in ["already exists", "duplicate"]):
            logger.debug("LangGraph schema already exists")

        # Permission error - provide instructions
        elif "permission denied" in error_msg or "access denied" in error_msg:
            logger.warning(
                "Cannot create checkpoint schema (permission denied). "
                "Please create manually via Supabase SQL Editor. "
                "SQL script available in docs/deployment/langgraph-schema.sql"
            )

        # Other API errors
        else:
            logger.error(f"Failed to create checkpoint schema: {e}")
            raise CheckpointerError(
                "Checkpoint schema setup failed. "
                "Create manually via Supabase dashboard or disable checkpointing."
            ) from e

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error during schema setup: {e}", exc_info=True)
        raise CheckpointerError(f"Failed to initialize checkpoint schema: {e}") from e
