"""Test the ImageOCR tool."""

from io import BytesIO
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest
from PIL import Image

from aimq.attachment import Attachment
from aimq.tools.ocr.image_ocr import ImageOCR
from aimq.tools.ocr.processor import OCRProcessor


class MockOCRProcessor(OCRProcessor):
    """Mock OCR processor for testing."""

    def __init__(self):
        """Initialize the mock processor."""
        super().__init__()
        self.process_image = Mock()


@pytest.fixture
def mock_processor():
    """Create a mock OCR processor."""
    return MockOCRProcessor()


@pytest.fixture
def image_ocr(mock_processor):
    """Create an ImageOCR instance with a mock processor."""
    return ImageOCR(processor=mock_processor)


@pytest.fixture
def sample_image():
    """Create a sample image attachment."""
    # Create a small test image
    img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    attachment = MagicMock(spec=Attachment)
    attachment.data = img_bytes.getvalue()
    return attachment


def test_image_ocr_initialization(image_ocr, mock_processor):
    """Test that ImageOCR is initialized correctly."""
    assert image_ocr.name == "image_ocr"
    assert image_ocr.description == "Extract text from images using OCR"
    assert image_ocr.processor == mock_processor


def test_image_ocr_run_success(image_ocr, mock_processor, sample_image):
    """Test successful OCR processing."""
    expected_results = {"text": "sample text", "time": 1.0}
    mock_processor.process_image.return_value = expected_results

    results = image_ocr._run(sample_image)

    mock_processor.process_image.assert_called_once_with(
        image=sample_image.data, save_debug_image=False
    )
    assert results == expected_results


def test_image_ocr_run_with_debug(image_ocr, mock_processor, sample_image):
    """Test OCR processing with debug image enabled."""
    expected_results = {"text": "sample text", "time": 1.0, "debug_image": b"debug image data"}
    mock_processor.process_image.return_value = expected_results

    results = image_ocr._run(sample_image, save_debug_image=True)

    mock_processor.process_image.assert_called_once_with(
        image=sample_image.data, save_debug_image=True
    )
    assert results == expected_results


def test_image_ocr_run_invalid_image(image_ocr):
    """Test OCR processing with invalid image."""
    invalid_image = Mock(spec=Attachment)
    # Don't set the data attribute

    with pytest.raises(ValueError, match="Image data not provided"):
        image_ocr._run(invalid_image)


@pytest.mark.asyncio
async def test_image_ocr_arun(image_ocr, mock_processor, sample_image):
    """Test async OCR processing."""
    expected_results = {"text": "sample text", "time": 1.0}
    mock_processor.process_image.return_value = expected_results

    results = await image_ocr._arun(sample_image)

    mock_processor.process_image.assert_called_once_with(
        image=sample_image.data, save_debug_image=False
    )
    assert results == expected_results
