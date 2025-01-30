# type: ignore  # mypy is configured to ignore test files in pyproject.toml
"""Tests for the Supabase file read tool.

This module contains test cases for the ReadFile tool, which is responsible for
reading files from Supabase Storage. Tests cover initialization, template handling,
file reading with various parameters, and error handling.
"""

from unittest.mock import Mock, patch

import pytest
from langchain.prompts import PromptTemplate

from aimq.attachment import Attachment
from aimq.tools.supabase.read_file import ReadFile, ReadFileInput


@pytest.fixture
def read_file_tool():
    """Create a ReadFile tool instance for testing."""
    return ReadFile()


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing.

    Returns a mock instance that can be used to verify storage interactions.
    """
    with patch("aimq.tools.supabase.read_file.supabase") as mock:
        yield mock


class TestReadFile:
    """Test suite for the ReadFile tool.

    Tests the functionality of the ReadFile tool including initialization,
    template handling, file reading with various parameters, and error handling.
    """

    def test_init(self, read_file_tool):
        """Test initialization of ReadFile tool."""
        assert read_file_tool.name == "read_file"
        assert read_file_tool.description == "Read a file from Supabase Storage"
        assert read_file_tool.args_schema == ReadFileInput

    def test_get_template_string(self, read_file_tool):
        """Test converting string to PromptTemplate."""
        template = read_file_tool._get_template("test/{name}")
        assert isinstance(template, PromptTemplate)
        assert template.template == "test/{name}"

    def test_get_template_prompt_template(self, read_file_tool):
        """Test passing PromptTemplate directly."""
        original = PromptTemplate.from_template("test/{name}")
        template = read_file_tool._get_template(original)
        assert template == original

    def test_run_with_defaults(self, read_file_tool, mock_supabase):
        """Test reading a file with default parameters."""
        file_path = "test/file.txt"
        file_content = b"test content"
        expected_data = {
            "file": Attachment(data=file_content),
            "metadata": {"bucket": "files", "path": file_path},
        }

        mock_storage = Mock()
        mock_storage.download.return_value = file_content
        mock_supabase.client.storage.from_.return_value = mock_storage

        result = read_file_tool._run(path=file_path, bucket="files")

        assert result["metadata"] == expected_data["metadata"]
        assert isinstance(result["file"], Attachment)
        assert result["file"].data == file_content
        mock_supabase.client.storage.from_.assert_called_once_with("files")
        mock_storage.download.assert_called_once_with(file_path)

    def test_run_with_custom_bucket(self, read_file_tool, mock_supabase):
        """Test reading a file with custom bucket."""
        file_path = "test/file.txt"
        bucket = "custom_bucket"
        file_content = b"test content"
        expected_data = {
            "file": Attachment(data=file_content),
            "metadata": {"bucket": bucket, "path": file_path},
        }

        mock_storage = Mock()
        mock_storage.download.return_value = file_content
        mock_supabase.client.storage.from_.return_value = mock_storage

        result = read_file_tool._run(path=file_path, bucket=bucket)

        assert result["metadata"] == expected_data["metadata"]
        assert isinstance(result["file"], Attachment)
        assert result["file"].data == file_content
        mock_supabase.client.storage.from_.assert_called_once_with(bucket)
        mock_storage.download.assert_called_once_with(file_path)

    def test_run_with_metadata(self, read_file_tool, mock_supabase):
        """Test reading a file with metadata."""
        file_path = "test/file.txt"
        metadata = {"type": "text", "size": 100}
        file_content = b"test content"
        expected_data = {
            "file": Attachment(data=file_content),
            "metadata": {"bucket": "files", "path": file_path, **metadata},
        }

        mock_storage = Mock()
        mock_storage.download.return_value = file_content
        mock_supabase.client.storage.from_.return_value = mock_storage

        result = read_file_tool._run(path=file_path, bucket="files", metadata=metadata)

        assert result["metadata"] == expected_data["metadata"]
        assert isinstance(result["file"], Attachment)
        assert result["file"].data == file_content
        mock_supabase.client.storage.from_.assert_called_once_with("files")
        mock_storage.download.assert_called_once_with(file_path)

    def test_file_not_found(self, read_file_tool, mock_supabase):
        """Test behavior when file is not found."""
        file_path = "non-existent/file.txt"

        mock_storage = Mock()
        mock_storage.download.side_effect = Exception("File not found")
        mock_supabase.client.storage.from_.return_value = mock_storage

        with pytest.raises(
            ValueError, match="Error reading file from Supabase: File not found"
        ):
            read_file_tool._run(path=file_path)
