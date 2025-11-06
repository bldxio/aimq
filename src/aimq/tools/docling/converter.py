"""Docling document converter tool."""

from typing import Any, Literal

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class DoclingConverterInput(BaseModel):
    """Input schema for DoclingConverter tool."""

    file_path: str = Field(..., description="Path to document file to convert")
    export_format: Literal["markdown", "html", "json"] = Field(
        default="markdown",
        description="Output format: markdown, html, or json",
    )


class DoclingConverter(BaseTool):
    """
    Convert documents using Docling.

    Supports: PDF, DOCX, PPTX, XLSX, images
    Features: Layout analysis, table extraction, OCR

    Example:
        tool = DoclingConverter()
        result = tool.invoke({
            "file_path": "report.pdf",
            "export_format": "markdown"
        })
    """

    name: str = "docling_convert"
    description: str = """Convert documents (PDF, DOCX, PPTX, XLSX, images) to structured format.
    Supports layout analysis, table extraction, OCR for scanned documents."""
    args_schema: type[BaseModel] = DoclingConverterInput

    def _run(
        self,
        file_path: str,
        export_format: Literal["markdown", "html", "json"] = "markdown",
    ) -> dict[str, Any]:
        """Convert document.

        Args:
            file_path: Path to document file
            export_format: Output format (markdown, html, or json)

        Returns:
            Dict with content, format, and metadata

        Raises:
            ImportError: If docling is not installed
            FileNotFoundError: If file_path does not exist
            ValueError: If file format is not supported
        """
        try:
            from docling.document_converter import DocumentConverter
        except ImportError as e:
            raise ImportError(
                "docling is required for document conversion. " "Install with: uv add docling"
            ) from e

        import os

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Create converter and convert document
        converter = DocumentConverter()
        result = converter.convert(file_path)

        # Export to requested format
        if export_format == "markdown":
            content = result.document.export_to_markdown()
        elif export_format == "html":
            content = result.document.export_to_html()
        else:  # json
            content = result.document.export_to_dict()

        return {
            "content": content,
            "format": export_format,
            "metadata": result.document.metadata,
        }

    async def _arun(
        self,
        file_path: str,
        export_format: Literal["markdown", "html", "json"] = "markdown",
    ) -> dict[str, Any]:
        """Async version of _run.

        Note: Docling doesn't have native async support, so this calls the sync version.
        """
        return self._run(file_path, export_format)
