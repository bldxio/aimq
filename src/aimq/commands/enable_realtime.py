"""Command for enabling realtime on existing PGMQ queues."""

import typer
from rich.console import Console

from aimq.config import config
from aimq.providers.supabase import SupabaseQueueProvider

console = Console()


def enable_realtime(
    queue_name: str = typer.Argument(..., help="Name of the queue to enable realtime on"),
    channel: str = typer.Option(
        "aimq:jobs",
        "--channel",
        "-c",
        help="Realtime channel name for notifications",
    ),
    event: str = typer.Option(
        "job_enqueued",
        "--event",
        "-e",
        help="Event name for realtime notifications",
    ),
) -> None:
    """Enable realtime notifications on an existing PGMQ queue.

    Upgrades a standard queue to an AIMQ queue with instant worker wake-up.
    Adds a trigger that broadcasts to Supabase Realtime when jobs are enqueued.

    Example:
        aimq enable-realtime my-queue
        aimq enable-realtime my-queue --channel custom:channel --event custom_event

    Note: Requires SUPABASE_URL and SUPABASE_KEY environment variables.
    The setup_aimq migration must be applied first.
    """
    try:
        # Get Supabase credentials from config (loads .env automatically)
        if not config.supabase_url or not config.supabase_key:
            console.print(
                "[bold red]Error:[/bold red] SUPABASE_URL and SUPABASE_KEY "
                "environment variables required.",
                style="red",
            )
            raise typer.Exit(1)

        # Create queue provider
        provider = SupabaseQueueProvider()

        # Enable realtime via RPC
        with console.status(f"Enabling realtime on queue '{queue_name}'..."):
            result = provider.enable_queue_realtime(
                queue_name=queue_name,
                channel_name=channel,
                event_name=event,
            )

        # Show result
        if result.get("success"):
            console.print(
                f"[bold green]✓[/bold green] Successfully enabled realtime on queue "
                f"[cyan]{queue_name}[/cyan]"
            )
            console.print(
                f"\n[dim]Channel:[/dim] {channel}\n"
                f"[dim]Event:[/dim] {event}\n"
                f"[dim]Trigger:[/dim] {result.get('trigger_name', 'N/A')}"
            )
        else:
            error = result.get("error", "Unknown error")
            console.print(f"[bold red]Error:[/bold red] Failed to enable realtime: {error}")
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
                "\n[bold cyan]Need help?[/bold cyan]\n"
                "  Run [cyan]aimq init --supabase[/cyan] to set up a new project with migrations."
            )
        else:
            console.print(f"[bold red]Error:[/bold red] {error_msg}")

        raise typer.Exit(1)
