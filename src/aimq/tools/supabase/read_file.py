"""Tool for reading files from Supabase Storage."""

from typing import Any, Dict, Literal, Optional, Type

from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from ...attachment import Attachment
from ...clients.supabase import supabase


class ReadFileInput(BaseModel):
    """Input for ReadFile."""

    path: Optional[str] = Field(..., description="The path values to apply to the template path")
    bucket: Optional[str] = Field("files", description="The storage bucket to read the file from")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata to attach to the file"
    )


class ReadFile(BaseTool):
    """Tool for reading files from Supabase Storage."""

    name: str = "read_file"
    description: str = "Read a file from Supabase Storage"
    args_schema: Type[BaseModel] = ReadFileInput

    bucket: str | PromptTemplate = Field(
        "{{bucket}}", description="The storage bucket template to read the file from"
    )
    path: str | PromptTemplate = Field(
        "{{path}}", description="The path template to use for the file"
    )
    formater: Literal["f-string", "mustache"] = Field(
        "mustache", description="The format to use for the template"
    )

    def _get_template(self, value: str | PromptTemplate) -> PromptTemplate:
        """Convert a string or PromptTemplate to a PromptTemplate."""
        if isinstance(value, PromptTemplate):
            return value
        return PromptTemplate.from_template(value, template_format=self.formater)

    def _run(
        self,
        path: Optional[str] = None,
        bucket: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: RunnableConfig = RunnableConfig(),
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Read a file from Supabase Storage.

        Args:
            path: The path values to apply to the template path
            bucket: Optional bucket name to override the default
            metadata: Optional metadata to attach to the file
        """
        try:
            if metadata is None:
                metadata = {}

            template_args = metadata | {
                "path": path,
                "bucket": bucket,
                "config": config.get("configurable", {}),
            }
            template_args["config"] = config.get("configurable", {})

            bucket = self._get_template(self.bucket).format(**template_args)
            path = self._get_template(self.path).format(**template_args)

            # Initialize metadata
            metadata.update({"bucket": bucket, "path": path})

            data = supabase.client.storage.from_(bucket).download(path)
            if not data:
                raise ValueError(f"No data received for {path}")

            return {"file": Attachment(data=data), "metadata": metadata}
        except Exception as e:
            raise ValueError(f"Error reading file from Supabase: {str(e)}")
