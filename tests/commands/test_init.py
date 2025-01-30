# type: ignore  # mypy is configured to ignore test files in pyproject.toml
"""Tests for the init command functionality.

This module contains tests for the init command, which is responsible for
initializing a new AIMQ project with the required directory structure and files.
"""

from pathlib import Path
from typing import Generator, Optional, Tuple, Union
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app
from aimq.commands.shared.config import SupabaseConfig
from aimq.commands.shared.migration import SupabaseMigrations
from aimq.commands.shared.paths import ProjectPath


class TestInitCommand:
    """Test suite for the init command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner for testing.

        Returns:
            CliRunner: A Typer CLI runner instance for testing command invocations.
        """
        return CliRunner()

    @pytest.fixture
    def mock_dependencies(self) -> Generator[Tuple[Mock, Mock, Mock, Mock], None, None]:
        """Create mocked dependencies for testing.

        Yields:
            Tuple[Mock, Mock, Mock, Mock]: A tuple containing (SupabaseConfig,
                SupabaseMigrations, ProjectPath, Path.mkdir).

        Notes:
            The mocks are set up with default behaviors suitable for testing the init
            command. The Path operations (mkdir, exists, write_text, read_text) are
            mocked to simulate file system operations without actually performing them.
        """
        with (
            patch("aimq.commands.init.SupabaseConfig") as mock_config,
            patch("aimq.commands.init.SupabaseMigrations") as mock_migrations,
            patch("aimq.commands.init.ProjectPath") as mock_path_class,
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch("pathlib.Path.exists") as mock_exists,
            patch("pathlib.Path.write_text") as mock_write_text,
            patch("pathlib.Path.read_text") as mock_read_text,
        ):

            config_instance = Mock(spec=SupabaseConfig)
            migrations_instance = Mock(spec=SupabaseMigrations)

            def create_path_instance(root: Optional[Union[str, Path]] = None) -> Mock:
                """Create a mock ProjectPath instance.

                Args:
                    root: Optional root path for the project. Can be a string,
                        Path, or None.

                Returns:
                    Mock: Configured mock ProjectPath instance.
                """
                path_instance = Mock(spec=ProjectPath)
                path_instance.root = Path(root or ".").resolve()
                path_instance.supabase = path_instance.root / "supabase"
                path_instance.migrations = path_instance.supabase / "migrations"
                return path_instance

            mock_config.return_value = config_instance
            mock_migrations.return_value = migrations_instance
            mock_path_class.side_effect = create_path_instance
            mock_mkdir.return_value = None
            mock_exists.return_value = False
            mock_write_text.return_value = None
            mock_read_text.return_value = "# Template tasks file"

            yield config_instance, migrations_instance, mock_path_class, mock_mkdir

    def test_init_successful(
        self, runner: CliRunner, mock_dependencies: Tuple[Mock, Mock, Mock, Mock]
    ) -> None:
        """Test successful project initialization.

        Args:
            runner: The CLI runner instance.
            mock_dependencies: Tuple of mocked dependencies.

        Raises:
            AssertionError:
                If the command fails or project is not initialized correctly.
        """
        # Arrange
        mock_config, mock_migrations, mock_path_class, mock_mkdir = mock_dependencies
        expected_path = Path(".").resolve()

        # Act
        result = runner.invoke(app, ["init"])

        # Print debug info if test fails
        if result.exit_code != 0:
            print(f"Command failed with output: {result.stdout}")

        # Assert
        assert result.exit_code == 0
        assert (
            "Successfully initialized AIMQ project in "
            f"{expected_path}" in result.stdout
        )
        mock_config.enable.assert_called_once()
        mock_migrations.setup_aimq_migration.assert_called_once()
        mock_path_class.assert_called_once_with(expected_path)
        assert mock_mkdir.call_count == 3  # project_dir, supabase, migrations

    def test_init_with_directory(
        self, runner: CliRunner, mock_dependencies: Tuple[Mock, Mock, Mock, Mock]
    ) -> None:
        """Test project initialization with a specific directory.

        Args:
            runner: The CLI runner instance.
            mock_dependencies: Tuple of mocked dependencies.

        Raises:
            AssertionError: If the command fails or project is not initialized in
                correct directory.
        """
        # Arrange
        mock_config, mock_migrations, mock_path_class, mock_mkdir = mock_dependencies
        test_dir = "test_project"
        expected_path = Path(test_dir).resolve()

        # Act
        result = runner.invoke(app, ["init", test_dir])

        # Print debug info if test fails
        if result.exit_code != 0:
            print(f"Command failed: {result.stdout}")

        # Assert
        assert result.exit_code == 0
        assert (
            "Successfully initialized AIMQ project in "
            f"{expected_path}" in result.stdout
        )
        mock_config.enable.assert_called_once()
        mock_migrations.setup_aimq_migration.assert_called_once()
        mock_path_class.assert_called_once_with(expected_path)
        assert mock_mkdir.call_count == 3  # project_dir, supabase, migrations

    def test_init_failure_config(
        self, runner: CliRunner, mock_dependencies: Tuple[Mock, Mock, Mock, Mock]
    ) -> None:
        """Test handling of config setup failures.

        Args:
            runner: The CLI runner instance.
            mock_dependencies: Tuple of mocked dependencies.

        Raises:
            AssertionError: If config failures are not handled properly.
        """
        # Arrange
        mock_config, _, _, _ = mock_dependencies
        error_message = "Configuration error"
        mock_config.enable.side_effect = Exception(error_message)

        # Act
        result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1
        assert "Failed to initialize AIMQ project: " f"{error_message}" in result.stdout
        mock_config.enable.assert_called_once()

    def test_init_failure_migrations(
        self, runner: CliRunner, mock_dependencies: Tuple[Mock, Mock, Mock, Mock]
    ) -> None:
        """Test handling of migration setup failures.

        Args:
            runner: The CLI runner instance.
            mock_dependencies: Tuple of mocked dependencies.

        Raises:
            AssertionError: If migration failures are not handled properly.
        """
        # Arrange
        _, mock_migrations, _, _ = mock_dependencies
        error_message = "Migration error"
        mock_migrations.setup_aimq_migration.side_effect = Exception(error_message)

        # Act
        result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1
        assert "Failed to initialize AIMQ project: " f"{error_message}" in result.stdout
        mock_migrations.setup_aimq_migration.assert_called_once()

    def test_init_failure_makedirs(self, runner: CliRunner) -> None:
        """Test handling of directory creation failures.

        Args:
            runner: The CLI runner instance.

        Raises:
            AssertionError: If directory creation failures are not handled
                properly.
        """
        # Arrange
        error_message = "Permission denied"
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError(error_message)

            # Act
            result = runner.invoke(app, ["init"])

            # Assert
            assert result.exit_code == 1
            assert (
                "Failed to initialize AIMQ project: "
                f"{error_message}" in result.stdout
            )
