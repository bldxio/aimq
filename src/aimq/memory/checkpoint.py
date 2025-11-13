"""Supabase-backed checkpointing for LangGraph workflows."""

import logging
import re
from urllib.parse import quote_plus

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from aimq.common.exceptions import CheckpointerError
from aimq.config import config

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
        conn_string = _build_connection_string()

        pool = ConnectionPool(
            conninfo=conn_string,
            max_size=20,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
                "row_factory": dict_row,
            },
        )

        _checkpointer_instance = PostgresSaver(conn=pool)

        _setup_schema(_checkpointer_instance)

    assert _checkpointer_instance is not None
    return _checkpointer_instance


def _build_connection_string() -> str:
    """Build PostgreSQL connection string with flexible configuration.

    Supports multiple deployment scenarios:
    1. Direct DATABASE_URL override (highest priority)
    2. Smart parsing of SUPABASE_URL (cloud/self-hosted/local/docker)
    3. Manual configuration via DATABASE_HOST, DATABASE_PORT, etc.

    Smart defaults for local Supabase (localhost/127.0.0.1):
    - Port: Automatically uses 54322 (local Supabase default from `supabase start`)
    - Password: Automatically uses "postgres" (local DB password, not the JWT token)
    - Cloud/self-hosted use port 5432 and SUPABASE_KEY unless overridden

    Returns:
        PostgreSQL connection URL with encoded credentials

    Raises:
        CheckpointerError: If configuration is invalid or missing

    Examples:
        Direct: postgresql://user:pass@host:5432/dbname
        Cloud: postgresql://postgres:jwt_token@db.project.supabase.co:5432/postgres
        Self-hosted: postgresql://postgres:jwt_token@supabase.company.com:5432/postgres
        Local: postgresql://postgres:postgres@localhost:54322/postgres (auto-detected!)
        Docker: postgresql://postgres:pw@supabase-db:5432/postgres
    """
    if config.database_url:
        logger.info("Using direct DATABASE_URL configuration")
        return config.database_url

    user = config.database_user
    port = config.database_port
    db_name = config.database_name

    if not config.database_host:
        if not config.supabase_url:
            raise CheckpointerError(
                "Database host required. Set DATABASE_HOST or SUPABASE_URL environment variable."
            )

        host = _extract_database_host(config.supabase_url)
        logger.debug(f"Extracted database host from SUPABASE_URL: {host}")
    else:
        host = config.database_host
        logger.debug(f"Using explicit DATABASE_HOST: {host}")

    is_localhost = host in ("localhost", "127.0.0.1")

    if port == 5432 and is_localhost:
        port = 54322
        logger.debug("Detected localhost, using port 54322 for local Supabase")

    if not config.database_password and is_localhost:
        password = "postgres"
        logger.debug("Detected localhost, using default password 'postgres' for local Supabase")
    else:
        password = config.database_password or config.supabase_key
        if not password:
            raise CheckpointerError(
                "Database password required. Set DATABASE_PASSWORD or SUPABASE_KEY environment variable."
            )

    encoded_password = quote_plus(password)

    conn_string = f"postgresql://{user}:{encoded_password}@{host}:{port}/{db_name}"

    logger.info(f"Built PostgreSQL connection string (host={host}, port={port}, db={db_name})")
    return conn_string


def _extract_database_host(supabase_url: str) -> str:
    """Extract database hostname from SUPABASE_URL with flexible pattern matching.

    Supports:
    - Supabase Cloud: https://PROJECT.supabase.co → db.PROJECT.supabase.co
    - Self-hosted: https://supabase.company.com → supabase.company.com
    - Local HTTP: http://localhost:54321 → localhost
    - Local HTTPS: https://localhost:54321 → localhost
    - Docker: http://supabase:8000 → supabase

    Args:
        supabase_url: Supabase API URL

    Returns:
        Database hostname to connect to

    Raises:
        CheckpointerError: If URL format is invalid
    """
    cloud_match = re.search(r"https://(.+?)\.supabase\.co", supabase_url)
    if cloud_match:
        project_ref = cloud_match.group(1)
        logger.debug(f"Detected Supabase Cloud project: {project_ref}")
        return f"db.{project_ref}.supabase.co"

    url_match = re.search(r"https?://([^:/]+)", supabase_url)
    if url_match:
        hostname = url_match.group(1)
        logger.debug(f"Detected self-hosted/local Supabase: {hostname}")

        if hostname not in ("localhost", "127.0.0.1") and not hostname.startswith("db."):
            if "supabase" in hostname.lower() or "." not in hostname:
                return hostname
            logger.debug(f"Self-hosted domain detected, using db. prefix: db.{hostname}")
            return f"db.{hostname}"

        return hostname

    raise CheckpointerError(
        f"Invalid SUPABASE_URL format: {supabase_url}. "
        f"Expected format: http(s)://hostname or https://PROJECT.supabase.co"
    )


def _setup_schema(saver: PostgresSaver) -> None:
    """Setup checkpoint schema using PostgresSaver's built-in setup() method.

    This uses LangGraph's official schema creation that creates 4 tables:
    - checkpoints: Main checkpoint storage
    - checkpoint_blobs: Large binary data storage
    - checkpoint_writes: Write operations tracking
    - checkpoint_migrations: Schema version tracking

    The setup is automatic in development but may require manual schema
    creation in production environments with restricted database permissions.

    Args:
        saver: PostgresSaver instance to setup

    Raises:
        CheckpointerError: If schema setup fails
    """
    try:
        saver.setup()
        logger.info(
            "LangGraph checkpoint schema initialized successfully via PostgresSaver.setup()"
        )

    except Exception as e:
        error_msg = str(e).lower()

        if "already exists" in error_msg or "duplicate" in error_msg:
            logger.debug("LangGraph checkpoint tables already exist")
            return

        if "permission denied" in error_msg or "access denied" in error_msg:
            logger.warning(
                "Cannot create checkpoint schema automatically (permission denied). "
                "For production environments, create the schema manually:\n"
                "1. Run PostgresSaver.setup() with admin credentials once\n"
                "2. Or use the SQL in docs/deployment/langgraph-schema.sql\n"
                "3. Then restart with standard database user credentials"
            )
            raise CheckpointerError(
                "Checkpoint schema setup failed due to permissions. "
                "Create schema manually with database admin credentials."
            ) from e

        logger.error(f"Failed to create checkpoint schema: {e}", exc_info=True)
        raise CheckpointerError(
            f"Checkpoint schema setup failed: {e}. "
            "Try creating schema manually via database admin."
        ) from e
