import sys
from unittest.mock import Mock, patch

import pytest

from aimq.tools.docling.converter import DoclingConverter, DoclingConverterInput


@pytest.fixture
def converter_tool():
    return DoclingConverter()


@pytest.fixture
def sample_file(tmp_path):
    file_path = tmp_path / "test_document.pdf"
    file_path.write_bytes(b"fake pdf content")
    return str(file_path)


class TestDoclingConverter:
    def test_init(self, converter_tool):
        assert converter_tool.name == "docling_convert"
        assert "Convert documents" in converter_tool.description
        assert converter_tool.args_schema == DoclingConverterInput

    def test_run_markdown_format(self, converter_tool, sample_file):
        mock_result = Mock()
        mock_document = Mock()
        mock_document.export_to_markdown.return_value = "# Test Document\n\nContent here"
        mock_document.metadata = {"pages": 1, "title": "Test"}
        mock_result.document = mock_document

        mock_converter = Mock()
        mock_converter.convert.return_value = mock_result
        mock_converter_class = Mock(return_value=mock_converter)

        mock_docling_module = Mock()
        mock_docling_module.DocumentConverter = mock_converter_class

        with patch.dict(sys.modules, {"docling.document_converter": mock_docling_module}):
            result = converter_tool._run(file_path=sample_file, export_format="markdown")

            assert result["content"] == "# Test Document\n\nContent here"
            assert result["format"] == "markdown"
            assert result["metadata"] == {"pages": 1, "title": "Test"}
            mock_converter.convert.assert_called_once_with(sample_file)
            mock_document.export_to_markdown.assert_called_once()

    def test_run_html_format(self, converter_tool, sample_file):
        mock_result = Mock()
        mock_document = Mock()
        mock_document.export_to_html.return_value = "<html><body>Test</body></html>"
        mock_document.metadata = {"pages": 1}
        mock_result.document = mock_document

        mock_converter = Mock()
        mock_converter.convert.return_value = mock_result
        mock_converter_class = Mock(return_value=mock_converter)

        mock_docling_module = Mock()
        mock_docling_module.DocumentConverter = mock_converter_class

        with patch.dict(sys.modules, {"docling.document_converter": mock_docling_module}):
            result = converter_tool._run(file_path=sample_file, export_format="html")

            assert result["content"] == "<html><body>Test</body></html>"
            assert result["format"] == "html"
            mock_document.export_to_html.assert_called_once()

    def test_run_json_format(self, converter_tool, sample_file):
        mock_result = Mock()
        mock_document = Mock()
        mock_document.export_to_dict.return_value = {"text": "content", "pages": 1}
        mock_document.metadata = {"pages": 1}
        mock_result.document = mock_document

        mock_converter = Mock()
        mock_converter.convert.return_value = mock_result
        mock_converter_class = Mock(return_value=mock_converter)

        mock_docling_module = Mock()
        mock_docling_module.DocumentConverter = mock_converter_class

        with patch.dict(sys.modules, {"docling.document_converter": mock_docling_module}):
            result = converter_tool._run(file_path=sample_file, export_format="json")

            assert result["content"] == {"text": "content", "pages": 1}
            assert result["format"] == "json"
            mock_document.export_to_dict.assert_called_once()

    def test_run_file_not_found(self, converter_tool):
        mock_docling_module = Mock()
        with patch.dict(sys.modules, {"docling.document_converter": mock_docling_module}):
            with pytest.raises(FileNotFoundError, match="File not found"):
                converter_tool._run(file_path="/nonexistent/file.pdf", export_format="markdown")

    def test_run_import_error(self, converter_tool, sample_file):
        with patch.dict(sys.modules, {"docling.document_converter": None}):
            with pytest.raises(ImportError, match="docling is required"):
                converter_tool._run(file_path=sample_file, export_format="markdown")

    @pytest.mark.asyncio
    async def test_arun_calls_sync_version(self, converter_tool, sample_file):
        mock_result = Mock()
        mock_document = Mock()
        mock_document.export_to_markdown.return_value = "# Async Test"
        mock_document.metadata = {}
        mock_result.document = mock_document

        mock_converter = Mock()
        mock_converter.convert.return_value = mock_result
        mock_converter_class = Mock(return_value=mock_converter)

        mock_docling_module = Mock()
        mock_docling_module.DocumentConverter = mock_converter_class

        with patch.dict(sys.modules, {"docling.document_converter": mock_docling_module}):
            result = await converter_tool._arun(file_path=sample_file, export_format="markdown")

            assert result["content"] == "# Async Test"
            assert result["format"] == "markdown"

    def test_input_schema(self):
        input_data = DoclingConverterInput(file_path="/path/to/file.pdf", export_format="markdown")
        assert input_data.file_path == "/path/to/file.pdf"
        assert input_data.export_format == "markdown"

    def test_input_schema_default_format(self):
        input_data = DoclingConverterInput(file_path="/path/to/file.pdf")
        assert input_data.export_format == "markdown"
