---
messages:
  - "Ready to extract text from documents! 📄"
  - "OCR engines warming up... ⚡"
  - "Time to process some PDFs! 🚀"
  - "Document pipeline activated! ✨"
  - "Let's turn images into searchable text! 🔍"
  - "Scanning documents like a boss! 💪"
---

# Document Workflow Worker

Automated document processing with OCR and type detection.

## What This Worker Does

1. **Fetch** - Retrieve documents from Supabase Storage
2. **Detect** - Identify document type (PDF, image, text)
3. **Route** - Select appropriate processor
4. **Process** - Extract content using OCR/PDF tools
5. **Store** - Save results to database

{message}

## Database Setup

Before running, create this table in your Supabase project:

```sql
CREATE TABLE processed_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  path TEXT NOT NULL,
  text TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Supported Document Types

- **PDF files (.pdf)** - Splits into pages, extracts text via OCR
- **Images (.jpg, .png)** - Direct OCR text extraction
- **Text files (.txt, .md)** - Direct content reading
- **Scanned documents** - Automatic OCR processing
