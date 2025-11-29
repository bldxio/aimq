from unittest.mock import patch

import pytest

from aimq.tools.mistral.document_ocr import DocumentOCR, DocumentOCRInput


@pytest.fixture
def ocr_tool():
    return DocumentOCR()


@pytest.fixture
def mock_mistral():
    with patch("aimq.tools.mistral.document_ocr.mistral") as mock:
        yield mock


class TestDocumentOCR:
    def test_init(self, ocr_tool):
        assert ocr_tool.name == "document_ocr"
        assert ocr_tool.description == "Convert a PDF file to markdown"
        assert ocr_tool.args_schema == DocumentOCRInput

    def test_run_success(self, ocr_tool, mock_mistral):
        test_url = "https://example.com/document.pdf"
        expected_response = {
            "text": "Extracted text from PDF",
            "pages": [{"page_number": 1, "content": "Page 1 content"}],
            "metadata": {"total_pages": 1},
        }

        mock_mistral.client.ocr.process.return_value = expected_response

        result = ocr_tool._run(url=test_url)

        assert result == expected_response
        mock_mistral.client.ocr.process.assert_called_once_with(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": test_url},
            include_image_base64=True,
        )

    def test_run_with_different_url(self, ocr_tool, mock_mistral):
        test_url = "https://storage.example.com/files/report.pdf"
        mock_response = {"text": "Report content", "pages": []}

        mock_mistral.client.ocr.process.return_value = mock_response

        result = ocr_tool._run(url=test_url)

        assert result == mock_response
        mock_mistral.client.ocr.process.assert_called_once()
        call_args = mock_mistral.client.ocr.process.call_args
        assert call_args[1]["document"]["document_url"] == test_url

    def test_run_ocr_failure(self, ocr_tool, mock_mistral):
        test_url = "https://example.com/invalid.pdf"
        mock_mistral.client.ocr.process.side_effect = Exception("OCR processing failed")

        with pytest.raises(Exception, match="OCR processing failed"):
            ocr_tool._run(url=test_url)

    def test_run_api_error(self, ocr_tool, mock_mistral):
        test_url = "https://example.com/document.pdf"
        mock_mistral.client.ocr.process.side_effect = RuntimeError("API rate limit exceeded")

        with pytest.raises(RuntimeError, match="API rate limit exceeded"):
            ocr_tool._run(url=test_url)

    def test_input_schema(self):
        input_data = DocumentOCRInput(url="https://example.com/test.pdf")
        assert input_data.url == "https://example.com/test.pdf"

    def test_input_schema_validation(self):
        with pytest.raises(Exception):
            DocumentOCRInput()
