"""Command for creating PGMQ queues."""

import typer
from rich.console import Console

from aimq.commands.shared.migration import SupabaseMigrations
from aimq.commands.shared.paths import ProjectPath
from aimq.config import config
from aimq.providers.supabase import SupabaseQueueProvider

console = Console()


def create(
    queue_name: str = typer.Argument(
        ...,
        help="Name of the queue to create",
    ),
    migration: bool = typer.Option(
        False,
        "--migration",
        help="Generate a migration file instead of creating via RPC",
    ),
    no_realtime: bool = typer.Option(
        False,
        "--no-realtime",
        help="Create queue without realtime trigger (RPC mode only)",
    ),
) -> None:
    """Create a new PGMQ queue with optional realtime trigger.

    By default, creates the queue immediately via Supabase RPC with realtime enabled.
    Use --migration flag to generate a migration file instead.

    Examples:
        # Create queue with realtime (default)
        aimq create my-queue

        # Create queue without realtime
        aimq create my-queue --no-realtime

        # Generate migration file instead
        aimq create my-queue --migration

    Note: RPC mode requires SUPABASE_URL and SUPABASE_KEY environment variables.
    The pgmq_public schema must be enabled (run 'aimq enable' if needed).
    """
    try:
        if migration:
            # Generate migration file (old behavior)
            project_path = ProjectPath()
            migrations = SupabaseMigrations(project_path)
            migration_path = migrations.create_queue_migration(queue_name)

            console.print(f"✓ Created migration: {migration_path.name}", style="green")
            console.print(
                "\n[bold]Next steps:[/bold]\n"
                "1. Apply locally: [cyan]supabase db reset[/cyan]\n"
                "2. Or push to remote: [cyan]supabase db push[/cyan]"
            )
        else:
            # Create via RPC (new default behavior)
            if not config.supabase_url or not config.supabase_key:
                console.print(
                    "[bold red]Error:[/bold red] SUPABASE_URL and SUPABASE_KEY "
                    "environment variables required for RPC mode.\n"
                    "Use --migration flag to generate a migration file instead.",
                    style="red",
                )
                raise typer.Exit(1)

            # Create queue provider
            provider = SupabaseQueueProvider()

            # Create queue via RPC
            with console.status(f"Creating queue '{queue_name}'..."):
                result = provider.create_queue(queue_name, with_realtime=not no_realtime)

            if result.get("success"):
                console.print(f"✓ Created queue: [cyan]{queue_name}[/cyan]", style="green")
                if result.get("realtime_enabled"):
                    console.print(
                        f"  Realtime: [green]enabled[/green] "
                        f"(channel: {result.get('channel')}, event: {result.get('event')})"
                    )
                else:
                    console.print("  Realtime: [dim]disabled[/dim]")
            else:
                console.print(f"[bold red]Error:[/bold red] {result.get('error', 'Unknown error')}")
                raise typer.Exit(1)

    except Exception as e:
        error_msg = str(e)

        # Check if it's a missing function error (migrations not applied)
        if (
            "PGRST202" in error_msg
            or "function" in error_msg.lower()
            and "not" in error_msg.lower()
        ):
            console.print(
                "\n[bold red]Error:[/bold red] AIMQ database functions not found.\n"
                "\n[bold]The setup_aimq migration needs to be applied.[/bold]\n"
                "\n[bold cyan]For local development:[/bold cyan]\n"
                "  1. Run: [cyan]supabase db reset[/cyan]\n"
                "  2. Or: [cyan]supabase db push[/cyan]\n"
                "\n[bold cyan]For remote database:[/bold cyan]\n"
                "  1. Run: [cyan]supabase db push[/cyan]\n"
                "  2. Or apply via Supabase Dashboard → SQL Editor\n"
                "\n[bold cyan]Alternative:[/bold cyan]\n"
                "  Use [cyan]--migration[/cyan] flag to generate a migration file instead.\n"
                "  Example: [cyan]aimq create {queue_name} --migration[/cyan]"
            )
        else:
            console.print(f"[bold red]Error:[/bold red] {error_msg}")

        raise typer.Exit(1)
