"""Tests for the GetUrl Supabase tool."""

from unittest.mock import Mock, patch

import pytest
from langchain_core.runnables import RunnableConfig

from aimq.tools.supabase.get_url import GetUrl


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    with patch("aimq.tools.supabase.get_url.supabase") as mock_sb:
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.create_signed_url.return_value = "https://example.com/signed-url"
        mock_storage.from_.return_value = mock_bucket
        mock_sb.client.storage = mock_storage
        yield mock_sb


class TestGetUrl:
    """Test suite for GetUrl tool."""

    def test_get_url_basic(self, mock_supabase_client):
        """Test basic URL retrieval."""
        # Arrange
        tool = GetUrl()
        path = "documents/test.pdf"
        bucket = "files"

        # Act
        result = tool._run(path=path, bucket=bucket)

        # Assert
        assert result["url"] == "https://example.com/signed-url"
        assert result["metadata"]["path"] == path
        assert result["metadata"]["bucket"] == bucket
        mock_supabase_client.client.storage.from_.assert_called_once_with(bucket)

    def test_get_url_default_bucket(self, mock_supabase_client):
        """Test URL retrieval with default bucket."""
        # Arrange
        tool = GetUrl()
        path = "documents/test.pdf"

        # Act
        result = tool._run(path=path, bucket="files")

        # Assert
        assert result["url"] == "https://example.com/signed-url"
        assert result["metadata"]["path"] == path
        assert result["metadata"]["bucket"] == "files"
        mock_supabase_client.client.storage.from_.assert_called_once_with("files")

    def test_get_url_with_metadata(self, mock_supabase_client):
        """Test URL retrieval with custom metadata."""
        # Arrange
        tool = GetUrl()
        path = "documents/test.pdf"
        bucket = "files"
        metadata = {"user_id": "123", "document_type": "invoice"}

        # Act
        result = tool._run(path=path, bucket=bucket, metadata=metadata)

        # Assert
        assert result["url"] == "https://example.com/signed-url"
        assert result["metadata"]["user_id"] == "123"
        assert result["metadata"]["document_type"] == "invoice"
        assert result["metadata"]["path"] == path
        assert result["metadata"]["bucket"] == bucket

    def test_get_url_with_config(self, mock_supabase_client):
        """Test URL retrieval with runnable config."""
        # Arrange
        tool = GetUrl()
        path = "documents/test.pdf"
        config = RunnableConfig(configurable={"workspace": "main"})

        # Act
        result = tool._run(path=path, config=config)

        # Assert
        assert result["url"] == "https://example.com/signed-url"
        assert result["metadata"]["path"] == path

    def test_get_url_template_formatting(self, mock_supabase_client):
        """Test URL retrieval with template formatting."""
        # Arrange
        tool = GetUrl(bucket="{{workspace}}/{{bucket}}", path="{{user_id}}/{{path}}")
        path = "test.pdf"
        bucket = "files"
        metadata = {"workspace": "prod", "user_id": "user123"}

        # Act
        result = tool._run(path=path, bucket=bucket, metadata=metadata)

        # Assert
        assert result["url"] == "https://example.com/signed-url"
        mock_supabase_client.client.storage.from_.assert_called_once_with("prod/files")

    def test_get_url_no_url_returned(self, mock_supabase_client):
        """Test handling when no URL is returned."""
        # Arrange
        tool = GetUrl()
        path = "documents/test.pdf"
        mock_supabase_client.client.storage.from_().create_signed_url.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="No URL received for"):
            tool._run(path=path)

    def test_get_url_storage_error(self, mock_supabase_client):
        """Test handling of storage errors."""
        # Arrange
        tool = GetUrl()
        path = "documents/test.pdf"
        mock_supabase_client.client.storage.from_().create_signed_url.side_effect = Exception(
            "Storage error"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Error getting URL"):
            tool._run(path=path)

    def test_get_url_tool_properties(self):
        """Test tool properties and schema."""
        # Arrange & Act
        tool = GetUrl()

        # Assert
        assert tool.name == "get_url"
        assert "signed URL" in tool.description
        assert tool.args_schema is not None
