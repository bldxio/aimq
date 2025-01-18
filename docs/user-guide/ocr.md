# OCR (Optical Character Recognition)

This guide covers AIMQ's OCR capabilities for extracting text from images.

## Basic Usage

```python
from aimq.tools.ocr import ImageOCR

# Initialize OCR
ocr = ImageOCR()

# Process an image
result = ocr.process_image("image.jpg")
print(result["text"])
```

## Features

### Multi-language Support

```python
# Initialize with multiple languages
ocr = ImageOCR(languages=["en", "es", "fr"])

# Process image
result = ocr.process_image("multilingual.jpg")
```

### Debug Visualization

```python
# Process with debug visualization
result = ocr.process_image("document.jpg", save_debug_image=True)

# Access debug image
debug_image = result["debug_image"]
```

### Text Regions

```python
# Get detailed text regions
result = ocr.process_image("document.jpg")
for region in result["regions"]:
    print(f"Text: {region['text']}")
    print(f"Confidence: {region['confidence']}")
    print(f"Position: {region['bbox']}")
```

## Integration Examples

### Queue Processing

```python
from aimq import Worker
from aimq.tools.ocr import ImageOCR

worker = Worker()
ocr = ImageOCR()

@worker.task(queue="ocr")
def process_image(data):
    image_data = data["image"]
    return ocr.process_image(image_data)
```

### Batch Processing

```python
from aimq.tools.ocr import BatchImageOCR

# Initialize batch processor
batch_ocr = BatchImageOCR()

# Process multiple images
images = ["image1.jpg", "image2.jpg", "image3.jpg"]
results = batch_ocr.process_images(images)
```

### PDF OCR

```python
from aimq.tools.ocr import PDFImageOCR

# Initialize PDF OCR processor
pdf_ocr = PDFImageOCR()

# Process PDF pages
result = pdf_ocr.process_pdf("document.pdf")
```

## Performance Optimization

### Image Preprocessing

```python
from aimq.tools.ocr import ImagePreprocessor

# Initialize preprocessor
preprocessor = ImagePreprocessor()

# Preprocess image
processed_image = preprocessor.process(
    image,
    denoise=True,
    deskew=True,
    enhance_contrast=True
)

# Run OCR on processed image
result = ocr.process_image(processed_image)
```

### Parallel Processing

```python
from aimq.tools.ocr import ParallelOCR

# Initialize parallel processor
parallel_ocr = ParallelOCR(num_workers=4)

# Process images in parallel
results = parallel_ocr.process_images(images)
```

## Best Practices

1. **Image Quality**
   - Ensure good image resolution (at least 300 DPI)
   - Use clear, well-lit images
   - Remove noise and artifacts

2. **Language Selection**
   - Specify correct languages for better accuracy
   - Use multiple languages only when needed

3. **Performance**
   - Use batch processing for multiple images
   - Enable preprocessing for poor quality images
   - Use parallel processing for large workloads

4. **Error Handling**
   ```python
   try:
       result = ocr.process_image(image)
   except OCRError as e:
       logger.error(f"OCR failed: {e}")
       # Handle error appropriately
   ```
