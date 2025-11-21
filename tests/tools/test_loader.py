"""Tests for tool loader."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from aimq.tools.loader import ToolLoader
from aimq.tools.webhook import WebhookTool


class TestToolLoader:
    """Tests for ToolLoader."""

    def test_load_from_dict_webhook(self):
        """Test loading webhook tools from dict."""
        config = {
            "tools": [
                {
                    "type": "webhook",
                    "name": "weather",
                    "description": "Get weather",
                    "url": "https://example.com/weather",
                    "args": {"location": {"type": "string", "description": "City name"}},
                }
            ]
        }

        loader = ToolLoader()
        tools = loader.load_from_dict(config)

        assert len(tools) == 1
        assert isinstance(tools[0], WebhookTool)
        assert tools[0].name == "weather"

    def test_load_from_dict_multiple_tools(self):
        """Test loading multiple tools."""
        config = {
            "tools": [
                {
                    "type": "webhook",
                    "name": "weather",
                    "description": "Get weather",
                    "url": "https://example.com/weather",
                },
                {
                    "type": "webhook",
                    "name": "email",
                    "description": "Send email",
                    "url": "https://example.com/email",
                },
            ]
        }

        loader = ToolLoader()
        tools = loader.load_from_dict(config)

        assert len(tools) == 2
        assert tools[0].name == "weather"
        assert tools[1].name == "email"

    def test_load_from_dict_empty(self):
        """Test loading empty config."""
        config = {"tools": []}

        loader = ToolLoader()
        tools = loader.load_from_dict(config)

        assert len(tools) == 0

    def test_load_from_dict_invalid_tool(self):
        """Test loading with invalid tool config."""
        config = {
            "tools": [
                {
                    "type": "webhook",
                    "name": "valid",
                    "description": "Valid tool",
                    "url": "https://example.com/valid",
                },
                {
                    "type": "webhook",
                    "name": "invalid",
                    # Missing required fields
                },
            ]
        }

        loader = ToolLoader()
        tools = loader.load_from_dict(config)

        # Should load valid tool and skip invalid
        assert len(tools) == 1
        assert tools[0].name == "valid"

    def test_load_from_dict_unknown_type(self):
        """Test loading tool with unknown type."""
        config = {
            "tools": [
                {
                    "type": "unknown_type",
                    "name": "test",
                    "description": "Test",
                }
            ]
        }

        loader = ToolLoader()
        tools = loader.load_from_dict(config)

        # Should skip unknown type
        assert len(tools) == 0

    def test_load_from_file(self):
        """Test loading tools from JSON file."""
        config = {
            "tools": [
                {
                    "type": "webhook",
                    "name": "weather",
                    "description": "Get weather",
                    "url": "https://example.com/weather",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            loader = ToolLoader()
            tools = loader.load_from_file(temp_path)

            assert len(tools) == 1
            assert tools[0].name == "weather"
        finally:
            Path(temp_path).unlink()

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file."""
        loader = ToolLoader()
        tools = loader.load_from_file("nonexistent.json")

        # Should return empty list
        assert len(tools) == 0

    def test_load_from_file_invalid_json(self):
        """Test loading from file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            loader = ToolLoader()
            with pytest.raises(ValueError, match="Invalid tools configuration"):
                loader.load_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_from_env(self):
        """Test loading tools from environment variable."""
        config = {
            "tools": [
                {
                    "type": "webhook",
                    "name": "weather",
                    "description": "Get weather",
                    "url": "https://example.com/weather",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            with patch.dict("os.environ", {"TOOLS_CONFIG_PATH": temp_path}):
                tools = ToolLoader.load_from_env()

                assert len(tools) == 1
                assert tools[0].name == "weather"
        finally:
            Path(temp_path).unlink()

    def test_load_from_env_default_path(self):
        """Test loading from default path when env var not set."""
        # Should try to load from "tools.json" (which doesn't exist in tests)
        tools = ToolLoader.load_from_env()

        # Should return empty list when file not found
        assert len(tools) == 0

    def test_create_tool_webhook(self):
        """Test creating webhook tool from config."""
        config = {
            "type": "webhook",
            "name": "test",
            "description": "Test tool",
            "url": "https://example.com/test",
        }

        loader = ToolLoader()
        tool = loader._create_tool(config)

        assert isinstance(tool, WebhookTool)
        assert tool.name == "test"

    def test_create_tool_unknown_type(self):
        """Test creating tool with unknown type."""
        config = {
            "type": "unknown",
            "name": "test",
        }

        loader = ToolLoader()
        with pytest.raises(ValueError, match="Unknown tool type"):
            loader._create_tool(config)
