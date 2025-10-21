"""Tests for the Mistral client wrapper."""

from unittest.mock import patch

import pytest

from aimq.clients.mistral import MistralClient, MistralError


class TestMistralClient:
    """Test suite for Mistral client."""

    @patch("aimq.clients.mistral.config")
    def test_client_initialization_success(self, mock_config):
        """Test successful client initialization."""
        # Arrange
        mock_config.mistral_api_key = "test-api-key"

        # Act
        client = MistralClient()
        mistral_instance = client.client

        # Assert
        assert mistral_instance is not None
        assert client._client is mistral_instance

    @patch("aimq.clients.mistral.config")
    def test_client_caching(self, mock_config):
        """Test that client instance is cached."""
        # Arrange
        mock_config.mistral_api_key = "test-api-key"

        # Act
        client = MistralClient()
        first_instance = client.client
        second_instance = client.client

        # Assert
        assert first_instance is second_instance

    @patch("aimq.clients.mistral.config")
    def test_client_no_api_key(self, mock_config):
        """Test error when API key is not configured."""
        # Arrange
        mock_config.mistral_api_key = None

        # Act & Assert
        client = MistralClient()
        with pytest.raises(MistralError, match="Mistral client not configured"):
            _ = client.client

    @patch("aimq.clients.mistral.config")
    def test_client_empty_api_key(self, mock_config):
        """Test error when API key is empty string."""
        # Arrange
        mock_config.mistral_api_key = "   "

        # Act & Assert
        client = MistralClient()
        with pytest.raises(MistralError, match="Mistral client not configured"):
            _ = client.client

    @patch("aimq.clients.mistral.config")
    def test_client_empty_string_api_key(self, mock_config):
        """Test error when API key is empty."""
        # Arrange
        mock_config.mistral_api_key = ""

        # Act & Assert
        client = MistralClient()
        with pytest.raises(MistralError, match="Mistral client not configured"):
            _ = client.client


class TestMistralError:
    """Test suite for MistralError exception."""

    def test_mistral_error_message(self):
        """Test MistralError with custom message."""
        # Arrange & Act
        error = MistralError("Test error message")

        # Assert
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
