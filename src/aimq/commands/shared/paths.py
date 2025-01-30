"""Path management for Supabase AIMQ project structure.

This module provides utilities for managing file and directory paths within
a Supabase AIMQ project, including migrations and configuration files.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ProjectPath:
    """Manages project-specific paths for Supabase AIMQ integration.

    This class provides a centralized way to handle paths for various
    project components including Supabase directory, migrations, and
    configuration files.
    """

    def __init__(self, root: Optional[Path] = None):
        """Initialize ProjectPath with a root directory.

        Args:
            root (Optional[Path]): Root directory path. If None, uses current
                working directory.
        """
        self.root = root or Path.cwd()

    @property
    def supabase(self) -> Path:
        """Get the Supabase directory path."""
        return self.root / "supabase"

    @property
    def migrations(self) -> Path:
        """Get the migrations directory path."""
        return self.supabase / "migrations"

    @property
    def supabase_config(self) -> Path:
        """Get the Supabase config file path."""
        return self.supabase / "config.toml"

    def migration_path(self, name: str) -> Path:
        """
        Generate a path for a new migration file.

        Args:
            name (str): The name of the migration.

        Returns:
            Path: The path to the new migration file.
        """
        timestamp = self.get_current_timestamp()
        migration_file = f"{timestamp}_{name}.sql"
        return self.migrations / migration_file

    def find_existing_migration(self, name: str) -> Optional[Path]:
        """
        Check if there is an existing migration file with the given name.

        Args:
            name (str): The name of the migration to search for.

        Returns:
            Optional[Path]: Path to the existing migration if found, None otherwise.
        """
        if not self.migrations.exists():
            return None

        for file in self.migrations.glob(f"*_{name}.sql"):
            return file
        return None

    @staticmethod
    def get_current_timestamp() -> str:
        """Get the current UTC timestamp as a string.

        Format: YYYYMMDDHHMMSS (equivalent to Go's 20060102150405)

        Returns:
            str: Formatted timestamp string.
        """
        return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


# Create a default instance for backward compatibility
default_paths = ProjectPath()
