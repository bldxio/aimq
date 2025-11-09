"""Document processing workflow."""

import logging
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, StateGraph
from rich.console import Console
from rich.panel import Panel

from aimq.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)
console = Console()


class DocumentState(TypedDict):
    """State for document workflow.

    Required fields must be present at initialization.
    NotRequired fields are populated during workflow execution.
    """

    document_path: str  # Required: path to document
    metadata: dict  # Required: metadata container
    status: str  # Required: current status

    # Optional fields populated during workflow
    raw_content: NotRequired[bytes]  # Fetched content
    document_type: NotRequired[Literal["image", "pdf", "docx"]]  # Detected type
    text: NotRequired[str]  # Extracted text


class DocumentWorkflow(BaseWorkflow):
    """
    Multi-step document processing pipeline.

    Steps:
    1. Fetch document from storage
    2. Detect document type
    3. Route to appropriate processor (OCR, PDF, etc.)
    4. Extract metadata
    5. Store results

    Args:
        storage_tool: Tool for reading files (e.g., ReadFile())
        ocr_tool: Tool for OCR processing (e.g., ImageOCR())
        pdf_tool: Tool for PDF processing (e.g., PageSplitter())
        checkpointer: Enable state persistence

    Example:
        from aimq.workflows import DocumentWorkflow
        from aimq.tools.supabase import ReadFile, WriteRecord
        from aimq.tools.ocr import ImageOCR

        workflow = DocumentWorkflow(
            storage_tool=ReadFile(),
            ocr_tool=ImageOCR(),
            checkpointer=True
        )

        worker.assign(workflow, queue="documents")
    """

    def __init__(
        self,
        storage_tool,
        ocr_tool,
        pdf_tool=None,
        checkpointer: bool = False,
    ):
        """Initialize document workflow.

        Args:
            storage_tool: Tool for reading files from storage
            ocr_tool: Tool for OCR processing of images
            pdf_tool: Tool for PDF processing (optional)
            checkpointer: Enable state persistence
        """
        self.storage_tool = storage_tool
        self.ocr_tool = ocr_tool
        self.pdf_tool = pdf_tool

        # Validate libmagic availability
        self._magic_available = self._check_libmagic()

        super().__init__(checkpointer=checkpointer)

    def _check_libmagic(self) -> bool:
        """Check if libmagic is available for MIME type detection.

        Returns:
            True if libmagic is available, False otherwise
        """
        try:
            import magic

            # Test if libmagic library is actually loaded
            magic.from_buffer(b"test", mime=True)
            logger.info("libmagic is available for MIME type detection")
            return True
        except Exception as e:
            console.print(
                Panel(
                    f"[bold yellow]⚠️  libmagic is not available[/]\n\n"
                    f"{type(e).__name__}: {e}\n\n"
                    "Falling back to filename extension detection.\n"
                    "To enable MIME type detection, install libmagic:\n\n"
                    "[cyan]macOS:[/]   brew install libmagic\n"
                    "[cyan]Ubuntu:[/]  apt-get install libmagic1\n"
                    "[cyan]Alpine:[/]  apk add libmagic\n"
                    "[cyan]Windows:[/] pip install python-magic-bin",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )
            return False

    def _build_graph(self) -> StateGraph:
        """Build document processing graph.

        Returns:
            StateGraph with fetch -> detect -> process -> store pipeline
        """
        graph = StateGraph(DocumentState)

        # Add nodes
        graph.add_node("fetch", self._fetch_node)
        graph.add_node("detect", self._detect_type_node)
        graph.add_node("process_image", self._process_image_node)
        graph.add_node("process_pdf", self._process_pdf_node)
        graph.add_node("store", self._store_node)

        # Add edges
        graph.add_edge("fetch", "detect")
        graph.add_conditional_edges(
            "detect",
            self._route_by_type,
            {
                "process_image": "process_image",
                "process_pdf": "process_pdf",
            },
        )
        graph.add_edge("process_image", "store")
        graph.add_edge("process_pdf", "store")
        graph.add_edge("store", END)

        graph.set_entry_point("fetch")

        return graph

    def _fetch_node(self, state: DocumentState) -> DocumentState:
        """Fetch document from storage (Fix #11 - Logger integration).

        Args:
            state: Current document state

        Returns:
            Updated state with raw_content or error status
        """
        logger.info(f"Fetching document: {state['document_path']}")

        try:
            result = self.storage_tool.invoke({"path": state["document_path"]})
            # ReadFile returns {"file": Attachment(...), "metadata": ...}
            # Extract the bytes from the Attachment
            raw_bytes = result["file"].data
            logger.debug(f"Document fetched: {len(raw_bytes)} bytes")
            return {
                "raw_content": raw_bytes,
                "status": "fetched",
            }
        except Exception:
            # Let exception propagate - Queue will handle logging
            raise

    def _detect_type_node(self, state: DocumentState) -> DocumentState:
        """Detect document type using libmagic or filename fallback.

        Args:
            state: Current document state with raw_content and document_path

        Returns:
            Updated state with document_type or error status
        """
        logger.info("Detecting document type")

        try:
            if self._magic_available:
                # Use libmagic for accurate MIME detection
                import magic

                mime = magic.from_buffer(state["raw_content"], mime=True)
                logger.debug(f"Detected MIME type via libmagic: {mime}")
            else:
                # Fallback to filename extension
                mime = self._detect_mime_from_filename(state["document_path"])
                logger.debug(f"Detected MIME type via filename: {mime}")

            if mime.startswith("image/"):
                doc_type = "image"
            elif mime == "application/pdf":
                doc_type = "pdf"
            else:
                doc_type = "unknown"

            logger.info(f"Detected type: {doc_type} (mime: {mime})")

            return {
                "document_type": doc_type,
                "metadata": {**state.get("metadata", {}), "mime_type": mime},
                "status": "typed",
            }
        except Exception:
            # Let exception propagate - Queue will handle logging
            raise

    def _detect_mime_from_filename(self, filename: str) -> str:
        """Fallback MIME type detection from filename extension.

        Args:
            filename: The filename or path to analyze

        Returns:
            MIME type string based on file extension
        """
        import os

        _, ext = os.path.splitext(filename.lower())

        mime_types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
        }

        return mime_types.get(ext, "application/octet-stream")

    def _process_image_node(self, state: DocumentState) -> DocumentState:
        """Process image with OCR (Fix #11 - Logger integration).

        Args:
            state: Current document state with image content

        Returns:
            Updated state with extracted text or error status
        """
        from aimq.attachment import Attachment

        logger.info("Processing image with OCR")

        try:
            attachment = Attachment(data=state["raw_content"])
            result = self.ocr_tool.invoke({"image": attachment})

            logger.info(f"OCR complete: {len(result.get('text', ''))} characters")

            return {
                "text": result["text"],
                "metadata": {
                    **state.get("metadata", {}),
                    "ocr_confidence": result.get("confidence"),
                },
                "status": "processed",
            }
        except Exception:
            # Let exception propagate - Queue will handle logging
            raise

    def _process_pdf_node(self, state: DocumentState) -> DocumentState:
        """Process PDF by splitting into pages and running OCR.

        Args:
            state: Current document state with PDF content

        Returns:
            Updated state with extracted text

        Raises:
            ValueError: If PDF tool is not configured
        """
        from aimq.attachment import Attachment

        if not self.pdf_tool:
            raise ValueError("PDF tool not configured")

        logger.info("Processing PDF")

        try:
            # Split PDF into page images
            attachment = Attachment(data=state["raw_content"])
            pages = self.pdf_tool.invoke({"file": attachment})

            # Run OCR on each page image to extract text
            page_texts = []
            for i, page in enumerate(pages):
                logger.debug(f"Running OCR on page {i + 1}/{len(pages)}")
                ocr_result = self.ocr_tool.invoke({"image": page["file"]})
                page_texts.append(ocr_result.get("text", ""))

            # Combine text from all pages
            text = "\n\n".join(page_texts)

            logger.info(f"PDF processed: {len(pages)} pages, {len(text)} characters")

            return {
                "text": text,
                "metadata": {**state.get("metadata", {}), "page_count": len(pages)},
                "status": "processed",
            }
        except Exception:
            # Let exception propagate - Queue will handle logging
            raise

    def _store_node(self, state: DocumentState) -> DocumentState:
        """Store results (Fix #11 - Logger integration).

        Args:
            state: Current document state with processed text

        Returns:
            Updated state with stored status or error
        """
        from aimq.tools.supabase import WriteRecord

        logger.info("Storing results")

        try:
            write_tool = WriteRecord()
            write_tool.invoke(
                {
                    "table": "processed_documents",
                    "data": {
                        "path": state["document_path"],
                        "text": state.get("text"),
                        "metadata": state.get("metadata"),
                    },
                    "id": "",  # Empty string = insert new record
                }
            )

            logger.info("Results stored successfully")
            return {"status": "stored"}

        except Exception:
            # Let exception propagate - Queue will handle logging
            raise

    def _route_by_type(self, state: DocumentState) -> str:
        """Route based on document type.

        Args:
            state: Current document state with document_type

        Returns:
            Next node name: "process_image" or "process_pdf"

        Raises:
            ValueError: If document type is unknown or unsupported
        """
        doc_type = state.get("document_type")

        if doc_type == "image":
            logger.debug("Routing to image processor")
            return "process_image"
        elif doc_type == "pdf":
            logger.debug("Routing to PDF processor")
            return "process_pdf"

        # Unknown document type - let Queue handle logging
        raise ValueError(f"Unknown or unsupported document type: {doc_type}")
