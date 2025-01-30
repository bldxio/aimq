# type: ignore  # mypy is configured to ignore test files in pyproject.toml
"""Tests for the utils module.

This module contains test cases for utility functions, including image encoding,
path manipulation, and module loading functionality.
"""

import io
import sys

import pytest
from PIL import Image  # type: ignore  # PIL doesn't have type hints

from aimq.utils import add_to_path, encode_image, load_module


class TestUtils:
    """Test cases for utility functions."""

    @pytest.fixture
    def sample_image(self):
        """Create a simple test image."""
        img = Image.new("RGB", (100, 100), color="red")
        return img

    def test_encode_image(self, sample_image):
        """Test image encoding to base64."""
        encoded = encode_image(sample_image)
        assert isinstance(encoded, str)
        assert len(encoded) > 0

        # Verify it's valid base64 that can be decoded
        import base64

        decoded_bytes = base64.b64decode(encoded)
        image_stream = io.BytesIO(decoded_bytes)
        decoded_image = Image.open(image_stream)
        assert isinstance(decoded_image, Image.Image)

    def test_add_to_path(self, tmp_path):
        """Test temporarily adding a path to sys.path."""
        test_path = str(tmp_path)
        original_path = sys.path.copy()

        with add_to_path(test_path):
            assert test_path == sys.path[0]

        assert sys.path == original_path
        assert test_path not in sys.path

    def test_load_module(self, tmp_path):
        """Test loading a Python module from file."""
        # Create a test module
        module_path = tmp_path / "test_module.py"
        module_path.write_text(
            """
def test_function():
    return "Hello from test module"
"""
        )

        # Test loading with add_to_sys_path=True
        module = load_module(module_path)
        assert hasattr(module, "test_function")
        assert module.test_function() == "Hello from test module"

        # Test loading with add_to_sys_path=False
        module = load_module(module_path, add_to_sys_path=False)
        assert hasattr(module, "test_function")
