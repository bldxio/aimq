"""Utility functions for the core package."""

import base64
import importlib.util
import sys
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Any, Generator

from PIL import Image


def encode_image(image: Image.Image) -> str:
    """
    Encode a PIL Image as a base64 string.

    Args:
        image: PIL Image to encode

    Returns:
        Base64 encoded string of the image in PNG format
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@contextmanager
def add_to_path(path: str) -> Generator[None, None, None]:
    """Temporarily add a directory to sys.path.

    Args:
        path: Directory to add to sys.path

    Yields:
        None
    """
    sys.path.insert(0, path)
    try:
        yield
    finally:
        sys.path.pop(0)


def load_module(module_path: Path, *, add_to_sys_path: bool = True) -> Any:
    """Load a Python module from a file path.

    Args:
        module_path: Path to the Python file to load
        add_to_sys_path: Whether to add the module's parent directory to sys.path

    Returns:
        The loaded module

    Raises:
        ImportError: If the module cannot be loaded
    """
    if add_to_sys_path:
        # Add the parent directory to Python path
        module_dir = module_path.parent
        sys.path.insert(0, str(module_dir.parent))

    try:
        # Import the module using the package name
        package_name = module_path.parent.name
        module_name = module_path.stem
        full_module_name = f"{package_name}.{module_name}"

        # Import the module
        spec = importlib.util.spec_from_file_location(full_module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[full_module_name] = module  # Register the module in sys.modules
        spec.loader.exec_module(module)

        return module
    finally:
        if add_to_sys_path:
            # Remove the added path to avoid polluting sys.path
            sys.path.pop(0)
