"""Tool for uploading files to Mistral."""

from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ...attachment import Attachment
from ...clients.mistral import mistral


class UploadFileInput(BaseModel):
    """Input for UploadFile."""

    file: Attachment = Field(..., description="The file to upload")


class UploadFile(BaseTool):
    """Tool for uploading files to Mistral."""

    name: str = "upload_file"
    description: str = "Upload a file to Mistral"
    args_schema: Type[BaseModel] = UploadFileInput

    def _run(self, file: Attachment) -> dict:
        """Upload a file to Mistral."""
        try:
            response = mistral.client.files.upload(file.data)
            signed_url = mistral.client.files.get_signed_url(response["id"])
            return {"file_id": response["id"], "signed_url": signed_url}
        except Exception as e:
            raise ValueError(f"Error uploading file to Mistral: {str(e)}")
