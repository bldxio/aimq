"""Command for creating PGMQ queues."""

import typer

from aimq.commands.shared.migration import SupabaseMigrations
from aimq.commands.shared.paths import ProjectPath


def create(
    queue_name: str = typer.Argument(
        ...,
        help="Name of the queue to create",
    ),
) -> None:
    """Create a new PGMQ queue by generating a migration file.

    Queues in pgmq cannot be created via RPC, so this command generates
    a migration file that you can apply using Supabase CLI.

    Example:
        # Generate migration for a new queue
        aimq create my-queue

        # Apply the migration
        supabase db reset
        # Or push to remote
        supabase db push

    Note: You can also create queues via the Supabase Dashboard.
    """
    try:
        # Generate migration file
        project_path = ProjectPath()
        migrations = SupabaseMigrations(project_path)
        migration_path = migrations.create_queue_migration(queue_name)

        typer.echo(f"✓ Created migration: {migration_path.name}")
        typer.echo(
            "\nNext steps:\n"
            "1. Apply locally: supabase db reset\n"
            "2. Or push to remote: supabase db push\n"
            "\nNote: Queues can also be created via the Supabase Dashboard."
        )

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
