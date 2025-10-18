"""Tool for performing OCR on images."""

from typing import Any, Dict, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

from ...attachment import Attachment
from .processor import OCRProcessor


class ImageOCRInput(BaseModel):
    """Input for ImageOCR."""

    image: Attachment = Field(..., description="The image file to perform OCR on")
    save_debug_image: bool = Field(
        default=False,
        description="If True, includes debug image in output showing detected text regions",
    )


class ImageOCR(BaseTool):
    """Tool for performing OCR on images."""

    name: str = "image_ocr"
    description: str = "Extract text from images using OCR"
    args_schema: Type[BaseModel] = ImageOCRInput
    model_config = ConfigDict(arbitrary_types_allowed=True)
    processor: OCRProcessor = Field(default_factory=OCRProcessor)

    def __init__(self, **kwargs):
        """Initialize the OCR processor."""
        super().__init__(**kwargs)

    def _run(self, image: Attachment, save_debug_image: bool = False) -> Dict[str, Any]:
        """
        Process an image and extract text using OCR.

        Args:
            image: The image file to process
            save_debug_image: If True, includes debug image in output

        Returns:
            dict: OCR results including processing time, detected text, and debug image if requested
        """
        if not hasattr(image, "data"):
            raise ValueError("Image data not provided")

        # Process the image
        results = self.processor.process_image(image=image.data, save_debug_image=save_debug_image)

        return results

    async def _arun(self, image: Attachment, save_debug_image: bool = False) -> Dict[str, Any]:
        """Async implementation of run."""
        return self._run(image, save_debug_image)
