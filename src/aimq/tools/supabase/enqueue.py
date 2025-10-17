"""Tool for enqueueing jobs to Supabase Queue."""

from typing import Any, Dict, Literal, Optional, Type

from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from ...providers.supabase import SupabaseQueueProvider


class EnqueueInput(BaseModel):
    """Input for Enqueue."""

    data: Dict[str, Any] = Field(..., description="The job data to enqueue")
    queue: Optional[str] = Field(None, description="The queue name to send the job to")
    delay: Optional[int] = Field(
        None, description="Optional delay in seconds before the job becomes available"
    )


class Enqueue(BaseTool):
    """Tool for enqueueing jobs to Supabase Queue."""

    name: str = "enqueue"
    description: str = "Send a job to a Supabase Queue"
    args_schema: Type[BaseModel] = EnqueueInput

    queue: str | PromptTemplate = Field(
        "{{queue}}", description="The queue template to send the job to"
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
        data: Dict[str, Any],
        queue: Optional[str] = None,
        delay: Optional[int] = None,
        config: RunnableConfig = RunnableConfig(),
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Send a job to a Supabase Queue.

        Args:
            data: The job data to enqueue
            queue: Optional queue name to override the default
            delay: Optional delay in seconds before the job becomes available
        """
        try:
            template_args = {"queue": queue, "config": config.get("configurable", {})}

            queue_name = self._get_template(self.queue).format(**template_args)

            queue_provider = SupabaseQueueProvider()
            job_id = queue_provider.send(queue_name=queue_name, data=data, delay=delay)

            return {"job_id": job_id, "queue": queue_name, "status": "enqueued"}

        except Exception as e:
            return {"error": str(e), "status": "failed"}
