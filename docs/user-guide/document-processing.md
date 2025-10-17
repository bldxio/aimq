# Document Processing

This guide covers AIMQ's document processing capabilities.

## Supported Document Types

AIMQ supports processing various document types:

- Images (JPG, PNG, TIFF, etc.)
- PDFs
- Text documents
- Scanned documents

## Processing Pipeline

### 1. Document Upload

```python
from aimq.attachment import Attachment

# Create attachment from file
attachment = Attachment.from_file("document.pdf")

# Or from bytes
attachment = Attachment.from_bytes(file_bytes, "application/pdf")
```

### 2. Document Analysis

```python
from aimq.tools.pdf import PDFProcessor
from aimq.tools.ocr import ImageOCR

# Process PDF
pdf_processor = PDFProcessor()
pdf_result = pdf_processor.process(attachment)

# Process image with OCR
ocr = ImageOCR()
ocr_result = ocr.process(attachment)
```

### 3. Result Processing

```python
# Extract text
text = result["text"]

# Get metadata
metadata = result["metadata"]

# Access debug information
debug_info = result["debug"]
```

## Processing Tools

### OCR Processing

```python
from aimq.tools.ocr import ImageOCR

ocr = ImageOCR()

# Basic processing
result = ocr.process(image_attachment)

# With debug visualization
result = ocr.process(image_attachment, save_debug_image=True)
debug_image = result["debug_image"]
```

### PDF Processing

```python
from aimq.tools.pdf import PDFProcessor

processor = PDFProcessor()

# Process entire PDF
result = processor.process(pdf_attachment)

# Process specific pages
result = processor.process(pdf_attachment, pages=[1, 3, 5])
```

## Integration with Queue Processing

```python
from aimq import Worker
from aimq.tools.ocr import ImageOCR

worker = Worker()
worker.register_queue("documents")
ocr = ImageOCR()

@worker.processor("documents")
async def process_document(job):
    attachment = job.data["attachment"]

    # Process based on file type
    if attachment.is_image():
        return ocr.process(attachment)
    elif attachment.is_pdf():
        return pdf_processor.process(attachment)
    else:
        raise ValueError(f"Unsupported file type: {attachment.mime_type}")
```

## Best Practices

1. **File Type Validation**
   ```python
   if not attachment.is_supported():
       raise ValueError(f"Unsupported file type: {attachment.mime_type}")
   ```

2. **Error Handling**
   ```python
   try:
       result = processor.process(attachment)
   except ProcessingError as e:
       logger.error(f"Processing failed: {e}")
       raise
   ```

3. **Resource Management**
   ```python
   with attachment.open() as file:
       result = processor.process(file)
   ```

4. **Debug Mode**
   ```python
   # Enable debug mode for more information
   processor.enable_debug()
   result = processor.process(attachment)
   debug_info = result["debug"]
   ```
