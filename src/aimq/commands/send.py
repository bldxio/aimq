"""Command for sending jobs to a queue."""

import json
from enum import Enum
from typing import Optional
import typer

from aimq.providers.supabase import SupabaseQueueProvider

class Provider(str, Enum):
    SUPABASE = "supabase"

def send(
    queue_name: str = typer.Argument(
        ...,
        help="Name of the queue to send the job to",
    ),
    data: str = typer.Argument(
        ...,
        help="JSON data to send as the job payload",
    ),
    delay: Optional[int] = typer.Option(
        None,
        "--delay",
        "-d",
        help="Delay in seconds before the job becomes visible",
    ),
    provider: Provider = typer.Option(
        Provider.SUPABASE,
        "--provider",
        "-p",
        help="Queue provider to use",
        case_sensitive=False,
    ),
) -> None:
    """Send a job to a queue with JSON data."""
    try:
        # Parse the JSON data
        job_data = json.loads(data)
        
        # Create provider instance based on selection
        if provider == Provider.SUPABASE:
            queue_provider = SupabaseQueueProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Send the job
        job_id = queue_provider.send(queue_name, job_data, delay=delay)
        
        typer.echo(f"Successfully sent job {job_id} to queue '{queue_name}' using {provider} provider")
        
    except json.JSONDecodeError:
        typer.echo("Error: Invalid JSON data", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    send()
