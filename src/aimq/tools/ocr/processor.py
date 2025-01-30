"""OCR module for text extraction and processing from images.

This module provides functionality for extracting and processing text from images
using the EasyOCR library. It includes utilities for handling text bounding boxes,
merging overlapping detections, and creating debug visualizations.
"""

import io
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import easyocr  # type: ignore  # Missing py.typed marker
import numpy as np
from PIL import Image, ImageDraw


def boxes_overlap(box1: Dict[str, int] | None, box2: Dict[str, int] | None) -> bool:
    """
    Check if two boxes overlap at all.

    Args:
        box1: Dictionary with x, y, width, height or None
        box2: Dictionary with x, y, width, height or None

    Returns:
        bool: True if boxes overlap
    """
    if not box1 or not box2:
        return False

    h_overlap = (
        box1["x"] < box2["x"] + box2["width"] and box2["x"] < box1["x"] + box1["width"]
    )

    v_overlap = (
        box1["y"] < box2["y"] + box2["height"]
        and box2["y"] < box1["y"] + box1["height"]
    )

    return h_overlap and v_overlap


def merge_boxes(boxes: List[Dict[str, int]]) -> Optional[Dict[str, int]]:
    """
    Merge a list of bounding boxes into a single box that encompasses all of them.

    Args:
        boxes: List of dictionaries with x, y, width, height

    Returns:
        dict: Merged bounding box or None if input is empty
    """
    if not boxes:
        return None

    min_x = min(box["x"] for box in boxes)
    min_y = min(box["y"] for box in boxes)
    max_x = max(box["x"] + box["width"] for box in boxes)
    max_y = max(box["y"] + box["height"] for box in boxes)

    return {
        "x": int(min_x),
        "y": int(min_y),
        "width": int(max_x - min_x),
        "height": int(max_y - min_y),
    }


def group_text_boxes(
    detections: List[Dict[str, Any]], width_growth: int = 0, height_growth: int = 0
) -> List[Dict[str, Any]]:
    """Group text boxes that are spatially related.

    This function groups text boxes that are spatially related, starting with
    overlapping boxes. It can optionally expand boxes horizontally and vertically
    before grouping to capture nearby text that may be related.

    Args:
        detections: List of detection dictionaries containing text and bounding boxes
        width_growth: Number of pixels to expand boxes horizontally
        height_growth: Number of pixels to expand boxes vertically

    Returns:
        List[Dict[str, Any]]: List of grouped text detections with merged bounding boxes
    """
    if not detections:
        return []

    def grow_box(box: Dict[str, int] | None) -> Dict[str, int] | None:
        """Grow a box by width_growth and height_growth.

        Args:
            box: Box to grow, or None

        Returns:
            Dict[str, int] | None: Grown box or None if input was None
        """
        if not box:
            return None

        return {
            "x": box["x"] - width_growth,
            "y": box["y"] - height_growth,
            "width": box["width"] + 2 * width_growth,
            "height": box["height"] + 2 * height_growth,
        }

    groups = [[det] for det in detections]

    while True:
        merged = False
        new_groups = []
        used = set()

        for i, group1 in enumerate(groups):
            if i in used:
                continue

            merged_group = group1.copy()
            used.add(i)

            box1 = grow_box(merge_boxes([det["bounding_box"] for det in merged_group]))

            for j, group2 in enumerate(groups):
                if j in used:
                    continue

                box2 = grow_box(merge_boxes([det["bounding_box"] for det in group2]))

                if boxes_overlap(box1, box2):
                    merged_group.extend(group2)
                    used.add(j)
                    box1 = grow_box(
                        merge_boxes([det["bounding_box"] for det in merged_group])
                    )
                    merged = True

            new_groups.append(merged_group)

        if not merged:
            break

        groups = new_groups

    return [
        {
            "text": " ".join(
                det["text"]
                for det in sorted(
                    group,
                    key=lambda d: (d["bounding_box"]["y"], d["bounding_box"]["x"]),
                )
            ),
            "confidence": float(
                round(sum(det["confidence"] for det in group) / len(group), 3)
            ),
            "bounding_box": merge_boxes([det["bounding_box"] for det in group]),
        }
        for group in groups
    ]


