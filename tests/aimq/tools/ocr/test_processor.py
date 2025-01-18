"""Tests for OCR processor."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io
import numpy as np

from aimq.tools.ocr.processor import OCRProcessor, boxes_overlap, merge_boxes, group_text_boxes

@pytest.fixture
def mock_image():
    """Create a mock image for testing."""
    # Create a simple test image with some dimensions
    img = Image.new('RGB', (100, 50), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.read()

@pytest.fixture
def mock_detections():
    """Create mock OCR detections for testing."""
    return [
        [[[10, 10], [30, 10], [30, 20], [10, 20]], 'Hello', 0.95],
        [[[40, 10], [60, 10], [60, 20], [40, 20]], 'World', 0.90],
    ]

@pytest.fixture
def ocr_processor():
    """Create an OCR processor instance."""
    return OCRProcessor(languages=['en'])

class TestOCRProcessor:
    def test_init(self, ocr_processor):
        """Test initialization of OCR processor."""
        assert ocr_processor.languages == ['en']
        assert ocr_processor._reader is None

    @patch('easyocr.Reader')
    def test_reader_initialization(self, mock_reader, ocr_processor):
        """Test lazy initialization of EasyOCR reader."""
        mock_reader_instance = Mock()
        mock_reader.return_value = mock_reader_instance
        
        # First access should create reader
        reader = ocr_processor.reader
        assert reader == mock_reader_instance
        mock_reader.assert_called_once_with(['en'])
        
        # Subsequent access should use cached reader
        reader = ocr_processor.reader
        mock_reader.assert_called_once()

    @patch('easyocr.Reader')
    def test_process_image_bytes(self, mock_reader, ocr_processor, mock_image, mock_detections):
        """Test processing image from bytes."""
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.return_value = mock_detections
        mock_reader.return_value = mock_reader_instance

        result = ocr_processor.process_image(mock_image)
        
        assert 'processing_time' in result
        assert 'text' in result
        assert isinstance(result['text'], str)
        assert 'Hello World' in result['text']
        assert 'detections' in result
        assert len(result['detections']) == 1  # Detections are grouped
        
        # Check the grouped detection
        detection = result['detections'][0]
        assert detection['text'] == 'Hello World'
        assert 0.9 <= detection['confidence'] <= 1.0
        assert 'bounding_box' in detection
        bbox = detection['bounding_box']
        assert all(key in bbox for key in ['x', 'y', 'width', 'height'])

    @patch('easyocr.Reader')
    def test_process_image_with_debug(self, mock_reader, ocr_processor, mock_image, mock_detections):
        """Test processing image with debug output."""
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.return_value = mock_detections
        mock_reader.return_value = mock_reader_instance

        result = ocr_processor.process_image(mock_image, save_debug_image=True)
        
        assert 'debug_image' in result
        assert isinstance(result['debug_image'], bytes)

    def test_process_image_invalid_input(self, ocr_processor):
        """Test processing with invalid input."""
        with pytest.raises(ValueError, match="Image must be a file path, PIL Image, or bytes"):
            ocr_processor.process_image(None)

class TestBoxOperations:
    def test_boxes_overlap(self):
        """Test box overlap detection."""
        box1 = {'x': 0, 'y': 0, 'width': 10, 'height': 10}
        box2 = {'x': 5, 'y': 5, 'width': 10, 'height': 10}
        box3 = {'x': 20, 'y': 20, 'width': 10, 'height': 10}
        
        assert boxes_overlap(box1, box2) is True
        assert boxes_overlap(box1, box3) is False

    def test_merge_boxes(self):
        """Test merging of bounding boxes."""
        boxes = [
            {'x': 0, 'y': 0, 'width': 10, 'height': 10},
            {'x': 5, 'y': 5, 'width': 10, 'height': 10}
        ]
        
        merged = merge_boxes(boxes)
        assert merged['x'] == 0
        assert merged['y'] == 0
        assert merged['width'] == 15
        assert merged['height'] == 15

        assert merge_boxes([]) is None

    def test_group_text_boxes(self):
        """Test grouping of text boxes."""
        detections = [
            {'bounding_box': {'x': 0, 'y': 0, 'width': 10, 'height': 10}, 'text': 'Hello', 'confidence': 0.9},
            {'bounding_box': {'x': 5, 'y': 5, 'width': 10, 'height': 10}, 'text': 'World', 'confidence': 0.8},
            {'bounding_box': {'x': 30, 'y': 30, 'width': 10, 'height': 10}, 'text': '!', 'confidence': 0.95}
        ]
        
        groups = group_text_boxes(detections)
        assert len(groups) == 2  # Overlapping boxes should be grouped
        
        # Test with growth parameters
        groups_with_growth = group_text_boxes(detections, width_growth=20, height_growth=20)
        assert len(groups_with_growth) == 1  # All boxes should be grouped due to growth
