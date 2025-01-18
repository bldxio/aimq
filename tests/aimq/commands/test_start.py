import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import Mock, patch

from aimq.commands.start import app, start
from aimq.logger import LogLevel
from aimq.worker import Worker

@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture
def mock_worker():
    with patch('aimq.commands.start.Worker') as mock:
        worker_instance = Mock()
        mock.return_value = worker_instance
        mock.load.return_value = worker_instance
        yield mock, worker_instance

class TestStartCommand:
    """Tests for the start command in AIMQ CLI."""
    
    def test_start_without_worker_path(self, cli_runner, mock_worker):
        """Test starting AIMQ without specifying a worker path."""
        mock_class, mock_instance = mock_worker
        
        result = cli_runner.invoke(app, [])
        
        assert result.exit_code == 0
        mock_class.assert_called_once()
        mock_instance.start.assert_called_once()
        assert mock_instance.log_level == LogLevel.INFO

    def test_start_with_worker_path(self, cli_runner, mock_worker):
        """Test starting AIMQ with a specific worker path."""
        mock_class, mock_instance = mock_worker
        worker_path = "worker.py"
        
        result = cli_runner.invoke(app, [worker_path])
        
        assert result.exit_code == 0
        mock_class.load.assert_called_once_with(Path(worker_path))
        mock_instance.start.assert_called_once()

    def test_start_with_debug_flag(self, cli_runner, mock_worker):
        """Test starting AIMQ with debug flag enabled."""
        mock_class, mock_instance = mock_worker
        
        result = cli_runner.invoke(app, ["--debug"])
        
        assert result.exit_code == 0
        assert mock_instance.log_level == LogLevel.DEBUG
        mock_instance.start.assert_called_once()

    def test_start_with_custom_log_level(self, cli_runner, mock_worker):
        """Test starting AIMQ with a custom log level."""
        mock_class, mock_instance = mock_worker
        
        result = cli_runner.invoke(app, ["--log-level", "ERROR"])
        
        assert result.exit_code == 0
        assert mock_instance.log_level == LogLevel.ERROR
        mock_instance.start.assert_called_once()

    def test_start_handles_worker_exception(self, cli_runner, mock_worker):
        """Test that exceptions during worker start are handled properly."""
        mock_class, mock_instance = mock_worker
        mock_instance.start.side_effect = Exception("Test error")
        
        result = cli_runner.invoke(app, [])
        
        assert result.exit_code == 1
        mock_instance.logger.error.assert_called_once()
        mock_instance.stop.assert_called_once()
        mock_instance.log.assert_called()

    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, cli_runner, mock_worker):
        """Test graceful shutdown when receiving SIGINT/SIGTERM signals."""
        mock_class, mock_instance = mock_worker
        
        with patch('aimq.commands.start.signal.signal') as mock_signal, \
             patch('aimq.commands.start.sys.exit') as mock_exit:
            result = cli_runner.invoke(app, [])
            
            # Verify signal handlers were registered
            assert mock_signal.call_count == 2  # SIGINT and SIGTERM
            
            # Get the signal handler function
            signal_handler = mock_signal.call_args_list[0][0][1]
            
            # Simulate signal
            signal_handler(None, None)
            
            # Verify shutdown sequence
            mock_instance.logger.info.assert_called_with("Shutting down...")
            mock_instance.stop.assert_called_once()
            mock_instance.log.assert_called()
            mock_exit.assert_called_with(0)
