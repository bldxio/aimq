from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...clients.mistral import mistral


class DocumentOCRInput(BaseModel):
    url: str = Field(..., description="The URL of the PDF file to convert to markdown")


class DocumentOCR(BaseTool):
    """Tool for converting PDFs to markdown."""

    name: str = "document_ocr"
    description: str = "Convert a PDF file to markdown"
    args_schema: Type[BaseModel] = DocumentOCRInput

    def _run(self, url: str) -> dict:
        ocr_response = mistral.client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": url},
            include_image_base64=True,
        )

        return ocr_response
