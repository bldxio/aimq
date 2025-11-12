"""
Example: Using built-in DocumentWorkflow

Demonstrates automated document processing pipeline with type detection
and conditional routing.

The DocumentWorkflow handles common document processing tasks:
1. Fetch document from storage
2. Detect document type (PDF, image, text, etc.)
3. Route to appropriate processor based on type
4. Extract and structure content
5. Store results

This is ideal for batch document ingestion and processing workflows.

Usage:
    # Terminal 1: Start worker
    uv run python examples/langgraph/using_builtin_document.py

    # Terminal 2: Send test job
    aimq send doc-pipeline '{
      "document_path": "uploads/report.pdf",
      "metadata": {"source": "email", "priority": "high"},
      "status": "pending"
    }'
"""

import warnings

# Suppress PyTorch MPS warnings (harmless on macOS)
warnings.filterwarnings("ignore", message=".*pin_memory.*")

from aimq.tools.ocr import ImageOCR  # noqa: E402
from aimq.tools.pdf import PageSplitter  # noqa: E402
from aimq.tools.supabase import ReadFile  # noqa: E402
from aimq.worker import Worker  # noqa: E402
from aimq.workflows import DocumentWorkflow  # noqa: E402

# Initialize worker
worker = Worker()

# Configure document workflow
workflow = DocumentWorkflow(
    storage_tool=ReadFile(),  # Tool to fetch documents from storage
    ocr_tool=ImageOCR(),  # Tool for image/scanned document processing
    pdf_tool=PageSplitter(),  # Tool for PDF document processing
    checkpointer=True,  # Enable checkpointing for long documents
)

# Assign to queue
# timeout=900 (15 minutes) allows for processing large documents
# delete_on_finish=True cleans up successful jobs automatically
worker.assign(workflow, queue="doc-pipeline", timeout=900, delete_on_finish=True)

if __name__ == "__main__":
    from pathlib import Path

    motd_path = Path(__file__).parent / "using_builtin_document_MOTD.md"
    worker.start(motd=str(motd_path), show_info=True)
