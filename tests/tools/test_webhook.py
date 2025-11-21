"""Tests for webhook tool."""

import os
from unittest.mock import Mock, patch

import httpx

from aimq.tools.webhook import WebhookConfig, WebhookTool


class TestWebhookConfig:
    """Tests for WebhookConfig."""

    def test_basic_config(self):
        """Test basic webhook configuration."""
        config = WebhookConfig(
            name="test_tool",
            description="Test tool description",
            url="https://example.com/webhook",
        )

        assert config.name == "test_tool"
        assert config.description == "Test tool description"
        assert config.url == "https://example.com/webhook"
        assert config.method == "POST"
        assert config.timeout == 10

    def test_substitute_secrets(self):
        """Test environment variable substitution."""
        os.environ["TEST_API_KEY"] = "secret123"
        os.environ["TEST_TOKEN"] = "token456"

        config = WebhookConfig(
            name="test_tool",
            description="Test",
            url="https://example.com/webhook",
            headers={
                "Authorization": "Bearer ${TEST_API_KEY}",
                "X-Token": "${TEST_TOKEN}",
            },
        )

        substituted = config.substitute_secrets()

        assert substituted.headers["Authorization"] == "Bearer secret123"
        assert substituted.headers["X-Token"] == "token456"

        del os.environ["TEST_API_KEY"]
        del os.environ["TEST_TOKEN"]

    def test_substitute_missing_env_var(self):
        """Test substitution with missing environment variable."""
        config = WebhookConfig(
            name="test_tool",
            description="Test",
            url="https://example.com/webhook",
            headers={"Authorization": "Bearer ${MISSING_VAR}"},
        )

        substituted = config.substitute_secrets()
        assert substituted.headers["Authorization"] == "Bearer "


class TestWebhookTool:
    """Tests for WebhookTool."""

    def test_create_tool(self):
        """Test creating a webhook tool."""
        config = WebhookConfig(
            name="weather",
            description="Get weather",
            url="https://example.com/weather",
            args={
                "location": {"type": "string", "description": "City name"},
            },
        )

        tool = WebhookTool(config=config)

        assert tool.name == "weather"
        assert tool.description == "Get weather"
        assert tool.args_schema is not None

    def test_create_args_schema(self):
        """Test creating Pydantic schema from args."""
        config = WebhookConfig(
            name="test_tool",
            description="Test",
            url="https://example.com/webhook",
            args={
                "text": {"type": "string", "description": "Text input"},
                "count": {"type": "integer", "description": "Count value"},
                "enabled": {"type": "boolean", "description": "Enable flag"},
            },
        )

        tool = WebhookTool(config=config)
        schema = tool.args_schema

        assert schema is not None
        instance = schema(text="hello", count=5, enabled=True)
        assert instance.text == "hello"
        assert instance.count == 5
        assert instance.enabled is True

    @patch("httpx.Client")
    def test_successful_request(self, mock_client_class):
        """Test successful webhook request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success", "data": "test"}
        mock_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        config = WebhookConfig(
            name="test_tool",
            description="Test",
            url="https://example.com/webhook",
            args={"input": {"type": "string", "description": "Input"}},
        )

        tool = WebhookTool(config=config)
        result = tool.run(input="test")

        assert "success" in result
        mock_client.request.assert_called_once()

    @patch("httpx.Client")
    def test_http_error(self, mock_client_class):
        """Test handling HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        def raise_status():
            raise httpx.HTTPStatusError("404 Not Found", request=Mock(), response=mock_response)

        mock_response.raise_for_status = raise_status

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        config = WebhookConfig(
            name="test_tool",
            description="Test",
            url="https://example.com/webhook",
            args={"input": {"type": "string", "description": "Input"}},
        )

        tool = WebhookTool(config=config)
        result = tool.run(input="test")

        assert "Error calling webhook" in result
        assert "404" in result

    @patch("httpx.Client")
    def test_timeout_error(self, mock_client_class):
        """Test handling timeout errors."""
        mock_client = Mock()
        mock_client.request.side_effect = httpx.TimeoutException("Timeout")
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        config = WebhookConfig(
            name="test_tool",
            description="Test",
            url="https://example.com/webhook",
            timeout=5,
            args={"input": {"type": "string", "description": "Input"}},
        )

        tool = WebhookTool(config=config)
        result = tool.run(input="test")

        assert "Error calling webhook" in result
        assert "timed out" in result

    @patch("httpx.Client")
    def test_response_template(self, mock_client_class):
        """Test response template formatting."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"temperature": "72°F", "condition": "Sunny"}
        mock_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        config = WebhookConfig(
            name="weather",
            description="Get weather",
            url="https://example.com/weather",
            args={"location": {"type": "string", "description": "City"}},
            response_template="Weather for {location}:\n{response}",
        )

        tool = WebhookTool(config=config)
        result = tool.run(location="San Francisco")

        assert "Weather for San Francisco" in result
        assert "72°F" in result
        assert "Sunny" in result
