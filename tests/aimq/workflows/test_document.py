"""Tests for DocumentWorkflow."""

from unittest.mock import MagicMock, patch

import pytest  # noqa: F401

from aimq.worker import Worker
from aimq.workflows.document import DocumentState, DocumentWorkflow  # noqa: F401


class MockStorageTool:
    """Mock storage tool for testing."""

    def invoke(self, input):
        from aimq.attachment import Attachment

        path = input.get("path", "")
        if "error" in path:
            raise Exception("Storage error")
        # Match ReadFile's return format: {"file": Attachment(...), "metadata": ...}
        return {"file": Attachment(data=b"test file content"), "metadata": {}}


class MockOCRTool:
    """Mock OCR tool for testing."""

    def invoke(self, input):
        return {"text": "Extracted text from image", "confidence": 0.95}


class MockPDFTool:
    """Mock PDF tool for testing (matches PageSplitter output format)."""

    def invoke(self, input):
        from aimq.attachment import Attachment

        # PageSplitter returns list of dicts with "file" (Attachment) and "metadata"
        return [
            {
                "file": Attachment(data=b"page 1 image data"),
                "metadata": {"position": 0, "width": 800, "height": 600},
            },
            {
                "file": Attachment(data=b"page 2 image data"),
                "metadata": {"position": 1, "width": 800, "height": 600},
            },
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
    """Test routing for unknown document types raises ValueError."""
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

    with pytest.raises(ValueError, match="Unknown or unsupported document type: unknown"):
        workflow._route_by_type(state)


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
    """Test fetch node raises exception on storage error."""
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    state = {"document_path": "error.pdf", "metadata": {}, "status": "pending"}

    with pytest.raises(Exception, match="Storage error"):
        workflow._fetch_node(state)


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
    """Test image processing node raises exception on OCR error."""
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

    with pytest.raises(Exception, match="OCR failed"):
        workflow._process_image_node(state)


@patch("aimq.attachment.Attachment")
def test_process_pdf_node_success(mock_attachment_class):
    """Test PDF processing splits pages and runs OCR on each."""
    # Create mock attachments for PDF and pages
    mock_pdf_attachment = MagicMock()
    mock_page1_attachment = MagicMock()
    mock_page2_attachment = MagicMock()

    # Mock Attachment constructor to return different instances
    mock_attachment_class.side_effect = [mock_pdf_attachment]

    # Create a mock PDF tool that returns page attachments
    mock_pdf_tool = MagicMock()
    mock_pdf_tool.invoke.return_value = [
        {"file": mock_page1_attachment, "metadata": {"position": 0}},
        {"file": mock_page2_attachment, "metadata": {"position": 1}},
    ]

    # Create a mock OCR tool that tracks calls
    mock_ocr_tool = MagicMock()
    mock_ocr_tool.invoke.side_effect = [
        {"text": "Page 1 OCR text", "confidence": 0.95},
        {"text": "Page 2 OCR text", "confidence": 0.93},
    ]

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=mock_ocr_tool,
        pdf_tool=mock_pdf_tool,
    )

    state = {
        "raw_content": b"pdf data",
        "metadata": {},
        "status": "typed",
        "document_path": "",
    }

    result = workflow._process_pdf_node(state)

    # Verify Attachment was created with raw_content using data= keyword
    mock_attachment_class.assert_called_once_with(data=b"pdf data")

    # Verify PDF tool was called with {"file": attachment}
    mock_pdf_tool.invoke.assert_called_once_with({"file": mock_pdf_attachment})

    # Verify OCR was called twice, once for each page
    assert mock_ocr_tool.invoke.call_count == 2
    mock_ocr_tool.invoke.assert_any_call({"image": mock_page1_attachment})
    mock_ocr_tool.invoke.assert_any_call({"image": mock_page2_attachment})

    # Verify result contains combined OCR text
    assert result["status"] == "processed"
    assert "text" in result
    assert "Page 1 OCR text" in result["text"]
    assert "Page 2 OCR text" in result["text"]
    assert result["metadata"]["page_count"] == 2


def test_process_pdf_node_no_tool():
    """Test PDF processing raises ValueError when PDF tool not configured."""
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

    with pytest.raises(ValueError, match="PDF tool not configured"):
        workflow._process_pdf_node(state)


@patch("aimq.attachment.Attachment")
def test_process_pdf_node_error(mock_attachment_class):
    """Test PDF processing raises exception on PDF tool error."""
    mock_attachment = MagicMock()
    mock_attachment_class.return_value = mock_attachment

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

    with pytest.raises(Exception, match="PDF processing failed"):
        workflow._process_pdf_node(state)


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
    """Test store node raises exception on storage error."""
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

    with pytest.raises(Exception, match="Storage failed"):
        workflow._store_node(state)


