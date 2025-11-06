"""Tests for DocumentWorkflow."""

from unittest.mock import MagicMock, patch

import pytest  # noqa: F401

from aimq.workflows.document import DocumentState, DocumentWorkflow  # noqa: F401


class MockStorageTool:
    """Mock storage tool for testing."""

    def invoke(self, input):
        path = input.get("path", "")
        if "error" in path:
            raise Exception("Storage error")
        return b"test file content"


class MockOCRTool:
    """Mock OCR tool for testing."""

    def invoke(self, input):
        return {"text": "Extracted text from image", "confidence": 0.95}


class MockPDFTool:
    """Mock PDF tool for testing."""

    def invoke(self, input):
        return [
            {"text": "Page 1 content", "page_number": 1},
            {"text": "Page 2 content", "page_number": 2},
        ]


def test_document_workflow_initialization():
    """Test DocumentWorkflow can be initialized."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    assert workflow is not None
    assert workflow.storage_tool is not None
    assert workflow.ocr_tool is not None


def test_document_workflow_with_pdf_tool():
    """Test DocumentWorkflow with PDF tool."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
        pdf_tool=MockPDFTool(),
    )

    assert workflow.pdf_tool is not None


def test_document_workflow_graph_compilation():
    """Test workflow compiles graph successfully."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    assert workflow._compiled is not None
    assert workflow._graph is not None


def test_document_workflow_has_required_nodes():
    """Test graph has required nodes."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    nodes = workflow._graph.nodes
    assert "fetch" in nodes
    assert "detect" in nodes
    assert "process_image" in nodes
    assert "process_pdf" in nodes
    assert "store" in nodes


def test_route_by_type_image():
    """Test routing for image documents."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {"document_type": "image", "document_path": "", "metadata": {}, "status": ""}
    route = workflow._route_by_type(state)

    assert route == "process_image"


def test_route_by_type_pdf():
    """Test routing for PDF documents."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {"document_type": "pdf", "document_path": "", "metadata": {}, "status": ""}
    route = workflow._route_by_type(state)

    assert route == "process_pdf"


def test_route_by_type_unknown():
    """Test routing for unknown document types."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {
        "document_type": "unknown",
        "document_path": "",
        "metadata": {},
        "status": "",
    }
    route = workflow._route_by_type(state)

    assert route == "error"


def test_fetch_node_success():
    """Test fetch node successfully retrieves document."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {"document_path": "test.pdf", "metadata": {}, "status": "pending"}

    result = workflow._fetch_node(state)

    assert result["status"] == "fetched"
    assert "raw_content" in result
    assert result["raw_content"] == b"test file content"


