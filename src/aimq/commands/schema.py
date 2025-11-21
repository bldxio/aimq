"""Schema management commands."""

import typer
from rich.console import Console

from aimq.commands.shared.config import SupabaseConfig
from aimq.commands.shared.paths import ProjectPath

app = typer.Typer(help="Manage PGMQ schema in Supabase API configuration")
console = Console()


@app.command()
def enable() -> None:
    """Enable PGMQ in Supabase by adding pgmq_public to API schemas.

    This makes the pgmq_public schema accessible via the Supabase API,
    allowing you to send messages and manage queues from your application.

    Example:
        aimq schema enable
    """
    try:
        config = SupabaseConfig(ProjectPath())
        config.enable()
        console.print("[bold green]✓[/bold green] Successfully enabled PGMQ in Supabase config")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to enable PGMQ: {str(e)}", style="red")
        raise typer.Exit(1)


@app.command()
def disable() -> None:
    """Disable PGMQ in Supabase by removing pgmq_public from API schemas.

    This removes the pgmq_public schema from the Supabase API configuration.
    Use this if you want to restrict API access to the queue functions.

    Example:
        aimq schema disable
    """
    try:
        config = SupabaseConfig(ProjectPath())
        config.disable()
        console.print("[bold green]✓[/bold green] Successfully disabled PGMQ in Supabase config")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to disable PGMQ: {str(e)}", style="red")
        raise typer.Exit(1)
