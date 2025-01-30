"""Command for sending jobs to a queue."""

import json
from enum import Enum
from typing import Optional

import typer

from aimq.providers.supabase import SupabaseQueueProvider


class Provider(str, Enum):
    """Provider options for the queue system.

    Supported providers:
        SUPABASE: Use Supabase as the queue provider
    """

    SUPABASE = "supabase"


QUEUE_NAME_ARG = typer.Argument(
    ...,
    help="Name of the queue to send the job to",
)

DATA_ARG = typer.Argument(
    ...,
    help="JSON data to send as the job payload",
)

DELAY_OPTION = typer.Option(
    None,
    "--delay",
    "-d",
    help="Delay in seconds before the job becomes visible",
)

PROVIDER_OPTION = typer.Option(
    Provider.SUPABASE,
    "--provider",
    "-p",
    help="Queue provider to use",
    case_sensitive=False,
)


def send(
    queue_name: str = QUEUE_NAME_ARG,
    data: str = DATA_ARG,
    delay: Optional[int] = DELAY_OPTION,
    provider: Provider = PROVIDER_OPTION,
) -> None:
    """Send a job to a queue with JSON data.

    Args:
        queue_name: Name of the queue to send the job to.
        data: JSON data to send as the job payload.
        delay: Optional delay in seconds before the job becomes visible.
        provider: Queue provider to use. Default is Supabase.

    Raises:
        typer.Exit: If there is an error sending the job.
        json.JSONDecodeError: If the provided data is not valid JSON.
        ValueError: If the specified provider is not supported.
    """
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

        typer.echo(
            f"Successfully sent job {job_id} to queue '{queue_name}' "
            f"using {provider} provider"
        )

    except json.JSONDecodeError:
        typer.echo("Error: Invalid JSON data", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    typer.run(send)
