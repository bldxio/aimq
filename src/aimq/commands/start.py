"""Command for starting the AIMQ worker."""

import signal
import sys
from pathlib import Path
from typing import Optional

import typer

from aimq.config import config
from aimq.logger import LogLevel
from aimq.worker import Worker


def resolve_worker_path(worker_path: Optional[Path]) -> Path:
    """Resolve the worker path with fallback logic.

    Args:
        worker_path: Optional worker path provided by user.

    Returns:
        Resolved Path to the worker file.
    """
    if worker_path is None:
        # Check for WORKER_PATH env var or config default
        worker_path = Path(config.worker_path)

        # If the config default doesn't exist, try current directory
        if not worker_path.exists():
            cwd_tasks = Path.cwd() / "tasks.py"
            if cwd_tasks.exists():
                worker_path = cwd_tasks

    return Path(worker_path)


def validate_worker_path(worker_path: Path) -> None:
    """Validate that the worker path exists.

    Args:
        worker_path: Path to validate.

    Raises:
        typer.Exit: If path doesn't exist.
    """
    if not worker_path.exists():
        typer.echo(f"Error: Worker file not found: {worker_path}", err=True)
        typer.echo("\nPlease ensure you have a tasks.py file in your current directory.", err=True)
        typer.echo("You can create one with: uvx aimq init", err=True)
        raise typer.Exit(1)


def validate_supabase_config() -> None:
    """Validate that Supabase configuration is present.

    Raises:
        typer.Exit: If Supabase config is missing.
    """
    if not config.supabase_url or not config.supabase_key:
        typer.echo("Error: Missing Supabase configuration", err=True)
        typer.echo("\nPlease set the following environment variables:", err=True)
        if not config.supabase_url:
            typer.echo("  - SUPABASE_URL", err=True)
        if not config.supabase_key:
            typer.echo("  - SUPABASE_KEY", err=True)
        typer.echo("\nYou can create a .env file with: uvx aimq init", err=True)
        raise typer.Exit(1)


def load_worker_safely(worker_path: Path) -> Worker:
    """Load worker from path with error handling.

    Args:
        worker_path: Path to worker file.

    Returns:
        Loaded Worker instance.

    Raises:
        typer.Exit: If loading fails.
    """
    try:
        return Worker.load(worker_path)
    except AttributeError as e:
        typer.echo(f"Error loading worker: {e}", err=True)
        typer.echo(
            f"\nMake sure {worker_path} exports a 'worker' variable (instance of Worker).",
            err=True,
        )
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error loading worker from {worker_path}: {e}", err=True)
        raise typer.Exit(1)


def start(
    worker_path: Optional[Path] = typer.Argument(
        None,
        help="Path to the Python file containing worker definitions",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO,
        "--log-level",
        "-l",
        help="Set the log level (debug, info, warning, error, critical)",
        case_sensitive=False,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging (shortcut for --log-level debug)",
    ),
):
    """Start the AIMQ worker with the specified tasks.

    If no worker_path is provided, attempts to use:
    1. WORKER_PATH environment variable
    2. ./tasks.py in the current directory
    3. Config default (usually ./tasks.py)
    """
    # Resolve and validate worker path
    resolved_path = resolve_worker_path(worker_path)
    validate_worker_path(resolved_path)
    validate_supabase_config()

    # Load worker
    worker = load_worker_safely(resolved_path)
    worker.log_level = LogLevel.DEBUG if debug else log_level

    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        print("")
        worker.logger.info("Shutting down...")
        worker.log(block=False)
        worker.stop()
        worker.log(block=False)
        sys.exit(0)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        worker.start()
    except Exception as e:
        worker.logger.error(f"Error: {e}")
        worker.log(block=False)
        worker.stop()
        worker.log(block=False)
        sys.exit(1)


if __name__ == "__main__":
    typer.run(start)
