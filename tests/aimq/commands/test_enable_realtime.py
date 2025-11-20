"""Tests for enable-realtime command."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app

runner = CliRunner()


@pytest.fixture
def mock_config():
    """Mock config with Supabase credentials."""
    with patch("aimq.commands.enable_realtime.config") as mock:
        mock.supabase_url = "https://test.supabase.co"
        mock.supabase_key = "test-key"
        yield mock


@pytest.fixture
def mock_provider():
    """Mock SupabaseQueueProvider."""
    with patch("aimq.commands.enable_realtime.SupabaseQueueProvider") as mock:
        provider = MagicMock()
        mock.return_value = provider
        yield provider


def test_enable_realtime_success(mock_config, mock_provider):
    """Test successful realtime enablement."""
    mock_provider.enable_queue_realtime.return_value = {
        "success": True,
        "trigger_name": "aimq_notify_test_queue",
    }

    result = runner.invoke(app, ["enable-realtime", "test-queue"])

    assert result.exit_code == 0
    assert "Successfully enabled realtime" in result.stdout
    assert "test-queue" in result.stdout
    mock_provider.enable_queue_realtime.assert_called_once_with(
        queue_name="test-queue",
        channel_name="aimq:jobs",
        event_name="job_enqueued",
    )


def test_enable_realtime_with_custom_channel(mock_config, mock_provider):
    """Test realtime enablement with custom channel and event."""
    mock_provider.enable_queue_realtime.return_value = {
        "success": True,
        "trigger_name": "aimq_notify_test_queue",
    }

    result = runner.invoke(
        app,
        [
            "enable-realtime",
            "test-queue",
            "--channel",
            "custom:channel",
            "--event",
            "custom_event",
        ],
    )

    assert result.exit_code == 0
    mock_provider.enable_queue_realtime.assert_called_once_with(
        queue_name="test-queue",
        channel_name="custom:channel",
        event_name="custom_event",
    )


def test_enable_realtime_failure(mock_config, mock_provider):
    """Test failed realtime enablement."""
    mock_provider.enable_queue_realtime.return_value = {
        "success": False,
        "error": "Queue not found",
    }

    result = runner.invoke(app, ["enable-realtime", "nonexistent-queue"])

    assert result.exit_code == 1
    assert "Failed to enable realtime" in result.stdout
    assert "Queue not found" in result.stdout


def test_enable_realtime_missing_credentials():
    """Test error when credentials are missing."""
    with patch("aimq.commands.enable_realtime.config") as mock_config:
        mock_config.supabase_url = None
        mock_config.supabase_key = None

        result = runner.invoke(app, ["enable-realtime", "test-queue"])

        assert result.exit_code == 1
        assert "SUPABASE_URL and SUPABASE_KEY" in result.stdout


def test_enable_realtime_migration_not_applied(mock_config, mock_provider):
    """Test error message when migrations haven't been applied."""
    mock_provider.enable_queue_realtime.side_effect = Exception("PGRST202: function not found")

    result = runner.invoke(app, ["enable-realtime", "test-queue"])

    assert result.exit_code == 1
    assert "setup_aimq migration needs to be applied" in result.stdout
    assert "supabase db reset" in result.stdout
