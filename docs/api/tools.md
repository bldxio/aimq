# Tools API Reference

AIMQ provides a set of built-in tools for document processing and storage operations.

## OCR Tools

AIMQ includes OCR (Optical Character Recognition) capabilities for extracting text from images.

### ImageOCR

LangChain tool for performing OCR on images. Supports multiple languages and debug visualization.

**Full Reference:** [ImageOCR API](../reference/aimq/tools/ocr/image_ocr.md)

### OCRProcessor

Low-level processor for direct image processing with EasyOCR. Provides detailed text detection results with bounding boxes and confidence scores.

**Full Reference:** [OCRProcessor API](../reference/aimq/tools/ocr/processor.md)

## PDF Tools

### PageSplitter

Tool for splitting PDF documents into individual pages for parallel processing.

**Full Reference:** [PageSplitter API](../reference/aimq/tools/pdf/page_splitter.md)

## Storage Tools

AIMQ includes tools for interacting with Supabase storage and database.

### Supabase Storage

- **[ReadFile](../reference/aimq/tools/supabase/read_file.md)** - Read files from Supabase storage buckets
- **[WriteFile](../reference/aimq/tools/supabase/write_file.md)** - Write files to Supabase storage buckets

### Supabase Database

- **[ReadRecord](../reference/aimq/tools/supabase/read_record.md)** - Query records from Supabase database tables
- **[WriteRecord](../reference/aimq/tools/supabase/write_record.md)** - Insert or update records in Supabase database tables

### Queue Operations

- **[Enqueue](../reference/aimq/tools/supabase/enqueue.md)** - Send messages to pgmq queues

## See Also

For complete auto-generated API documentation, see the [Reference section](../reference/aimq/tools/index.md).
