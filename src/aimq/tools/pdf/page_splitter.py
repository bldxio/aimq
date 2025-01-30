"""Tool for splitting PDFs into individual pages."""

import io
from typing import List, Type

import pypdfium2 as pdfium  # type: ignore  # Missing py.typed marker
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...attachment import Attachment


class PageSplitterInput(BaseModel):
    """Input for PageSplitter."""

    file: Attachment = Field(..., description="The PDF file to split into pages")


class PageSplitter(BaseTool):
    """Tool for splitting PDF into pages."""

    name: str = "pdf_page_splitter"
    description: str = "Split a PDF file into individual pages"
    args_schema: Type[BaseModel] = PageSplitterInput

    def _run(self, file: Attachment) -> List[dict]:
        """Split a PDF into individual pages."""
        try:
            # Read PDF file
            if not hasattr(file, "data"):
                raise ValueError("PDF data not provided")

            pdf = pdfium.PdfDocument(io.BytesIO(file.data))
            pages = []

            try:
                # Process each page
                for position in range(len(pdf)):
                    # Get and render page
                    page = pdf.get_page(position)
                    try:
                        bitmap = page.render()
                        try:
                            image = bitmap.to_pil()

                            # merge metadata dictionaries
                            page_metadata = {
                                "position": position,
                                "width": image.width,
                                "height": image.height,
                            }

                            # Create new attachment for the page
                            buffer = io.BytesIO()
                            image.save(buffer, format="PNG")
                            page_attachment = Attachment(data=buffer.getvalue())

                            pages.append(
                                {"file": page_attachment, "metadata": page_metadata}
                            )
                        finally:
                            # Clean up bitmap
                            bitmap.close()
                    finally:
                        # Clean up page
                        page.close()
            finally:
                # Clean up PDF document
                pdf.close()

            return pages
        except Exception as e:
            raise Exception(f"Error splitting PDF into pages: {str(e)}")
