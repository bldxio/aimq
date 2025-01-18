# User Guide Overview

AIMQ is designed to make document processing with AI capabilities easy and efficient. This guide will help you understand the core concepts and features of AIMQ.

## Core Concepts

### Workers and Queues

AIMQ uses a worker-queue pattern where:
- **Workers** manage the processing of jobs
- **Queues** store and distribute jobs to workers
- **Jobs** represent units of work (like documents to process)

### Document Processing

AIMQ supports various document types:
- Images (JPG, PNG, etc.)
- PDFs
- Text documents

### AI Integration

AIMQ integrates with various AI tools and services:
- OCR for text extraction
- Language models for text processing
- Custom AI model integration

## Common Use Cases

1. **Document Processing Pipeline**
   - Upload documents to Supabase storage
   - Queue documents for processing
   - Extract text and metadata
   - Store results

2. **Batch Processing**
   - Process multiple documents in parallel
   - Handle different document types
   - Aggregate results

3. **Real-time Processing**
   - Process documents as they are uploaded
   - Send notifications when processing is complete
   - Stream results to clients

## Next Steps

- Learn about [Queue Processing](queue-processing.md)
- Explore [Document Processing](document-processing.md)
- Try out [OCR capabilities](ocr.md)