def test_document_workflow_with_checkpointer():
    """Test DocumentWorkflow with checkpointer enabled."""
    with patch("aimq.workflows.base.get_checkpointer"):
        workflow = DocumentWorkflow(
            storage_tool=MockStorageTool(),
            ocr_tool=MockOCRTool(),
            checkpointer=True,
        )

        assert workflow._compiled is not None


@patch("aimq.worker.Queue")
def test_worker_assign_with_document_workflow(mock_queue_class):
    """Test that worker.assign() accepts DocumentWorkflow instances.

    This is an integration test to verify that the Queue validator
    accepts wrapper classes that delegate to Runnables (duck typing).
    """
    # Create a workflow instance
    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    # Set the workflow name for queue naming
    workflow._compiled.name = "doc-pipeline"

    # Create a worker
    worker = Worker()

    # This should NOT raise a validation error
    worker.assign(workflow, queue="doc-pipeline", timeout=900)

    # Verify Queue was called with the workflow
    mock_queue_class.assert_called_once()
    call_kwargs = mock_queue_class.call_args[1]
    assert call_kwargs["runnable"] == workflow
    assert call_kwargs["timeout"] == 900


def test_document_workflow_with_thread_id():
    """Test DocumentWorkflow invocation with thread_id in job data.

    The thread_id should be extracted by the Queue and placed in config,
    not passed as part of the workflow input state.
    """
    from datetime import datetime

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    # Job data with thread_id
    job_data = {
        "document_path": "test.pdf",
        "metadata": {"source": "email"},
        "status": "pending",
        "thread_id": "test-session-123",
    }

    # Mock the invoke to check what inputs it receives
    original_invoke = workflow._compiled.invoke

    def mock_invoke(input_data, config=None):
        # Verify thread_id is NOT in input_data
        assert "thread_id" not in input_data
        # Verify thread_id IS in config["configurable"]
        assert config is not None
        assert "configurable" in config
        assert config["configurable"]["thread_id"] == "test-session-123"
        # Verify other fields are present in input
        assert input_data["document_path"] == "test.pdf"
        assert input_data["status"] == "pending"
        # Return a minimal valid response
        return {"status": "stored", "document_path": "test.pdf", "metadata": {}}

    workflow._compiled.invoke = mock_invoke

    # Create Queue and run job
    from aimq.job import Job
    from aimq.queue import Queue

    queue = Queue(runnable=workflow, timeout=300)

    # Create a job with the data using proper field aliases
    now = datetime.now()
    job = Job(
        msg_id=1,
        read_ct=1,
        enqueued_at=now,
        vt=now,
        message=job_data,
    )

    # Run the job - this should extract thread_id and pass it correctly
    result = queue.run(job)

    # Verify result
    assert result["status"] == "stored"

    # Restore original invoke
    workflow._compiled.invoke = original_invoke


def test_document_workflow_without_thread_id():
    """Test DocumentWorkflow invocation without thread_id generates one.

    When thread_id is not provided, the Queue should auto-generate one
    based on the job ID.
    """
    from datetime import datetime

    workflow = DocumentWorkflow(
        storage_tool=MockStorageTool(),
        ocr_tool=MockOCRTool(),
    )

    # Job data WITHOUT thread_id
    job_data = {
        "document_path": "test.pdf",
        "metadata": {"source": "email"},
        "status": "pending",
    }

    # Mock the invoke to check what inputs it receives
    def mock_invoke(input_data, config=None):
        # Verify thread_id was auto-generated
        assert config is not None
        assert "configurable" in config
        assert config["configurable"]["thread_id"] == "job-42"
        # Verify input doesn't have thread_id
        assert "thread_id" not in input_data
        return {"status": "stored", "document_path": "test.pdf", "metadata": {}}

    workflow._compiled.invoke = mock_invoke

    # Create Queue and run job
    from aimq.job import Job
    from aimq.queue import Queue

    queue = Queue(runnable=workflow, timeout=300)

    # Create a job with ID 42 using proper field aliases
    now = datetime.now()
    job = Job(
        msg_id=42,
        read_ct=1,
        enqueued_at=now,
        vt=now,
        message=job_data,
    )

    # Run the job - should auto-generate thread_id as "job-42"
    result = queue.run(job)

    # Verify result
    assert result["status"] == "stored"
