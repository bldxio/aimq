"""Tests for the start command functionality.

This module contains tests for the start command, which is responsible for
starting the AIMQ worker process.
"""

from pathlib import Path
from typing import Tuple, Generator
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app
from aimq.logger import LogLevel
from aimq.worker import Worker


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
    with patch('aimq.commands.start.Worker') as mock:
        worker_instance = Mock()
        mock.return_value = worker_instance
        mock.load.return_value = worker_instance
        yield mock, worker_instance


class TestStartCommand:
    """Tests for the start command in AIMQ CLI."""
    
    def test_start_without_worker_path(self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock]) -> None:
        """Test starting AIMQ without specifying a worker path.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).

        Raises:
            AssertionError: If worker initialization or start fails.
        """
        # Arrange
        mock_class, mock_instance = mock_worker
        
        # Act
        result = cli_runner.invoke(app, ["start"])
        
        # Assert
        assert result.exit_code == 0
        mock_class.assert_called_once()
        mock_instance.start.assert_called_once()
        assert mock_instance.log_level == LogLevel.INFO

    def test_start_with_worker_path(self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock]) -> None:
        """Test starting AIMQ with a specific worker path.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).

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

    def test_start_with_debug_flag(self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock]) -> None:
        """Test starting AIMQ with debug flag enabled.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).

        Raises:
            AssertionError: If debug mode is not properly set.
        """
        # Arrange
        mock_class, mock_instance = mock_worker
        
        # Act
        result = cli_runner.invoke(app, ["start", "--debug"])
        
        # Assert
        assert result.exit_code == 0
        mock_class.assert_called_once()
        mock_instance.start.assert_called_once()
        assert mock_instance.log_level == LogLevel.DEBUG

    def test_start_with_custom_log_level(self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock]) -> None:
        """Test starting AIMQ with a custom log level.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).

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

    def test_start_handles_worker_exception(self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock]) -> None:
        """Test that exceptions during worker start are handled properly.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).

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

    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, cli_runner: CliRunner, mock_worker: Tuple[Mock, Mock]) -> None:
        """Test graceful shutdown when receiving SIGINT/SIGTERM signals.

        Args:
            cli_runner: The CLI runner instance.
            mock_worker: Tuple of (worker_class_mock, worker_instance_mock).

        Raises:
            AssertionError: If shutdown sequence is not properly executed.
        """
        # Arrange
        mock_class, mock_instance = mock_worker
        
        # Act
        with patch('aimq.commands.start.signal.signal') as mock_signal, \
             patch('aimq.commands.start.sys.exit') as mock_exit:
            result = cli_runner.invoke(app, ["start"])
            
            # Verify signal handlers were registered
            assert mock_signal.call_count == 2  # SIGINT and SIGTERM
            
            # Get the signal handler function
            signal_handler = mock_signal.call_args_list[0][0][1]
            
            # Simulate signal
            signal_handler(None, None)
            
            # Assert
            mock_instance.logger.info.assert_called_with("Shutting down...")
            mock_instance.stop.assert_called_once()
            mock_instance.log.assert_called()
            mock_exit.assert_called_with(0)
