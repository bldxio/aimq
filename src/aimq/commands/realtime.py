"""Realtime management commands."""

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from aimq.config import config
from aimq.providers.supabase import SupabaseQueueProvider

app = typer.Typer(help="Manage Supabase Realtime notifications for queues")
console = Console()


def _get_provider() -> SupabaseQueueProvider:
    """Get Supabase queue provider with validation."""
    if not config.supabase_url or not config.supabase_key:
        console.print(
            "[bold red]Error:[/bold red] SUPABASE_URL and SUPABASE_KEY "
            "environment variables required.",
            style="red",
        )
        raise typer.Exit(1)
    return SupabaseQueueProvider()


def _list_queues_with_realtime(provider: SupabaseQueueProvider) -> list[dict]:
    """Get list of all queues with realtime status."""
    try:
        queues = provider.list_queues()
        # list_queues() returns a list directly, not a dict
        if not isinstance(queues, list):
            console.print("[bold red]Error:[/bold red] Unexpected response format")
            raise typer.Exit(1)
        return queues
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def _select_queues(queues: list[dict], enabled_filter: bool = None) -> list[str]:
    """Show interactive menu to select queues.

    Args:
        queues: List of queue dicts with name and realtime_enabled
        enabled_filter: If True, only show queues with realtime enabled.
                       If False, only show queues without realtime.
                       If None, show all queues.

    Returns:
        List of selected queue names
    """
    # Filter queues based on realtime status
    if enabled_filter is not None:
        queues = [q for q in queues if q.get("realtime_enabled") == enabled_filter]

    if not queues:
        if enabled_filter is True:
            console.print("[yellow]No queues with realtime enabled.[/yellow]")
        elif enabled_filter is False:
            console.print("[yellow]No queues without realtime.[/yellow]")
        else:
            console.print("[yellow]No queues found.[/yellow]")
        raise typer.Exit(0)

    # Show table of queues
    table = Table(title="Available Queues")
    table.add_column("Queue Name", style="cyan")
    table.add_column("Realtime", style="green")
    table.add_column("Messages", justify="right")

    for queue in queues:
        realtime_status = "✓" if queue.get("realtime_enabled") else "✗"
        table.add_row(
            queue["queue_name"],
            realtime_status,
            str(queue.get("queue_length", 0)),
        )

    console.print(table)
    console.print()

    # Prompt for selection
    queue_names = [q["queue_name"] for q in queues]
    console.print("[dim]Enter queue names separated by commas, or 'all' for all queues:[/dim]")
    selection = Prompt.ask("Select queues", default="all")

    if selection.lower() == "all":
        return queue_names

    # Parse comma-separated list
    selected = [name.strip() for name in selection.split(",")]

    # Validate selections
    invalid = [name for name in selected if name not in queue_names]
    if invalid:
        console.print(f"[red]Invalid queue names: {', '.join(invalid)}[/red]")
        raise typer.Exit(1)

    return selected