class OCRProcessor:
    """Processor for performing OCR on images using EasyOCR.

    This class provides a high-level interface for performing OCR on images. It handles
    initialization of the EasyOCR reader, image preprocessing, text detection, and
    optional debug visualization.

    Attributes:
        languages: List of language codes for OCR
        _reader: Lazy-loaded EasyOCR reader instance
    """

    def __init__(self, languages: Optional[List[str]] = None) -> None:
        """Initialize OCR processor with specified languages.

        Args:
            languages: List of language codes (default: ['en'])
        """
        self.languages = languages or ["en"]
        self._reader = None

    @property
    def reader(self) -> easyocr.Reader:
        """Get or initialize the EasyOCR reader.

        Returns:
            easyocr.Reader: Initialized EasyOCR reader instance
        """
        if self._reader is None:
            self._reader = easyocr.Reader(self.languages)
        return self._reader

    def process_image(
        self,
        image: Union[str, Path, Image.Image, bytes],
        save_debug_image: bool = False,
    ) -> Dict[str, Any]:
        """Process an image and return OCR results.

        Args:
            image: The image to process. Can be one of:
                - Path to image file (str or Path)
                - PIL Image object
                - Bytes of image data
            save_debug_image: If True, includes debug image in output

        Returns:
            Dict[str, Any]: OCR results including:
                - processing_time: Time taken to process in seconds
                - text: Extracted text content
                - debug_image: Optional base64 encoded debug image
                - detections: List of text detections with coordinates

        Raises:
            ValueError: If image format is invalid or unreadable
        """
        start_time = time.time()

        # Convert input to a format EasyOCR can process
        image_path: Optional[str] = None
        pil_image: Image.Image

        if isinstance(image, (str, Path)):
            image_path = str(image)
            pil_image = Image.open(image_path)
        elif isinstance(image, bytes):
            image_stream = io.BytesIO(image)
            pil_image = Image.open(image_stream)
        elif isinstance(image, Image.Image):
            pil_image = image
        else:
            raise ValueError("Image must be a file path, PIL Image, or bytes")

        # Convert PIL Image to numpy array for EasyOCR
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        np_image = np.array(pil_image)

        # Read the image with optimized parameters
        results = self.reader.readtext(
            np_image,
            paragraph=False,
            min_size=20,
            text_threshold=0.7,
            link_threshold=0.4,
            low_text=0.4,
            width_ths=0.7,
            height_ths=0.9,
            ycenter_ths=0.9,
        )

        # Format initial results
        detections = []
        for result in results:
            if len(result) == 2:
                bbox, text = result
                confidence = 1.0
            else:
                bbox, text, confidence = result

            x1, y1 = int(bbox[0][0]), int(bbox[0][1])
            x2, _ = int(bbox[1][0]), int(bbox[1][1])
            _, y3 = int(bbox[2][0]), int(bbox[2][1])
            _, _ = int(bbox[3][0]), int(bbox[3][1])

            detections.append(
                {
                    "text": str(text),
                    "confidence": float(round(float(confidence), 3)),
                    "bounding_box": {
                        "x": x1,
                        "y": y1,
                        "width": x2 - x1,
                        "height": y3 - y1,
                    },
                }
            )

        # Group the detections
        grouped_detections = group_text_boxes(
            detections, width_growth=20, height_growth=1
        )

        end_time = time.time()
        output = {
            "processing_time": float(round(end_time - start_time, 2)),
            "detections": grouped_detections,
            "text": " ".join(d["text"] for d in grouped_detections),
        }

        if save_debug_image:
            debug_image = self._create_debug_image(pil_image, grouped_detections)
            # Convert debug image to bytes
            debug_bytes = io.BytesIO()
            debug_image.save(debug_bytes, format="PNG")
            output["debug_image"] = debug_bytes.getvalue()

        return output

    def _create_debug_image(
        self, image: Image.Image, detections: List[Dict[str, Any]]
    ) -> Image.Image:
        """Create a debug image with bounding boxes drawn around detected text.

        Args:
            image: Original image
            detections: List of text detections with bounding boxes

        Returns:
            Image.Image: Debug image with drawn bounding boxes
        """
        debug_image = image.copy()
        draw = ImageDraw.Draw(debug_image)

        for detection in detections:
            bbox = detection["bounding_box"]
            draw.rectangle(
                [
                    bbox["x"],
                    bbox["y"],
                    bbox["x"] + bbox["width"],
                    bbox["y"] + bbox["height"],
                ],
                outline="red",
                width=2,
            )

        return debug_image
