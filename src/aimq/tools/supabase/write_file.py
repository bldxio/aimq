"""Tool for writing files to Supabase Storage."""
from typing import Literal, Optional, Type, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ...clients.supabase import supabase
from ...attachment import Attachment

class WriteFileInput(BaseModel):
    """Input for WriteFile."""
    file: Attachment = Field(..., description="The file to write")
    path: Optional[str] = Field(None, description="The path values to apply to the template path")
    bucket: Optional[str] = Field("files", description="The storage bucket to read the file from")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata to attach to the file")

class WriteFile(BaseTool):
    """Tool for writing files to Supabase Storage."""
    name: str = "write_file"
    description: str = "Write a file to Supabase Storage"
    args_schema: Type[WriteFileInput] = WriteFileInput

    bucket: str | PromptTemplate = Field("{{bucket}}", description="The storage bucket template to read the file from")
    path: str | PromptTemplate = Field("{{path}}", description="The path template to use for the file")  
    formater: Literal['f-string', 'mustache'] = Field("mustache", description="The format to use for the template")

    def _get_template(self, value: str | PromptTemplate) -> PromptTemplate:
        """Convert a string or PromptTemplate to a PromptTemplate."""
        if isinstance(value, PromptTemplate):
            return value
        return PromptTemplate.from_template(value, template_format=self.formater)

    def _run(
        self, 
        file: Attachment, 
        path: Optional[str] = None, 
        bucket: Optional[str] = None, 
        metadata: Dict[str, Any] = {},
        config: RunnableConfig = RunnableConfig(),
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        """Write a file to Supabase Storage."""
        try:
            template_args = metadata.copy()
            template_args["file"] = file
            template_args["config"] = config.get("configurable", {})
            template_args["path"] = path or template_args.get("path", None)
            template_args["bucket"] = bucket or template_args.get("bucket", None)

            bucket = self._get_template(self.bucket).format(**template_args)
            path = self._get_template(self.path).format(**template_args)
            mimetype = file.mimetype

            supabase.client.storage.from_(bucket).upload(
                path=path,
                file=file.data,
                file_options={ "upsert": "true", "content-type": mimetype }
            )

            return {
                "metadata": metadata,
                "bucket": bucket,
                "path": path,
                "full_path": f"{bucket}/{path}"
            }
        except Exception as e:
            raise ValueError(f"Error writing file to Supabase: {str(e)}")
