"""Mistral toolss."""

from typing import List

from langchain.tools import BaseTool

from .document_ocr import DocumentOCR, DocumentOCRInput
from .upload_file import UploadFile, UploadFileInput

__all__ = ["DocumentOCR", "DocumentOCRInput", "UploadFile", "UploadFileInput"]


def get_tools() -> List[BaseTool]:
    """Get all Mistral tools."""
    tools: List[BaseTool] = [
        DocumentOCR(),
        UploadFile(),
    ]
    return tools
