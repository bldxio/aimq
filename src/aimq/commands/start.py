"""Command for starting the AIMQ worker."""

import os
import sys
from pathlib import Path
from typing import Optional

import typer

from aimq.commands.shared.git_loader import GitURLError, is_git_url, load_from_git_url
from aimq.config import config
from aimq.logger import LogLevel
from aimq.worker import Worker


def resolve_worker_path(worker_path: Optional[str]) -> Path:
    """Resolve the worker path with fallback logic.

    Supports:
    - Local file paths: tasks.py, /path/to/tasks.py
    - Git URLs: git:user/repo, git:user/repo@branch, git:host/user/repo#path
    - Environment variable: AIMQ_TASKS

    Args:
        worker_path: Optional worker path or git URL provided by user.

    Returns:
        Resolved Path to the worker file.

    Raises:
        GitURLError: If git URL is invalid or loading fails.
    """
    # Check for environment variable first
    if worker_path is None:
        worker_path = os.getenv("AIMQ_TASKS")

    # If still None, use config default or current directory
    if worker_path is None:
        # Check for WORKER_PATH env var or config default
        worker_path_obj = Path(config.worker_path)

        # If the config default doesn't exist, try current directory
        if not worker_path_obj.exists():
            cwd_tasks = Path.cwd() / "tasks.py"
            if cwd_tasks.exists():
                worker_path_obj = cwd_tasks
        return worker_path_obj

    # Check if it's a git URL
    if is_git_url(worker_path):
        try:
            # Check for SSH preference (git operations might need SSH keys)
            use_ssh = os.getenv("AIMQ_USE_SSH", "false").lower() == "true"
            return load_from_git_url(worker_path, use_ssh=use_ssh)
        except GitURLError as e:
            typer.echo(f"Error loading from git URL: {e}", err=True)
            typer.echo("\nGit URL format: git:user/repo[@ref][#subdir]", err=True)
            typer.echo("Examples:", err=True)
            typer.echo("  git:mycompany/aimq-tasks", err=True)
            typer.echo("  git:mycompany/aimq-tasks@production", err=True)
            typer.echo("  git:mycompany/monorepo#services/worker", err=True)
            raise typer.Exit(1)

    # Treat as local path
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
    worker_path: Optional[str] = typer.Argument(
        None,
        help="Path to tasks.py or git URL (git:user/repo[@ref][#path])",
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

    Supports local files and git URLs:
    - Local: aimq start tasks.py
    - Git URL: aimq start git:user/repo
    - Git branch: aimq start git:user/repo@production
    - Git subdir: aimq start git:user/monorepo#services/worker

    If no worker_path is provided, attempts to use:
    1. AIMQ_TASKS environment variable (can be local path or git URL)
    2. WORKER_PATH environment variable
    3. ./tasks.py in the current directory
    4. Config default (usually ./tasks.py)
    """
    # Resolve and validate worker path
    resolved_path = resolve_worker_path(worker_path)
    validate_worker_path(resolved_path)
    validate_supabase_config()

    # Load worker
    worker = load_worker_safely(resolved_path)
    worker.log_level = LogLevel.DEBUG if debug else log_level

    # Signal handlers are now registered automatically in worker.start()
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
