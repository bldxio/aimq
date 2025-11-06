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

from aimq.tools.ocr import ImageOCR
from aimq.tools.pdf import PageSplitter
from aimq.tools.supabase import ReadFile
from aimq.worker import Worker
from aimq.workflows import DocumentWorkflow

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
    print("=" * 60)
    print("Document Workflow Worker - Automated Processing")
    print("=" * 60)
    print("\nConfiguration:")
    print("  Queue: doc-pipeline")
    print("  Timeout: 900s (15 minutes)")
    print("  Tools: ReadFile, ImageOCR, PageSplitter")
    print("  Checkpointing: Enabled")

    print("\n" + "-" * 60)
    print("Workflow Steps")
    print("-" * 60)
    print("  1. Fetch   - Retrieve document from storage")
    print("  2. Detect  - Identify document type (PDF, image, text)")
    print("  3. Route   - Select appropriate processor")
    print("  4. Process - Extract content using specialized tools")
    print("  5. Store   - Save structured results to database")

    print("\n" + "-" * 60)
    print("Example Jobs")
    print("-" * 60)

    print("\n1. Process PDF document:")
    print("   aimq send doc-pipeline '{")
    print('     "document_path": "uploads/report.pdf",')
    print('     "metadata": {"source": "email", "priority": "high"},')
    print('     "status": "pending"')
    print("   }'")

    print("\n2. Process scanned image:")
    print("   aimq send doc-pipeline '{")
    print('     "document_path": "scans/invoice_001.jpg",')
    print('     "metadata": {"type": "invoice", "department": "finance"},')
    print('     "status": "pending"')
    print("   }'")

    print("\n3. Process batch of documents:")
    print("   for file in uploads/*.pdf; do")
    print("     aimq send doc-pipeline '{")
    print('       "document_path": "' "$file" '",')
    print('       "metadata": {"batch": "2024-10"},')
    print('       "status": "pending"')
    print("     }'")
    print("   done")

    print("\n4. Resumable processing (with thread_id):")
    print("   aimq send doc-pipeline '{")
    print('     "document_path": "large_docs/manual.pdf",')
    print('     "thread_id": "batch-123-doc-456",')
    print('     "metadata": {},')
    print('     "status": "pending"')
    print("   }'")

    print("\n" + "-" * 60)
    print("Document Type Support")
    print("-" * 60)
    print("  - PDF files (.pdf) - Splits into pages, extracts text")
    print("  - Images (.jpg, .png) - OCR text extraction")
    print("  - Text files (.txt, .md) - Direct content reading")
    print("  - Scanned documents - Automatic OCR processing")

    print("\n" + "-" * 60)
    print("Conditional Routing")
    print("-" * 60)
    print("  The workflow automatically detects document type and routes")
    print("  to the appropriate processor:")
    print("    - PDFs → PageSplitter (page-by-page extraction)")
    print("    - Images → ImageOCR (text extraction)")
    print("    - Text → Direct reading (no transformation)")
    print("    - Unknown → Error collection and graceful handling")

    print("\n" + "=" * 60)
    print("Starting worker... Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    worker.start()
