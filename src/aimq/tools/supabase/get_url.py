"""Tool for getting the signed URL of a file in Supabase Storage."""

from typing import Any, Dict, Optional, Type

from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from typing_extensions import Literal

from ...clients.supabase import supabase


class GetUrlInput(BaseModel):
    """Input for GetUrl."""

    path: str = Field(..., description="The path of the file")
    bucket: Optional[str] = Field("files", description="The storage bucket to read the file from")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata to attach to the file"
    )


class GetUrl(BaseTool):
    """Tool for getting the signed URL of a file in Supabase Storage."""

    name: str = "get_url"
    description: str = "Get the signed URL of a file in Supabase Storage"
    args_schema: Type[BaseModel] = GetUrlInput

    bucket: str | PromptTemplate = Field(
        "{{bucket}}", description="The storage bucket to read the file from"
    )
    path: str | PromptTemplate = Field("{{path}}", description="The path of the file")
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
        path: str,
        bucket: Optional[str] = None,
        metadata: Dict[str, Any] = {},
        config: RunnableConfig = RunnableConfig(),
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Get the signed URL of a file in Supabase Storage.

        Args:
            path: The path of the file
            bucket: Optional bucket name to override the default
            metadata: Optional metadata to attach to the file
        """
        try:
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

            url = supabase.client.storage.from_(bucket).create_signed_url(path)
            if not url:
                raise ValueError(f"No URL received for {path}")

            return {"url": url, "metadata": metadata}

        except Exception as e:
            raise ValueError(f"Error getting URL for {path}: {str(e)}")
