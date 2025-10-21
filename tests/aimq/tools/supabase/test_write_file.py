from unittest.mock import Mock, patch

import pytest
from langchain.prompts import PromptTemplate

from aimq.attachment import Attachment
from aimq.tools.supabase.write_file import WriteFile, WriteFileInput


@pytest.fixture
def write_file_tool():
    return WriteFile()


@pytest.fixture
def mock_supabase():
    with patch("aimq.tools.supabase.write_file.supabase") as mock:
        yield mock


class TestWriteFile:
    def test_init(self, write_file_tool):
        """Test initialization of WriteFile tool."""
        assert write_file_tool.name == "write_file"
        assert write_file_tool.description == "Write a file to Supabase Storage"
        assert write_file_tool.args_schema == WriteFileInput

    def test_get_template_string(self, write_file_tool):
        """Test converting string to PromptTemplate."""
        template = write_file_tool._get_template("test/{name}")
        assert isinstance(template, PromptTemplate)
        assert template.template == "test/{name}"

    def test_get_template_prompt_template(self, write_file_tool):
        """Test passing PromptTemplate directly."""
        original = PromptTemplate.from_template("test/{name}")
        template = write_file_tool._get_template(original)
        assert template == original

    def test_run_with_defaults(self, write_file_tool, mock_supabase):
        """Test writing a file with default parameters."""
        file_path = "test/file.txt"
        file_content = b"test content"
        expected_data = {"path": file_path, "bucket": "files"}

        mock_storage = Mock()
        mock_storage.upload.return_value = {"path": file_path}
        mock_supabase.client.storage.from_.return_value = mock_storage

        result = write_file_tool._run(
            path=file_path, bucket="files", file=Attachment(data=file_content)
        )

        assert result["path"] == expected_data["path"]
        assert result["bucket"] == expected_data["bucket"]
        mock_supabase.client.storage.from_.assert_called_once_with("files")
        mock_storage.upload.assert_called_once_with(
            path=file_path,
            file=file_content,
            file_options={"upsert": "true", "content-type": "application/octet-stream"},
        )

    def test_run_with_custom_bucket(self, write_file_tool, mock_supabase):
        """Test writing a file with custom bucket."""
        file_path = "test/file.txt"
        bucket = "custom_bucket"
        file_content = b"test content"
        expected_data = {"path": file_path, "bucket": bucket}

        mock_storage = Mock()
        mock_storage.upload.return_value = {"path": file_path}
        mock_supabase.client.storage.from_.return_value = mock_storage

        result = write_file_tool._run(
            path=file_path, bucket=bucket, file=Attachment(data=file_content)
        )

        assert result["path"] == expected_data["path"]
        assert result["bucket"] == expected_data["bucket"]
        mock_supabase.client.storage.from_.assert_called_once_with(bucket)
        mock_storage.upload.assert_called_once_with(
            path=file_path,
            file=file_content,
            file_options={"upsert": "true", "content-type": "application/octet-stream"},
        )

    def test_run_with_metadata(self, write_file_tool, mock_supabase):
        """Test writing a file with metadata."""
        file_path = "test/file.txt"
        metadata = {"type": "text", "size": 100}
        file_content = b"test content"
        expected_data = {"path": file_path, "bucket": "files", "metadata": metadata}

        mock_storage = Mock()
        mock_storage.upload.return_value = {"path": file_path}
        mock_supabase.client.storage.from_.return_value = mock_storage

        result = write_file_tool._run(
            path=file_path, bucket="files", file=Attachment(data=file_content), metadata=metadata
        )

        assert result["path"] == expected_data["path"]
        assert result["bucket"] == expected_data["bucket"]
        assert result["metadata"] == expected_data["metadata"]
        mock_supabase.client.storage.from_.assert_called_once_with("files")
        mock_storage.upload.assert_called_once_with(
            path=file_path,
            file=file_content,
            file_options={"upsert": "true", "content-type": "application/octet-stream"},
        )

    def test_upload_failure(self, write_file_tool, mock_supabase):
        """Test behavior when upload fails."""
        file_path = "test/file.txt"
        file_content = b"test content"

        mock_storage = Mock()
        mock_storage.upload.side_effect = Exception("Upload failed")
        mock_supabase.client.storage.from_.return_value = mock_storage

        with pytest.raises(ValueError, match="Error writing file to Supabase: Upload failed"):
            write_file_tool._run(path=file_path, bucket="files", file=Attachment(data=file_content))
