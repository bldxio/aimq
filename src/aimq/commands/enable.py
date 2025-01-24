"""Command for enabling PGMQ in Supabase."""

import typer

from aimq.commands.shared.config import SupabaseConfig
from .shared.paths import ProjectPath

def enable() -> None:
    """Enable PGMQ in Supabase by adding pgmq_public to API schemas."""
    try:
        config = SupabaseConfig(ProjectPath())
        config.enable()
        typer.echo("Successfully enabled PGMQ in Supabase config")
    except Exception as e:
        typer.echo(f"Failed to enable PGMQ: {str(e)}", err=True)
        raise typer.Exit(1)
