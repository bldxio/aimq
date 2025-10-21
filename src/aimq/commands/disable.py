"""Command for disabling PGMQ in Supabase."""

import typer

from aimq.commands.shared.config import SupabaseConfig
from aimq.commands.shared.paths import ProjectPath


def disable() -> None:
    """Disable PGMQ in Supabase by removing pgmq_public from API schemas."""
    try:
        config = SupabaseConfig(ProjectPath())
        config.disable()
        typer.echo("Successfully disabled PGMQ in Supabase config")
    except Exception as e:
        typer.echo(f"Failed to disable PGMQ: {str(e)}", err=True)
        raise typer.Exit(1)
