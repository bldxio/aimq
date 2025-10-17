"""Command for initializing a new AIMQ project.

This module provides functionality to initialize a new AIMQ project with the required
directory structure and configuration files.
"""

from pathlib import Path
from typing import Optional

import typer

from aimq.commands.shared.config import SupabaseConfig
from aimq.commands.shared.migration import SupabaseMigrations
from aimq.commands.shared.paths import ProjectPath


def init(
    directory: Optional[str] = typer.Argument(None, help="Directory to initialize AIMQ project in")
) -> None:
    """Initialize a new AIMQ project in the specified directory.

    Creates the required directory structure and configuration files for a new AIMQ project.
    If no directory is specified, initializes in the current directory.

    Args:
        directory: Optional directory path to initialize project in. Defaults to current directory.

    Raises:
        typer.Exit: If project initialization fails, exits with status code 1.
        FileNotFoundError: If template files cannot be found.
        PermissionError: If directory creation or file operations fail due to permissions.
    """
    try:
        # Convert directory to absolute Path
        project_dir = Path(directory or ".").resolve()
        typer.echo(f"Initializing project in directory: {project_dir}")

        # Create all required directories
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "supabase").mkdir(exist_ok=True)
        (project_dir / "supabase" / "migrations").mkdir(exist_ok=True)

        # Initialize project path with the target directory
        project_path = ProjectPath(project_dir)
        typer.echo(f"Created ProjectPath with root: {project_path.root}")

        # Create and configure Supabase
        config = SupabaseConfig(project_path)
        config.enable()  # Ensure pgmq_public is enabled

        # Create setup migration
        migrations = SupabaseMigrations(project_path)
        migrations.setup_aimq_migration()

        # Copy template tasks.py file if it doesn't exist
        tasks_file = project_path.root / "tasks.py"
        if not tasks_file.exists():
            template_tasks = Path(__file__).parent / "shared" / "templates" / "tasks.py"
            tasks_file.write_text(template_tasks.read_text())

        typer.echo(f"Successfully initialized AIMQ project in {project_path.root}")
    except Exception as e:
        typer.echo(f"Failed to initialize AIMQ project: {str(e)}", err=True)
        raise typer.Exit(1)
