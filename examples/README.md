# AIMQ Examples

This directory contains examples demonstrating how to use AIMQ with Supabase for document processing.

## Prerequisites

- [Supabase CLI](https://supabase.com/docs/guides/cli)
- Docker Desktop
- Python 3.11+

## Local Development Setup

1. Start the local Supabase instance:
   ```bash
   supabase start
   ```

2. Note down the following credentials (they will be displayed after starting):
   - API URL
   - anon key
   - service_role key
   - DB URL

3. Create a `.env` file in the examples directory:
   ```bash
   SUPABASE_URL=http://127.0.0.1:54321
   SUPABASE_KEY=your-service-role-key
   SUPABASE_USER_ID=00000000-0000-0000-0000-000000000000
   ```

4. Upload a test document:
   ```bash
   python upload_document.py
   ```
   This will upload the test PDF from `supabase/seed/test.pdf` using AIMQ's Supabase client.

5. Run the example tasks:
   
   Option 1 - Using AIMQ CLI (Recommended):
   ```bash
   # Start the worker to process tasks
   aimq start upload_document.py
   ```

   Option 2 - Running the script directly:
   ```bash
   # The script will start its own worker
   python upload_document.py
   ```

## Project Structure

- `supabase/` - Supabase project configuration and migrations
  - `migrations/` - Database migrations including PGMQ setup
  - `seed.sql` - Sample data for testing
  - `seed/` - Test files for uploading
- `upload_document.py` - Example showing how to upload documents using AIMQ
- `supabase_tasks.py` - Example AIMQ tasks using Supabase

## Available Examples

1. Document Upload (`upload_document.py`):
   - Upload a document to Supabase Storage
   - Create document metadata
   - Uses AIMQ's Supabase client

2. Document Processing (`supabase_tasks.py`):
   - Process uploaded documents using AIMQ
   - Store results back in Supabase
   - Handle document queues with PGMQ

## Additional Resources

- [AIMQ Documentation](https://bldxio.github.io/aimq)
- [Supabase Documentation](https://supabase.com/docs)
- [PGMQ Documentation](https://supabase.com/docs/guides/database/extensions/pgmq)