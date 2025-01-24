"""
Example demonstrating how to upload a document using AIMQ's worker and Supabase tools.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from aimq.worker import Worker
from aimq.attachment import Attachment
from aimq.tools.supabase.write_file import WriteFile

# Create worker
worker = Worker()

@worker.task()
def upload_document(data: dict):
    """Upload a document to Supabase storage using the WriteFile tool.
    
    Args:
        data: Dictionary containing:
            - file_path: Path to the document to upload
    """
    file_path = Path(data["file_path"])
    
    # Create attachment from file
    with open(file_path, "rb") as f:
        attachment = Attachment(
            name=file_path.name,
            content=f.read(),
            mime_type="application/pdf"
        )
    
    # Create WriteFile tool with custom bucket and path
    write_file = WriteFile(
        bucket="documents",
        path="{{config.user_id}}/{{file.name}}"
    )
    
    # Upload file and create metadata
    result = write_file.invoke({
        "file": attachment,
        "metadata": {
            "original_name": file_path.name,
            "mime_type": "application/pdf"
        }
    })
    
    return result

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Path to test PDF
    test_pdf = Path(__file__).parent / "supabase" / "seed" / "test.pdf"
    
    # Queue document upload task
    msg_id = worker.send(
        "upload_document",
        {"file_path": str(test_pdf)}
    )
    print(f"Queued document upload job: {msg_id}")
    
    # Start the worker (this will block)
    worker.start()
