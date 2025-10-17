"""Template task definitions for AIMQ.

This module provides example task definitions that demonstrate how to create and use
worker tasks in AIMQ. These templates can be used as starting points for creating
your own task definitions.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field
from rich import print

from aimq.clients.mistral import mistral
from aimq.clients.supabase import supabase
from aimq.worker import Worker

# Create a worker instance to handle task processing
worker = Worker()


class AttachmentDetails(BaseModel):
    """Attachment details."""

    summary: str = Field(..., description="Summary of the attachment")
    sentiment: float = Field(
        ..., description="Sentiment of the attachment as a range from -1.00 to 1.00"
    )


@worker.task()
def process_attachment(data: Dict[str, Any]) -> Dict[str, str]:
    """Process a document using Mistral."""
    path = data.get("storagePath")
    attachment_id = data.get("attachmentId")
    supabase.client.table("attachments").update({"status": "processing"}).eq(
        "id", attachment_id
    ).execute()

    file_data = supabase.client.storage.from_("attachments").download(path)
    uploaded_file = mistral.client.files.upload(
        file={"file_name": path, "content": file_data}, purpose="ocr"
    )
    signed_url = mistral.client.files.get_signed_url(file_id=uploaded_file.id)
    ocr_result = mistral.client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": signed_url.url},
    )

    # serialize ocr_result
    ocr_result = ocr_result.model_dump()
    ocr_content = "\n".join([page["markdown"] for page in ocr_result["pages"]])

    detail_response = mistral.client.chat.parse(
        messages=[
            {
                "role": "system",
                "content": "You are a summarizer. Given some markdown, summarize it and analyze the sentiment. sentiment is on a scale of -1.00 to 1.00 where -1.00 is very negative and 1.00 is very positive. 0 is neutral but should be avoided.",
            },
            {"role": "user", "content": ocr_content},
        ],
        model="mistral-small-latest",
        response_format=AttachmentDetails,
        temperature=0.0,
    )

    details = detail_response.choices[0].message.parsed
    print(details)

    supabase.client.table("attachments").update(
        {
            "content": ocr_result,
            "status": "processed",
            "summary": details.summary,
            "sentiment": details.sentiment,
        }
    ).eq("id", attachment_id).execute()
    return {
        "signed_url": signed_url.url,
        "file_id": uploaded_file.id,
        "attachment_id": attachment_id,
    }


if __name__ == "__main__":
    # Start the worker to begin processing tasks from all queues
    worker.start()
