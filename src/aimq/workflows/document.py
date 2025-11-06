"""Document processing workflow."""

import logging
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, StateGraph

from aimq.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


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
        super().__init__(checkpointer=checkpointer)

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
                "error": END,
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
            content = self.storage_tool.invoke({"path": state["document_path"]})
            logger.debug(f"Document fetched: {len(content)} bytes")
            return {
                "raw_content": content,
                "status": "fetched",
            }
        except Exception as e:
            logger.error(f"Fetch failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _detect_type_node(self, state: DocumentState) -> DocumentState:
        """Detect document type (Fix #11 - Logger integration).

        Args:
            state: Current document state with raw_content

        Returns:
            Updated state with document_type or error status
        """
        import magic

        logger.info("Detecting document type")

        try:
            mime = magic.from_buffer(state["raw_content"], mime=True)

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
        except Exception as e:
            logger.error(f"Type detection failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

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
            attachment = Attachment(state["raw_content"])
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
        except Exception as e:
            logger.error(f"OCR processing failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _process_pdf_node(self, state: DocumentState) -> DocumentState:
        """Process PDF (Fix #11 - Logger integration).

        Args:
            state: Current document state with PDF content

        Returns:
            Updated state with extracted text or error status
        """
        if not self.pdf_tool:
            logger.error("PDF tool not configured")
            return {"status": "error", "text": "No PDF tool configured"}

        logger.info("Processing PDF")

        try:
            pages = self.pdf_tool.invoke({"pdf": state["raw_content"]})
            text = "\n\n".join([p["text"] for p in pages])

            logger.info(f"PDF processed: {len(pages)} pages, {len(text)} characters")

            return {
                "text": text,
                "metadata": {**state.get("metadata", {}), "page_count": len(pages)},
                "status": "processed",
            }
        except Exception as e:
            logger.error(f"PDF processing failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

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
                }
            )

            logger.info("Results stored successfully")
            return {"status": "stored"}

        except Exception as e:
            logger.error(f"Storage failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _route_by_type(self, state: DocumentState) -> str:
        """Route based on document type.

        Args:
            state: Current document state with document_type

        Returns:
            Next node name: "process_image", "process_pdf", or "error"
        """
        doc_type = state.get("document_type")

        if doc_type == "image":
            logger.debug("Routing to image processor")
            return "process_image"
        elif doc_type == "pdf":
            logger.debug("Routing to PDF processor")
            return "process_pdf"

        logger.error(f"Unknown document type: {doc_type}")
        return "error"
