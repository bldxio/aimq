"""Tests for the enable command functionality.

This module contains tests for the enable command, which is responsible for
enabling PGMQ in Supabase by configuring the necessary schemas.
"""

from typing import Generator
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app
from aimq.commands.shared.config import SupabaseConfig
from aimq.commands.shared.paths import ProjectPath


class TestEnableCommand:
    """Test suite for the enable command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner for testing.

        Returns:
            CliRunner: A Typer CLI runner instance for testing command invocations.
        """
        return CliRunner()

    @pytest.fixture
    def mock_supabase_config(self) -> Generator[Mock, None, None]:
        """Create a mocked SupabaseConfig for testing.

        Yields:
            Mock: A mock instance of SupabaseConfig with predefined behavior.

        Notes:
            This fixture also mocks the ProjectPath class to avoid filesystem operations.
        """
        with (
            patch("aimq.commands.enable.SupabaseConfig") as mock_config,
            patch("aimq.commands.enable.ProjectPath") as mock_path,
        ):
            instance = Mock(spec=SupabaseConfig)
            mock_config.return_value = instance
            mock_path.return_value = Mock(spec=ProjectPath)
            yield instance

    def test_enable_successful(self, runner: CliRunner, mock_supabase_config: Mock) -> None:
        """Test successful PGMQ enabling in Supabase.

        Args:
            runner: The CLI runner instance.
            mock_supabase_config: Mock of the SupabaseConfig.

        Raises:
            AssertionError: If the command fails or config is not enabled correctly.
        """
        # Arrange
        mock_supabase_config.enable.return_value = None

        # Act
        result = runner.invoke(app, ["enable"])

        # Assert
        assert result.exit_code == 0
        assert "Successfully enabled PGMQ in Supabase config" in result.stdout
        mock_supabase_config.enable.assert_called_once()

    def test_enable_failure(self, runner: CliRunner, mock_supabase_config: Mock) -> None:
        """Test handling of PGMQ enable failures.

        Args:
            runner: The CLI runner instance.
            mock_supabase_config: Mock of the SupabaseConfig.

        Raises:
            AssertionError: If enable failures are not handled properly.
        """
        # Arrange
        error_message = "Configuration error"
        mock_supabase_config.enable.side_effect = Exception(error_message)

        # Act
        result = runner.invoke(app, ["enable"])

        # Assert
        assert result.exit_code == 1
        # Error messages are written to stderr, but CliRunner combines them in output
        assert f"Failed to enable PGMQ: {error_message}" in result.output
        mock_supabase_config.enable.assert_called_once()

    def test_enable_project_path_error(self, runner: CliRunner) -> None:
        """Test handling of project path errors.

        Args:
            runner: The CLI runner instance.

        Raises:
            AssertionError: If project path errors are not handled properly.
        """
        # Arrange
        error_message = "Invalid project path"
        with patch("aimq.commands.enable.ProjectPath") as mock_path:
            mock_path.side_effect = Exception(error_message)

            # Act
            result = runner.invoke(app, ["enable"])

            # Assert
            assert result.exit_code == 1
            # Error messages are written to stderr, but CliRunner combines them in output
            assert f"Failed to enable PGMQ: {error_message}" in result.output
