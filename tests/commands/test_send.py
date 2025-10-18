"""Tests for the send command functionality.

This module contains tests for the send command, which is responsible for
sending jobs to different queue providers.
"""

import json
from typing import Generator
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app
from aimq.providers.supabase import SupabaseQueueProvider


class TestSendCommand:
    """Test suite for the send command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner for testing.

        Returns:
            CliRunner: A Typer CLI runner instance for testing command invocations.
        """
        return CliRunner()

    @pytest.fixture
    def mock_supabase_provider(self) -> Generator[Mock, None, None]:
        """Create a mocked SupabaseQueueProvider for testing.

        Yields:
            Mock: A mock instance of SupabaseQueueProvider with predefined behavior.
        """
        with patch("aimq.commands.send.SupabaseQueueProvider") as mock_provider:
            instance = Mock(spec=SupabaseQueueProvider)
            instance.send.return_value = "test-job-id"
            mock_provider.return_value = instance
            yield instance

    def test_send_successful(self, runner: CliRunner, mock_supabase_provider: Mock) -> None:
        """Test successful job sending with valid queue and data.

        Args:
            runner: The CLI runner instance.
            mock_supabase_provider: Mock of the Supabase queue provider.

        Raises:
            AssertionError: If the command fails or provider is not called correctly.
        """
        # Arrange
        queue_name = "test-queue"
        job_data = {"key": "value"}

        # Act
        result = runner.invoke(app, ["send", queue_name, json.dumps(job_data)])

        # Assert
        assert result.exit_code == 0
        mock_supabase_provider.send.assert_called_once_with(queue_name, job_data, delay=None)
        assert "Successfully sent job" in result.stdout

    def test_send_invalid_json(self, runner: CliRunner) -> None:
        """Test sending with invalid JSON data.

        Args:
            runner: The CLI runner instance.

        Raises:
            AssertionError: If the command doesn't handle invalid JSON properly.
        """
        # Arrange
        queue_name = "test-queue"
        invalid_data = "invalid-json"

        # Act
        result = runner.invoke(app, ["send", queue_name, invalid_data])

        # Assert
        assert result.exit_code == 1
        # Error messages are written to stderr, but CliRunner combines them in output
        assert "Invalid JSON data" in result.output

    def test_send_missing_arguments(self, runner: CliRunner) -> None:
        """Test sending without required arguments.

        Args:
            runner: The CLI runner instance.

        Raises:
            AssertionError: If missing arguments are not handled properly.
        """
        # Act
        result = runner.invoke(app, ["send"])

        # Assert
        assert result.exit_code == 2
        # CLI usage errors are written to stderr
        assert "Missing argument" in result.output

    def test_send_with_delay(self, runner: CliRunner, mock_supabase_provider: Mock) -> None:
        """Test sending a job with delay parameter.

        Args:
            runner: The CLI runner instance.
            mock_supabase_provider: Mock of the Supabase queue provider.

        Raises:
            AssertionError: If the command fails or delay is not handled correctly.
        """
        # Arrange
        queue_name = "test-queue"
        job_data = {"key": "value"}
        delay = 60

        # Act
        result = runner.invoke(
            app, ["send", queue_name, json.dumps(job_data), "--delay", str(delay)]
        )

        # Assert
        assert result.exit_code == 0
        mock_supabase_provider.send.assert_called_once_with(queue_name, job_data, delay=delay)
        assert "Successfully sent job" in result.stdout

    def test_send_provider_error(self, runner: CliRunner, mock_supabase_provider: Mock) -> None:
        """Test handling of provider errors.

        Args:
            runner: The CLI runner instance.
            mock_supabase_provider: Mock of the Supabase queue provider.

        Raises:
            AssertionError: If provider errors are not handled properly.
        """
        # Arrange
        queue_name = "test-queue"
        job_data = {"key": "value"}
        mock_supabase_provider.send.side_effect = Exception("Provider error")

        # Act
        result = runner.invoke(app, ["send", queue_name, json.dumps(job_data)])

        # Assert
        assert result.exit_code == 1
        # Error messages are written to stderr, but CliRunner combines them in output
        assert "Error: Provider error" in result.output

    def test_send_complex_json(self, runner: CliRunner, mock_supabase_provider: Mock) -> None:
        """Test sending complex nested JSON data.

        Args:
            runner: The CLI runner instance.
            mock_supabase_provider: Mock of the Supabase queue provider.

        Raises:
            AssertionError: If complex JSON is not handled correctly.
        """
        # Arrange
        queue_name = "test-queue"
        complex_data = {
            "string": "value",
            "number": 42,
            "nested": {"bool": True, "null": None, "list": ["a", "b", "c"]},
        }

        # Act
        result = runner.invoke(app, ["send", queue_name, json.dumps(complex_data)])

        # Assert
        assert result.exit_code == 0
        mock_supabase_provider.send.assert_called_once_with(queue_name, complex_data, delay=None)
        assert "Successfully sent job" in result.stdout
