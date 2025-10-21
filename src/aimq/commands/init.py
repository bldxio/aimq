"""Command for initializing a new AIMQ project.

This module provides functionality to initialize a new AIMQ project with the required
directory structure and configuration files.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from aimq.commands.shared.config import SupabaseConfig
from aimq.commands.shared.migration import SupabaseMigrations
from aimq.commands.shared.paths import ProjectPath

console = Console()


def setup_tasks_template(project_dir: Path) -> None:
    """Copy the tasks.py template to the project directory.

    Args:
        project_dir: The project directory path.
    """
    tasks_file = project_dir / "tasks.py"
    if not tasks_file.exists():
        template_tasks = Path(__file__).parent / "shared" / "templates" / "tasks.py"
        tasks_file.write_text(template_tasks.read_text())
        console.print("✓ Created tasks.py template", style="green")
    else:
        console.print("  tasks.py already exists, skipping", style="yellow")


def setup_env_template(project_dir: Path) -> None:
    """Copy the .env.example template to the project directory.

    Args:
        project_dir: The project directory path.
    """
    env_example_file = project_dir / ".env.example"
    if not env_example_file.exists():
        template_env = Path(__file__).parent / "shared" / "templates" / "env.example.template"
        env_example_file.write_text(template_env.read_text())
        console.print("✓ Created .env.example", style="green")
    else:
        console.print("  .env.example already exists, skipping", style="yellow")


def setup_supabase(project_dir: Path) -> None:
    """Set up Supabase configuration and migrations.

    Args:
        project_dir: The project directory path.
    """
    # Create Supabase directories
    (project_dir / "supabase").mkdir(exist_ok=True)
    (project_dir / "supabase" / "migrations").mkdir(exist_ok=True)

    # Initialize project path with the target directory
    project_path = ProjectPath(project_dir)

    # Create and configure Supabase
    config = SupabaseConfig(project_path)
    config.enable()  # Ensure pgmq_public is enabled

    # Create setup migration
    migrations = SupabaseMigrations(project_path)
    migrations.setup_aimq_migration()

    console.print("✓ Configured Supabase and created migrations", style="green")


def setup_docker(project_dir: Path) -> None:
    """Set up Docker configuration files.

    Args:
        project_dir: The project directory path.
    """
    templates_dir = Path(__file__).parent / "shared" / "templates" / "docker"

    # Copy Dockerfile
    dockerfile = project_dir / "Dockerfile"
    if not dockerfile.exists():
        template_dockerfile = templates_dir / "Dockerfile.template"
        dockerfile.write_text(template_dockerfile.read_text())
        console.print("✓ Created Dockerfile", style="green")
    else:
        console.print("  Dockerfile already exists, skipping", style="yellow")

    # Copy docker-compose.yml
    compose_file = project_dir / "docker-compose.yml"
    if not compose_file.exists():
        template_compose = templates_dir / "docker-compose.yml.template"
        compose_file.write_text(template_compose.read_text())
        console.print("✓ Created docker-compose.yml", style="green")
    else:
        console.print("  docker-compose.yml already exists, skipping", style="yellow")

    # Copy .dockerignore
    dockerignore = project_dir / ".dockerignore"
    if not dockerignore.exists():
        template_dockerignore = templates_dir / ".dockerignore.template"
        dockerignore.write_text(template_dockerignore.read_text())
        console.print("✓ Created .dockerignore", style="green")
    else:
        console.print("  .dockerignore already exists, skipping", style="yellow")


def init(
    directory: Optional[str] = typer.Argument(None, help="Directory to initialize AIMQ project in"),
    supabase: bool = typer.Option(None, "--supabase", help="Setup Supabase configuration"),
    docker: bool = typer.Option(None, "--docker", help="Setup Docker files"),
    all_components: bool = typer.Option(False, "--all", help="Setup all components"),
    minimal: bool = typer.Option(False, "--minimal", help="Minimal setup (only tasks.py)"),
) -> None:
    """Initialize a new AIMQ project in the specified directory.

    Creates the required directory structure and configuration files for a new AIMQ project.
    If no directory is specified, initializes in the current directory.

    If no flags are provided, you'll be prompted interactively to choose components.

    Args:
        directory: Optional directory path to initialize project in. Defaults to current directory.
        supabase: Setup Supabase configuration and migrations.
        docker: Setup Docker and docker-compose files.
        all_components: Setup all available components.
        minimal: Create only the basic tasks.py template (no Supabase or Docker).

    Raises:
        typer.Exit: If project initialization fails, exits with status code 1.
        FileNotFoundError: If template files cannot be found.
        PermissionError: If directory creation or file operations fail due to permissions.
    """
    try:
        # Convert directory to absolute Path
        project_dir = Path(directory or ".").resolve()

        console.print(
            Panel.fit(
                f"[bold cyan]Initializing AIMQ project[/bold cyan]\n"
                f"Location: [yellow]{project_dir}[/yellow]",
                border_style="cyan",
            )
        )

        # Create project directory
        project_dir.mkdir(parents=True, exist_ok=True)

        # Determine what to setup
        setup_supabase_flag = supabase
        setup_docker_flag = docker

        # Handle --all flag
        if all_components:
            setup_supabase_flag = True
            setup_docker_flag = True

        # Handle --minimal flag
        if minimal:
            setup_supabase_flag = False
            setup_docker_flag = False

        # If no flags provided and not minimal, ask interactively
        if supabase is None and docker is None and not all_components and not minimal:
            console.print("\n[bold]Select components to setup:[/bold]")
            setup_supabase_flag = typer.confirm("  Setup Supabase configuration?", default=True)
            setup_docker_flag = typer.confirm("  Generate Docker files?", default=True)

        # Show what will be created
        console.print("\n[bold]Components to setup:[/bold]")
        console.print("  • tasks.py template: [green]✓[/green]")
        console.print("  • .env.example: [green]✓[/green]")
        supabase_status = "green]✓" if setup_supabase_flag else "dim]✗"
        console.print(f"  • Supabase config: [{supabase_status}[/]")
        docker_status = "green]✓" if setup_docker_flag else "dim]✗"
        console.print(f"  • Docker files: [{docker_status}[/]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Always setup tasks template and .env.example
            task = progress.add_task("Setting up project files...", total=None)
            setup_tasks_template(project_dir)
            setup_env_template(project_dir)
            progress.update(task, completed=True)

            # Setup Supabase if requested
            if setup_supabase_flag:
                task = progress.add_task("Configuring Supabase...", total=None)
                setup_supabase(project_dir)
                progress.update(task, completed=True)

            # Setup Docker if requested
            if setup_docker_flag:
                task = progress.add_task("Creating Docker files...", total=None)
                setup_docker(project_dir)
                progress.update(task, completed=True)

        # Show success message with next steps
        console.print()
        console.print(
            Panel.fit(
                "[bold green]✓ Project initialized successfully![/bold green]\n\n"
                "[bold]Next steps:[/bold]\n"
                f"1. cd {project_dir.name if directory else '.'}\n"
                "2. Copy .env.example to .env and configure your Supabase credentials\n"
                "3. Edit tasks.py to define your task queues\n"
                f"4. Run: [cyan]{'uvx aimq start' if not docker else 'docker-compose up'}[/cyan]",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"\n[bold red]Failed to initialize AIMQ project:[/bold red] {str(e)}")
        raise typer.Exit(1)
