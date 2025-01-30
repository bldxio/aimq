# type: ignore  # mypy is configured to ignore test files in pyproject.toml
"""Tests for the attachment module.

This module contains test cases for the Attachment class, which handles
file attachments with various data types and formats.
"""
import io

import filetype  # Missing py.typed marker
import pytest
from PIL import Image

from aimq.attachment import Attachment


class TestAttachment:
    """Test cases for Attachment class."""

    @pytest.fixture
    def sample_image_bytes(self):
        """Create sample image bytes."""
        img = Image.new("RGB", (100, 100), color="red")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    @pytest.fixture
    def sample_text_bytes(self):
        """Create sample text bytes."""
        return b"Hello, World!"

    def test_attachment_creation(self, sample_image_bytes):
        """Test basic attachment creation."""
        attachment = Attachment(data=sample_image_bytes)
        assert attachment.data == sample_image_bytes
        assert attachment.mimetype.startswith("image/")
        assert attachment.extension is not None
        assert isinstance(attachment.size, str)

    def test_attachment_with_text(self, sample_text_bytes):
        """Test attachment with text data."""
        attachment = Attachment(data=sample_text_bytes)
        assert attachment.data == sample_text_bytes
        assert attachment.mimetype == "application/octet-stream"
        assert attachment.extension is None

    def test_get_method(self, sample_image_bytes):
        """Test get method for accessing attributes."""
        attachment = Attachment(data=sample_image_bytes)

        # Test existing attribute
        assert attachment.get("mimetype") == attachment.mimetype

        # Test non-existing attribute
        assert attachment.get("nonexistent", "default") == "default"

    def test_repr_args(self, sample_image_bytes):
        """Test representation arguments."""
        attachment = Attachment(data=sample_image_bytes)
        repr_args = dict(attachment.__repr_args__())

        # Check that sensitive data is not in repr
        assert "data" not in repr_args
        assert "_mimetype" not in repr_args
        assert "_extension" not in repr_args

        # Check that computed fields are included
        assert "size" in repr_args

    def test_to_file_with_image(self, sample_image_bytes):
        """Test to_file method with image data."""
        attachment = Attachment(data=sample_image_bytes)
        assert attachment.mimetype.startswith("image/")
        image = attachment.to_file()
        assert isinstance(image, Image.Image)

    def test_to_file_with_invalid_data(self, sample_text_bytes):
        """Test to_file method with non-image data."""
        attachment = Attachment(data=sample_text_bytes)
        with pytest.raises(ValueError):
            _ = attachment.to_file()

    def test_model_post_init(self, sample_image_bytes):
        """Test post initialization processing."""
        attachment = Attachment(data=sample_image_bytes)
        kind = filetype.guess(sample_image_bytes)

        assert kind is not None, "File type could not be determined"
        assert attachment._mimetype == kind.mime
        assert attachment._extension == kind.extension
