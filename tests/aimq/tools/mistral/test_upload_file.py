from unittest.mock import patch

import pytest

from aimq.attachment import Attachment
from aimq.tools.mistral.upload_file import UploadFile, UploadFileInput


@pytest.fixture
def upload_tool():
    return UploadFile()


@pytest.fixture
def mock_mistral():
    with patch("aimq.tools.mistral.upload_file.mistral") as mock:
        yield mock


@pytest.fixture
def sample_attachment():
    return Attachment(data=b"test file content")


class TestUploadFile:
    def test_init(self, upload_tool):
        assert upload_tool.name == "upload_file"
        assert upload_tool.description == "Upload a file to Mistral"
        assert upload_tool.args_schema == UploadFileInput

    def test_run_success(self, upload_tool, mock_mistral, sample_attachment):
        expected_file_id = "file_abc123"
        expected_signed_url = "https://storage.mistral.ai/signed/url/abc123"

        mock_mistral.client.files.upload.return_value = {"id": expected_file_id}
        mock_mistral.client.files.get_signed_url.return_value = expected_signed_url

        result = upload_tool._run(file=sample_attachment)

        assert result["file_id"] == expected_file_id
        assert result["signed_url"] == expected_signed_url
        mock_mistral.client.files.upload.assert_called_once_with(sample_attachment.data)
        mock_mistral.client.files.get_signed_url.assert_called_once_with(expected_file_id)

    def test_run_with_different_file(self, upload_tool, mock_mistral):
        different_attachment = Attachment(data=b"different content here")
        file_id = "file_xyz789"
        signed_url = "https://storage.mistral.ai/signed/url/xyz789"

        mock_mistral.client.files.upload.return_value = {"id": file_id}
        mock_mistral.client.files.get_signed_url.return_value = signed_url

        result = upload_tool._run(file=different_attachment)

        assert result["file_id"] == file_id
        assert result["signed_url"] == signed_url
        mock_mistral.client.files.upload.assert_called_once_with(different_attachment.data)

    def test_run_upload_failure(self, upload_tool, mock_mistral, sample_attachment):
        mock_mistral.client.files.upload.side_effect = Exception("Network error")

        with pytest.raises(ValueError, match="Error uploading file to Mistral: Network error"):
            upload_tool._run(file=sample_attachment)

    def test_run_signed_url_failure(self, upload_tool, mock_mistral, sample_attachment):
        mock_mistral.client.files.upload.return_value = {"id": "file_123"}
        mock_mistral.client.files.get_signed_url.side_effect = Exception("Failed to get signed URL")

        with pytest.raises(
            ValueError, match="Error uploading file to Mistral: Failed to get signed URL"
        ):
            upload_tool._run(file=sample_attachment)

    def test_run_api_error(self, upload_tool, mock_mistral, sample_attachment):
        mock_mistral.client.files.upload.side_effect = RuntimeError("API authentication failed")

        with pytest.raises(
            ValueError, match="Error uploading file to Mistral: API authentication failed"
        ):
            upload_tool._run(file=sample_attachment)

    def test_input_schema(self, sample_attachment):
        input_data = UploadFileInput(file=sample_attachment)
        assert input_data.file == sample_attachment

    def test_input_schema_validation(self):
        with pytest.raises(Exception):
            UploadFileInput()
