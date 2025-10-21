# OCR (Optical Character Recognition)

This guide covers AIMQ's OCR capabilities for extracting text from images using EasyOCR.

## Overview

AIMQ provides two main interfaces for OCR:

- **`OCRProcessor`**: Low-level processor for direct image processing
- **`ImageOCR`**: LangChain tool for integration with AI workflows

## Basic Usage

### Using OCRProcessor Directly

```python
from aimq.tools.ocr.processor import OCRProcessor
from PIL import Image

# Initialize processor
processor = OCRProcessor(languages=["en"])

# Process an image (supports multiple input formats)
result = processor.process_image("image.jpg")
print(result["text"])
print(f"Processing time: {result['processing_time']}s")

# View individual text detections
for detection in result["detections"]:
    print(f"Text: {detection['text']}")
    print(f"Confidence: {detection['confidence']}")
    print(f"Position: {detection['bounding_box']}")
```

### Supported Input Formats

```python
# From file path
result = processor.process_image("image.jpg")

# From PIL Image
from PIL import Image
img = Image.open("image.jpg")
result = processor.process_image(img)

# From bytes
with open("image.jpg", "rb") as f:
    image_bytes = f.read()
result = processor.process_image(image_bytes)
```

## Features

### Multi-language Support

```python
# Initialize with multiple languages
processor = OCRProcessor(languages=["en", "es", "fr", "de"])

# Process multilingual document
result = processor.process_image("multilingual.jpg")
```

**Supported languages** (partial list):
- `en`: English
- `es`: Spanish
- `fr`: French
- `de`: German
- `ja`: Japanese
- `zh`: Chinese
- See [EasyOCR documentation](https://www.jaided.ai/easyocr/) for full list

### Debug Visualization

Get a debug image with bounding boxes drawn around detected text:

```python
result = processor.process_image("document.jpg", save_debug_image=True)

# Access debug image bytes
debug_image_bytes = result["debug_image"]

# Save debug image
from PIL import Image
import io
debug_img = Image.open(io.BytesIO(debug_image_bytes))
debug_img.save("debug_output.png")
```

### Text Detection Details

```python
result = processor.process_image("document.jpg")

# Full extracted text
print(result["text"])

# Individual detections with positions and confidence
for detection in result["detections"]:
    text = detection["text"]
    confidence = detection["confidence"]  # 0.0 to 1.0
    bbox = detection["bounding_box"]  # {x, y, width, height}

    print(f"{text} ({confidence:.2%} confident)")
    print(f"  Position: x={bbox['x']}, y={bbox['y']}")
```

## Integration with AIMQ Workers

### Using as a LangChain Tool

```python
from aimq import Worker
from aimq.tools.ocr import ImageOCR
from aimq.attachment import Attachment

worker = Worker()

# ImageOCR is a LangChain BaseTool
ocr_tool = ImageOCR()

@worker.task(queue="ocr-processing")
def process_document(data):
    """Process document with OCR."""
    # Create attachment from image data
    attachment = Attachment(data=data["image_bytes"])

    # Use the OCR tool (using public invoke API)
    result = ocr_tool.invoke({
        "image": attachment,
        "save_debug_image": True
    })

    return {
        "text": result["text"],
        "confidence": sum(d["confidence"] for d in result["detections"]) / len(result["detections"]),
        "processing_time": result["processing_time"]
    }
```

### Processing from Supabase Storage

```python
from aimq import Worker
from aimq.tools.ocr.processor import OCRProcessor
from aimq.tools.supabase import read_file

worker = Worker()
processor = OCRProcessor()

@worker.task(queue="document-ocr")
def process_stored_document(data):
    """Process document from Supabase storage."""
    # Read file from Supabase storage (returns dict with "file" key containing Attachment)
    result = read_file.invoke({
        "bucket": "documents",
        "path": data["document_path"]
    })

    # Process image bytes with OCR (extract bytes from Attachment)
    ocr_result = processor.process_image(result["file"].data)

    return {
        "text": ocr_result["text"],
        "detections": ocr_result["detections"]
    }
```

## Performance Optimization

### Image Quality Recommendations

For best OCR results:

1. **Resolution**: Minimum 300 DPI for scanned documents
2. **Format**: PNG or JPG with minimal compression
3. **Lighting**: Clear, even lighting without shadows
4. **Contrast**: High contrast between text and background
5. **Orientation**: Properly oriented (not rotated or skewed)

### Language Selection Strategy

```python
# Single language (fastest)
processor_en = OCRProcessor(languages=["en"])

# Multiple languages (slower but more flexible)
processor_multi = OCRProcessor(languages=["en", "es"])

# Choose based on your use case:
# - Use single language when content is known
# - Use multiple languages for mixed-language documents
```

### Processing Large Volumes

For processing many images, consider:

```python
from aimq import Worker
from aimq.tools.ocr.processor import OCRProcessor

# Reuse the processor across multiple calls
# (the EasyOCR reader is lazy-loaded and cached)
processor = OCRProcessor()

@worker.task(queue="batch-ocr")
def batch_process(data):
    """Process multiple images efficiently."""
    results = []
    for image_path in data["images"]:
        result = processor.process_image(image_path)
        results.append({
            "path": image_path,
            "text": result["text"]
        })
    return results
```

## Best Practices

### Error Handling

```python
from aimq.tools.ocr.processor import OCRProcessor

processor = OCRProcessor()

try:
    result = processor.process_image("document.jpg")
    if not result["text"].strip():
        print("Warning: No text detected")
except ValueError as e:
    print(f"Invalid image format: {e}")
except Exception as e:
    print(f"OCR processing failed: {e}")
```

### Filtering Low-Confidence Results

```python
result = processor.process_image("noisy_image.jpg")

# Filter out low-confidence detections
high_confidence_text = []
for detection in result["detections"]:
    if detection["confidence"] > 0.7:  # 70% confidence threshold
        high_confidence_text.append(detection["text"])

clean_text = " ".join(high_confidence_text)
```

### Text Grouping

OCR results are automatically grouped by spatial proximity. The grouping parameters are:

- `width_growth=20`: Horizontal tolerance for grouping text
- `height_growth=1`: Vertical tolerance for grouping text

This ensures text on the same line or in the same paragraph is grouped together.
