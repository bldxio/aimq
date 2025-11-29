"""Tests for the start command functionality.

This module contains tests for the start command, which is responsible for
starting the AIMQ worker process.
"""

from pathlib import Path
from typing import Generator, Tuple
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app
from aimq.logger import LogLevel


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner for testing.

    Returns:
        CliRunner: A Typer CLI runner instance for testing command invocations.
    """
    return CliRunner()


@pytest.fixture
def mock_worker() -> Generator[Tuple[Mock, Mock], None, None]:
    """Create a mocked Worker class and instance for testing.

    Yields:
        Tuple[Mock, Mock]: A tuple containing (worker_class_mock, worker_instance_mock).
    """
    with patch("aimq.commands.start.Worker") as mock:
        worker_instance = Mock()
        mock.return_value = worker_instance
        mock.load.return_value = worker_instance
        yield mock, worker_instance


@pytest.fixture
def mock_validations():
    """Mock validation functions to bypass environment checks."""

    def resolve_path_side_effect(path):
        """Return the path as-is if provided, otherwise return default."""
        return Path(path) if path else Path("tasks.py")

    with (
        patch("aimq.commands.start.validate_worker_path"),
        patch("aimq.commands.start.validate_supabase_config"),
        patch("aimq.commands.start.resolve_worker_path", side_effect=resolve_path_side_effect),
    ):
        yield


class TestStartCommand:
    """Tests for the start command in AIMQ CLI."""

    def test_start_without_worker_path(
        self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock], mock_validations
    ) -> None:
        """Test starting AIMQ without specifying a worker path.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).
            mock_validations: Mock validation functions fixture.

        Raises:
            AssertionError: If worker initialization or start fails.
        """
        # Arrange
        mock_class, mock_instance = mock_worker

        # Act
        result = cli_runner.invoke(app, ["start"])

        # Assert
        assert result.exit_code == 0
        mock_class.load.assert_called_once()
        mock_instance.start.assert_called_once()
        assert mock_instance.log_level == LogLevel.INFO

    def test_start_with_worker_path(
        self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock], mock_validations
    ) -> None:
        """Test starting AIMQ with a specific worker path.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).
            mock_validations: Mock validation functions fixture.

        Raises:
            AssertionError: If worker loading or start fails.
        """
        # Arrange
        mock_class, mock_instance = mock_worker
        worker_path = "worker.py"

        # Act
        result = cli_runner.invoke(app, ["start", worker_path])

        # Assert
        assert result.exit_code == 0
        mock_class.load.assert_called_once_with(Path(worker_path))
        mock_instance.start.assert_called_once()

    def test_start_with_debug_flag(
        self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock], mock_validations
    ) -> None:
        """Test starting AIMQ with debug flag enabled.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).
            mock_validations: Mock validation functions fixture.

        Raises:
            AssertionError: If debug mode is not properly set.
        """
        # Arrange
        mock_class, mock_instance = mock_worker

        # Act
        result = cli_runner.invoke(app, ["start", "--debug"])

        # Assert
        assert result.exit_code == 0
        mock_class.load.assert_called_once()
        mock_instance.start.assert_called_once()
        assert mock_instance.log_level == LogLevel.DEBUG

    def test_start_with_custom_log_level(
        self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock], mock_validations
    ) -> None:
        """Test starting AIMQ with a custom log level.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).
            mock_validations: Mock validation functions fixture.

        Raises:
            AssertionError: If custom log level is not properly set.
        """
        # Arrange
        mock_class, mock_instance = mock_worker

        # Act
        result = cli_runner.invoke(app, ["start", "--log-level", "ERROR"])

        # Assert
        assert result.exit_code == 0
        assert mock_instance.log_level == LogLevel.ERROR
        mock_instance.start.assert_called_once()

    def test_start_handles_worker_exception(
        self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock], mock_validations
    ) -> None:
        """Test that exceptions during worker start are handled properly.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).
            mock_validations: Mock validation functions fixture.

        Raises:
            AssertionError: If worker exception is not handled properly.
        """
        # Arrange
        mock_class, mock_instance = mock_worker
        mock_instance.start.side_effect = Exception("Test error")

        # Act
        result = cli_runner.invoke(app, ["start"])

        # Assert
        assert result.exit_code == 1
        mock_instance.logger.error.assert_called_once()
        mock_instance.stop.assert_called_once()
        mock_instance.log.assert_called()
