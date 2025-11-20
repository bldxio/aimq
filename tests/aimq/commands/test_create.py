"""Tests for the create command functionality.

This module contains tests for the create command, which creates PGMQ queues
by generating migration files.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner for testing.

    Returns:
        CliRunner: A Typer CLI runner instance for testing command invocations.
    """
    return CliRunner()


@pytest.fixture
def mock_migrations():
    """Create a mocked SupabaseMigrations for testing.

    Yields:
        Mock: A mocked SupabaseMigrations instance.
    """
    with patch("aimq.commands.create.SupabaseMigrations") as mock:
        migrations_instance = Mock()
        mock.return_value = migrations_instance
        migrations_instance.create_queue_migration.return_value = Path(
            "supabase/migrations/20240101000000_create_queue_test.sql"
        )
        yield migrations_instance


@pytest.fixture
def mock_project_path():
    """Create a mocked ProjectPath for testing.

    Yields:
        Mock: A mocked ProjectPath instance.
    """
    with patch("aimq.commands.create.ProjectPath") as mock:
        project_path_instance = Mock()
        mock.return_value = project_path_instance
        yield project_path_instance


class TestCreateCommand:
    """Tests for the create command in AIMQ CLI."""

    def test_create_generates_migration(
        self,
        cli_runner: CliRunner,
        mock_migrations: Mock,
        mock_project_path: Mock,
    ) -> None:
        """Test creating a queue generates a migration file with --migration flag.

        Args:
            cli_runner: The CLI runner instance.
            mock_migrations: Mocked SupabaseMigrations instance.
            mock_project_path: Mocked ProjectPath instance.

        Raises:
            AssertionError: If migration creation fails or output is incorrect.
        """
        # Act
        result = cli_runner.invoke(app, ["create", "test-queue", "--migration"])

        # Assert
        assert result.exit_code == 0
        mock_migrations.create_queue_migration.assert_called_once_with("test-queue")
        assert "Created migration:" in result.stdout
        assert "20240101000000_create_queue_test.sql" in result.stdout
        assert "supabase db reset" in result.stdout
        assert "supabase db push" in result.stdout

    def test_create_migration_error(
        self,
        cli_runner: CliRunner,
        mock_migrations: Mock,
        mock_project_path: Mock,
    ) -> None:
        """Test handling errors during migration file creation.

        Args:
            cli_runner: The CLI runner instance.
            mock_migrations: Mocked SupabaseMigrations instance.
            mock_project_path: Mocked ProjectPath instance.

        Raises:
            AssertionError: If error handling is incorrect.
        """
        # Arrange
        mock_migrations.create_queue_migration.side_effect = Exception("Template not found")

        # Act
        result = cli_runner.invoke(
            app, ["create", "test-queue", "--migration"], catch_exceptions=False
        )

        # Assert
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Error:" in output
        assert "Template not found" in output

    def test_create_with_special_characters(
        self, cli_runner: CliRunner, mock_migrations: Mock, mock_project_path: Mock
    ) -> None:
        """Test creating a queue with special characters in name.

        Args:
            cli_runner: The CLI runner instance.
            mock_migrations: Mocked SupabaseMigrations instance.
            mock_project_path: Mocked ProjectPath instance.

        Raises:
            AssertionError: If queue name is not handled correctly.
        """
        # Act
        result = cli_runner.invoke(app, ["create", "test-queue-123", "--migration"])

        # Assert
        assert result.exit_code == 0
        mock_migrations.create_queue_migration.assert_called_once_with("test-queue-123")

    def test_create_help_message(self, cli_runner: CliRunner) -> None:
        """Test that help message displays correctly.

        Args:
            cli_runner: The CLI runner instance.

        Raises:
            AssertionError: If help message is incorrect.
        """
        # Act
        result = cli_runner.invoke(app, ["create", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "Create a new PGMQ queue" in result.stdout
        assert "queue" in result.stdout.lower()
