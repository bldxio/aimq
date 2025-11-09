"""Tests for DocumentWorkflow error handling.

Verifies that:
1. Workflow nodes raise exceptions instead of returning error states
2. Unknown document types raise ValueError
"""

from unittest.mock import MagicMock

import pytest

from aimq.workflows.document import DocumentWorkflow


class TestDocumentWorkflowErrorHandling:
    """Test error handling in DocumentWorkflow nodes."""

    @pytest.fixture
    def workflow(self):
        """Create a DocumentWorkflow instance for testing."""
        storage_tool = MagicMock()
        ocr_tool = MagicMock()
        pdf_tool = MagicMock()

        workflow = DocumentWorkflow(
            storage_tool=storage_tool,
            ocr_tool=ocr_tool,
            pdf_tool=pdf_tool,
            checkpointer=False,
        )
        return workflow

    def test_fetch_node_raises_on_storage_error(self, workflow):
        """Test that _fetch_node raises exception when storage fails."""
        # Mock storage tool to raise an error
        workflow.storage_tool.invoke.side_effect = ValueError("Storage failed")

        state = {"document_path": "test.pdf", "metadata": {}, "status": "pending"}

        # Should raise ValueError, not return error state
        with pytest.raises(ValueError, match="Storage failed"):
            workflow._fetch_node(state)

    def test_process_pdf_node_raises_on_pdf_error(self, workflow):
        """Test that _process_pdf_node raises exception when PDF processing fails."""
        workflow.pdf_tool.invoke.side_effect = ValueError("PDF parsing failed")

        state = {
            "raw_content": b"fake pdf data",
            "document_type": "pdf",
            "metadata": {},
            "status": "typed",
        }

        # Should raise ValueError, not return error state
        with pytest.raises(ValueError, match="PDF parsing failed"):
            workflow._process_pdf_node(state)

    def test_route_by_type_raises_on_unknown_type(self, workflow):
        """Test that _route_by_type raises ValueError for unknown document types."""
        state = {"document_type": "unknown", "metadata": {}, "status": "typed"}

        # Should raise ValueError with descriptive message
        with pytest.raises(ValueError, match="Unknown or unsupported document type: unknown"):
            workflow._route_by_type(state)

    def test_route_by_type_raises_on_none_type(self, workflow):
        """Test that _route_by_type raises ValueError when document_type is None."""
        state = {"document_type": None, "metadata": {}, "status": "typed"}

        with pytest.raises(ValueError, match="Unknown or unsupported document type: None"):
            workflow._route_by_type(state)

    def test_route_by_type_returns_correct_routes(self, workflow):
        """Test that _route_by_type returns correct routes for valid types."""
        # Test image routing
        state_image = {"document_type": "image", "metadata": {}, "status": "typed"}
        assert workflow._route_by_type(state_image) == "process_image"

        # Test PDF routing
        state_pdf = {"document_type": "pdf", "metadata": {}, "status": "typed"}
        assert workflow._route_by_type(state_pdf) == "process_pdf"

    def test_fetch_node_successful_path(self, workflow):
        """Test that _fetch_node returns correct state on success."""
        workflow.storage_tool.invoke.return_value = b"test content"

        state = {"document_path": "test.pdf", "metadata": {}, "status": "pending"}

        result = workflow._fetch_node(state)

        assert result["raw_content"] == b"test content"
        assert result["status"] == "fetched"
