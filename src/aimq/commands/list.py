"""Command for listing PGMQ queues."""

import typer
from rich.console import Console
from rich.table import Table

from aimq.config import config
from aimq.providers.supabase import SupabaseQueueProvider

console = Console()


def format_age(seconds: int | None) -> str:
    """Format age in seconds to human-readable string."""
    if seconds is None:
        return "-"
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}d"


def list_queues() -> None:
    """List all PGMQ queues with their status and metrics.

    Shows queue name, realtime status, queue length, message ages, and total messages.

    Example:
        aimq list

    Note: Requires SUPABASE_URL and SUPABASE_KEY environment variables.
    The pgmq_public schema must be enabled (run 'aimq enable' if needed).
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

        # List queues via RPC
        with console.status("Fetching queues..."):
            queues = provider.list_queues()

        if not queues:
            console.print("[yellow]No queues found.[/yellow]")
            console.print("\nCreate a queue with: [cyan]aimq create <queue-name>[/cyan]")
            return

        # Create table
        table = Table(title="PGMQ Queues", show_header=True, header_style="bold cyan")
        table.add_column("Queue Name", style="cyan")
        table.add_column("Realtime", justify="center")
        table.add_column("Length", justify="right")
        table.add_column("Total", justify="right")
        table.add_column("Newest", justify="right")
        table.add_column("Oldest", justify="right")

        # Add rows
        for queue in queues:
            realtime_status = (
                "[green]✓[/green]" if queue.get("realtime_enabled") else "[dim]✗[/dim]"
            )
            queue_length = str(queue.get("queue_length", 0))
            total_messages = str(queue.get("total_messages", 0))
            newest_age = format_age(queue.get("newest_msg_age_sec"))
            oldest_age = format_age(queue.get("oldest_msg_age_sec"))

            table.add_row(
                queue["queue_name"],
                realtime_status,
                queue_length,
                total_messages,
                newest_age,
                oldest_age,
            )

        console.print(table)

        # Show legend
        console.print(
            "\n[dim]Length:[/dim] Messages in queue  "
            "[dim]Total:[/dim] All-time message count\n"
            "[dim]Newest/Oldest:[/dim] Message age (s=seconds, m=minutes, h=hours, d=days)"
        )

        # Show hint if any queues don't have realtime enabled
        queues_without_realtime = [q["queue_name"] for q in queues if not q.get("realtime_enabled")]
        if queues_without_realtime:
            console.print(
                "\n[dim]💡 Tip: Enable realtime on queues with:[/dim] "
                "[cyan]aimq enable-realtime <queue-name>[/cyan]"
            )

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
