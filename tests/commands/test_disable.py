"""Tests for the disable command functionality."""

from typing import Generator
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from aimq.commands import app


class TestDisableCommand:
    """Test suite for the disable command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture to provide a CLI runner for testing.

        Returns:
            CliRunner: A Typer CLI runner instance.
        """
        return CliRunner()

    @pytest.fixture
    def mock_supabase_config(self) -> Generator[Mock, None, None]:
        """Fixture to provide a mocked SupabaseConfig.

        Returns:
            Generator[Mock, None, None]: A mock instance of SupabaseConfig.
        """
        with patch("aimq.commands.disable.SupabaseConfig") as mock_config:
            instance = Mock()
            mock_config.return_value = instance
            yield instance

    def test_disable_successful(self, runner: CliRunner, mock_supabase_config: Mock) -> None:
        """Test successful PGMQ disabling.

        Tests that PGMQ can be successfully disabled in Supabase config.

        Args:
            runner: The CLI runner instance.
            mock_supabase_config: Mock of the SupabaseConfig.
        """
        result = runner.invoke(app, ["disable"])
        assert result.exit_code == 0
        assert "Successfully disabled PGMQ in Supabase config" in result.stdout
        mock_supabase_config.disable.assert_called_once()

    def test_disable_failure(self, runner: CliRunner, mock_supabase_config: Mock) -> None:
        """Test PGMQ disable failure handling.

        Tests that errors during PGMQ disabling are handled appropriately.

        Args:
            runner: The CLI runner instance.
            mock_supabase_config: Mock of the SupabaseConfig.
        """
        mock_supabase_config.disable.side_effect = Exception("Test error")
        result = runner.invoke(app, ["disable"])
        assert result.exit_code == 1
        assert "Failed to disable PGMQ: Test error" in result.stdout
        mock_supabase_config.disable.assert_called_once()