@app.command()
def enable(
    queue_name: str = typer.Argument(
        None, help="Name of the queue (optional, interactive if not provided)"
    ),
    channel: str = typer.Option(
        None,
        "--channel",
        "-c",
        help="Realtime channel name (default: aimq:jobs)",
    ),
    event: str = typer.Option(
        None,
        "--event",
        "-e",
        help="Event name (default: job_enqueued)",
    ),
) -> None:
    """Enable realtime notifications on queue(s).

    If no queue name is provided, shows an interactive menu to select queues.

    Example:
        aimq realtime enable my-queue
        aimq realtime enable  # Interactive selection
        aimq realtime enable --channel custom:channel --event custom_event my-queue
    """
    try:
        provider = _get_provider()

        # If no queue specified, show interactive selection
        if not queue_name:
            queues = _list_queues_with_realtime(provider)
            # Only show queues without realtime enabled
            queue_names = _select_queues(queues, enabled_filter=False)
        else:
            queue_names = [queue_name]

        # Use defaults if not specified
        channel_name = channel or config.supabase_realtime_channel
        event_name = event or config.supabase_realtime_event

        # Enable realtime on selected queues
        success_count = 0
        for name in queue_names:
            with console.status(f"Enabling realtime on '{name}'..."):
                result = provider.enable_queue_realtime(
                    queue_name=name,
                    channel_name=channel_name,
                    event_name=event_name,
                )

            if result.get("success"):
                console.print(
                    f"[bold green]✓[/bold green] Enabled realtime on queue [cyan]{name}[/cyan]"
                )
                success_count += 1
            else:
                error = result.get("error", "Unknown error")
                console.print(f"[bold red]✗[/bold red] Failed to enable {name}: {error}")

        if success_count > 0:
            console.print(
                f"\n[dim]Channel:[/dim] {channel_name}\n" f"[dim]Event:[/dim] {event_name}"
            )

    except Exception as e:
        error_msg = str(e)
        if "function" in error_msg.lower() and "does not exist" in error_msg.lower():
            console.print(
                "\n[bold red]Error:[/bold red] Required database functions not found.",
                style="red",
            )
            console.print("\n[yellow]The setup_aimq migration must be applied first.[/yellow]")
            console.print("\nRun this SQL in your Supabase SQL editor:")
            console.print("[dim]https://supabase.com/dashboard/project/_/sql/new[/dim]\n")
            console.print(
                "Then paste the contents of:\n"
                "[cyan]src/aimq/commands/shared/templates/setup_aimq.sql[/cyan]"
            )
            raise typer.Exit(1)

        console.print(f"[bold red]Error:[/bold red] {error_msg}", style="red")
        raise typer.Exit(1)


@app.command()
def disable(
    queue_name: str = typer.Argument(
        None, help="Name of the queue (optional, interactive if not provided)"
    ),
) -> None:
    """Disable realtime notifications on queue(s).

    If no queue name is provided, shows an interactive menu to select queues.

    Example:
        aimq realtime disable my-queue
        aimq realtime disable  # Interactive selection
    """
    try:
        provider = _get_provider()

        # If no queue specified, show interactive selection
        if not queue_name:
            queues = _list_queues_with_realtime(provider)
            # Only show queues with realtime enabled
            queue_names = _select_queues(queues, enabled_filter=True)
        else:
            queue_names = [queue_name]

        # Disable realtime on selected queues
        success_count = 0
        for name in queue_names:
            with console.status(f"Disabling realtime on '{name}'..."):
                result = provider.disable_queue_realtime(queue_name=name)

            if result.get("success"):
                console.print(
                    f"[bold green]✓[/bold green] Disabled realtime on queue [cyan]{name}[/cyan]"
                )
                success_count += 1
            else:
                error = result.get("error", "Unknown error")
                console.print(f"[bold red]✗[/bold red] Failed to disable {name}: {error}")

        if success_count > 0:
            console.print(
                f"\n[green]Successfully disabled realtime on {success_count} queue(s)[/green]"
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show realtime status for all queues.

    Displays a table showing which queues have realtime enabled.

    Example:
        aimq realtime status
    """
    try:
        provider = _get_provider()
        queues = _list_queues_with_realtime(provider)

        if not queues:
            console.print("[yellow]No queues found.[/yellow]")
            return

        # Show detailed table
        table = Table(title="Queue Realtime Status")
        table.add_column("Queue Name", style="cyan")
        table.add_column("Realtime", style="green")
        table.add_column("Messages", justify="right")
        table.add_column("Oldest", justify="right")
        table.add_column("Newest", justify="right")

        for queue in queues:
            realtime_status = (
                "[green]✓ Enabled[/green]"
                if queue.get("realtime_enabled")
                else "[dim]✗ Disabled[/dim]"
            )
            table.add_row(
                queue["queue_name"],
                realtime_status,
                str(queue.get("queue_length", 0)),
                str(queue.get("oldest_msg_age_sec", "-")),
                str(queue.get("newest_msg_age_sec", "-")),
            )

        console.print(table)

        # Show summary
        enabled_count = sum(1 for q in queues if q.get("realtime_enabled"))
        console.print(
            f"\n[dim]Total queues:[/dim] {len(queues)} "
            f"[dim]| Realtime enabled:[/dim] {enabled_count}"
        )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