def test_fetch_node_error():
    """Test fetch node handles errors."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {"document_path": "error.pdf", "metadata": {}, "status": "pending"}

    result = workflow._fetch_node(state)

    assert result["status"] == "error"
    assert "error" in result["metadata"]


def test_detect_type_node_image():
    """Test type detection for images."""
    mock_magic = MagicMock()
    mock_magic.from_buffer = MagicMock(return_value="image/png")

    with patch.dict("sys.modules", {"magic": mock_magic}):
        workflow = DocumentWorkflow(
            storage_tool=MockStorageTool(),
            ocr_tool=MockOCRTool(),
        )

        state = {
            "raw_content": b"fake image data",
            "metadata": {},
            "status": "fetched",
            "document_path": "",
        }

        result = workflow._detect_type_node(state)

        assert result["document_type"] == "image"
        assert result["status"] == "typed"
        assert result["metadata"]["mime_type"] == "image/png"


def test_detect_type_node_pdf():
    """Test type detection for PDFs."""
    mock_magic = MagicMock()
    mock_magic.from_buffer = MagicMock(return_value="application/pdf")

    with patch.dict("sys.modules", {"magic": mock_magic}):
        workflow = DocumentWorkflow(
            storage_tool=MockStorageTool(),
            ocr_tool=MockOCRTool(),
        )

        state = {
            "raw_content": b"fake pdf data",
            "metadata": {},
            "status": "fetched",
            "document_path": "",
        }

        result = workflow._detect_type_node(state)

        assert result["document_type"] == "pdf"
        assert result["metadata"]["mime_type"] == "application/pdf"


def test_detect_type_node_unknown():
    """Test type detection for unknown types."""
    mock_magic = MagicMock()
    mock_magic.from_buffer = MagicMock(return_value="text/plain")

    with patch.dict("sys.modules", {"magic": mock_magic}):
        workflow = DocumentWorkflow(
            storage_tool=MockStorageTool(),
            ocr_tool=MockOCRTool(),
        )

        state = {
            "raw_content": b"fake data",
            "metadata": {},
            "status": "fetched",
            "document_path": "",
        }

        result = workflow._detect_type_node(state)

        assert result["document_type"] == "unknown"


@patch("aimq.attachment.Attachment")
def test_process_image_node_success(mock_attachment_class):
    """Test image processing node."""
    mock_attachment = MagicMock()
    mock_attachment_class.return_value = mock_attachment

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {
        "raw_content": b"image data",
        "metadata": {},
        "status": "typed",
        "document_path": "",
    }

    result = workflow._process_image_node(state)

    assert result["status"] == "processed"
    assert "text" in result
    assert result["text"] == "Extracted text from image"
    assert result["metadata"]["ocr_confidence"] == 0.95


@patch("aimq.attachment.Attachment")
def test_process_image_node_error(mock_attachment_class):
    """Test image processing node handles errors."""
    mock_attachment = MagicMock()
    mock_attachment_class.return_value = mock_attachment

    # Make OCR tool raise error
    class ErrorOCRTool:
        def invoke(self, input):
            raise Exception("OCR failed")

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=ErrorOCRTool(),
    )

    state = {
        "raw_content": b"image data",
        "metadata": {},
        "status": "typed",
        "document_path": "",
    }

    result = workflow._process_image_node(state)

    assert result["status"] == "error"
    assert "error" in result["metadata"]


def test_process_pdf_node_success():
    """Test PDF processing node."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
        pdf_tool=MockPDFTool(),
    )

    state = {
        "raw_content": b"pdf data",
        "metadata": {},
        "status": "typed",
        "document_path": "",
    }

    result = workflow._process_pdf_node(state)

    assert result["status"] == "processed"
    assert "text" in result
    assert "Page 1 content" in result["text"]
    assert "Page 2 content" in result["text"]
    assert result["metadata"]["page_count"] == 2


def test_process_pdf_node_no_tool():
    """Test PDF processing without PDF tool configured."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
        pdf_tool=None,
    )

    state = {
        "raw_content": b"pdf data",
        "metadata": {},
        "status": "typed",
        "document_path": "",
    }

    result = workflow._process_pdf_node(state)

    assert result["status"] == "error"
    assert "No PDF tool configured" in result.get("text", "")


def test_process_pdf_node_error():
    """Test PDF processing handles errors."""

    class ErrorPDFTool:
        def invoke(self, input):
            raise Exception("PDF processing failed")

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
        pdf_tool=ErrorPDFTool(),
    )

    state = {
        "raw_content": b"pdf data",
        "metadata": {},
        "status": "typed",
        "document_path": "",
    }

    result = workflow._process_pdf_node(state)

    assert result["status"] == "error"


@patch("aimq.tools.supabase.WriteRecord")
def test_store_node_success(mock_write_class):
    """Test store node saves results."""
    mock_write = MagicMock()
    mock_write_class.return_value = mock_write

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {
        "document_path": "test.png",
        "text": "Extracted text",
        "metadata": {"ocr_confidence": 0.95},
        "status": "processed",
    }

    result = workflow._store_node(state)

    assert result["status"] == "stored"
    mock_write.invoke.assert_called_once()


@patch("aimq.tools.supabase.WriteRecord")
def test_store_node_error(mock_write_class):
    """Test store node handles errors."""
    mock_write = MagicMock()
    mock_write.invoke.side_effect = Exception("Storage failed")
    mock_write_class.return_value = mock_write

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {
        "document_path": "test.png",
        "text": "Extracted text",
        "metadata": {},
        "status": "processed",
    }

    result = workflow._store_node(state)

    assert result["status"] == "error"
    assert "error" in result["metadata"]


def test_document_workflow_with_checkpointer():
    """Test DocumentWorkflow with checkpointer enabled."""
    with patch("aimq.workflows.base.get_checkpointer"):
        workflow = DocumentWorkflow(
            storage_tool=MockStorageTool(),
            ocr_tool=MockOCRTool(),
            checkpointer=True,
        )

        assert workflow._compiled is not None
