"""Test the main entry point."""

import sys
from unittest.mock import patch

from typer.testing import CliRunner

from aimq.commands import app


def test_main():
    """Test that the main entry point calls the app function."""
    runner = CliRunner()
    with patch.object(
        sys, "argv", ["aimq", "--help"]
    ):  # Mock argv to avoid parsing test args
        result = runner.invoke(app)
        assert result.exit_code == 0  # Help command should succeed
        assert "Usage:" in result.stdout  # Help output should be shown
