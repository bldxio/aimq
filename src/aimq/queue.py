from datetime import datetime
from typing import Any, Callable, List

from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .config import config
from .job import Job
from .logger import Logger
from .providers import QueueProvider, SupabaseQueueProvider


class QueueNotFoundError(Exception):
    """Raised when attempting to access a queue that does not exist."""

    pass


class Queue(BaseModel):
    """A queue class that manages workflows with configurable parameters."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    runnable: Any = Field(description="Langchain runnable or runnable-like object to process jobs")

    @field_validator("runnable")
    @classmethod
    def validate_runnable(cls, v):
        """Validate that the runnable has the required methods (duck typing).

        Accepts:
        - Instances of langchain_core.runnables.Runnable
        - Any object with invoke() and stream() methods (duck typing)

        This allows both native Runnables and wrapper classes that delegate
        to Runnables (like BaseAgent, BaseWorkflow, _AgentBase, _WorkflowBase).
        """
        # Check if it's a proper Runnable instance
        if isinstance(v, Runnable):
            return v

        # Check for duck-typing: must have invoke() and stream() methods
        if not (hasattr(v, "invoke") and callable(getattr(v, "invoke"))):
            raise ValueError(f"runnable must have an 'invoke' method, got {type(v).__name__}")
        if not (hasattr(v, "stream") and callable(getattr(v, "stream"))):
            raise ValueError(f"runnable must have a 'stream' method, got {type(v).__name__}")

        return v

    timeout: int = Field(
        default=300,
        description="Visibility timeout in seconds (vt). Controls how long jobs stay invisible after being read, determining retry interval for failed jobs. If 0, messages will be popped (immediately deleted) instead of read.",
    )
    tags: List[str] = Field(
        default_factory=list, description="List of tags associated with the queue"
    )
    worker_name: str = Field(default="peon", description="Name of the worker processing this queue")
    delay: int = Field(default=0, ge=0, description="Delay in seconds between processing tasks")
    delete_on_finish: bool = Field(
        default=False,
        description="Whether to delete (True) or archive (False) jobs after processing",
    )
    max_retries: int | None = Field(
        default=None,
        description="Maximum retry attempts for failed jobs. None uses config default. 0 = no retries.",
    )
    dlq: str | None = Field(
        default=None,
        description="Dead-letter queue name. Failed jobs exceeding max_retries are sent here.",
    )
    on_error: Callable[[Job, Exception], None] | None = Field(
        default=None,
        description="Optional callback for custom error handling. Called before DLQ/archive.",
    )
    provider: QueueProvider = Field(
        default_factory=SupabaseQueueProvider, description="Queue provider implementation"
    )
    logger: Logger = Field(
        default_factory=Logger, description="Logger instance to use for queue events"
    )

    @property
    def name(self) -> str:
        """Get the queue name from the runnable."""
        if hasattr(self.runnable, "name") and self.runnable.name:
            return str(self.runnable.name)
        if hasattr(self.runnable, "__name__"):
            return str(self.runnable.__name__)
        return "unnamed_queue"

    def send(self, data: dict[str, Any], delay: int | None = None) -> int:
        """Add a message to the queue.

        Args:
            data: Data payload to send
            delay: Optional delay in seconds before the message becomes visible

        Returns:
            int: The ID of the added message
        """
        job_id = self.provider.send(self.name, data, delay)
        self.logger.info(f"Sent job {job_id} to queue {self.name}", data)
        return job_id

    def send_batch(self, data_list: list[dict[str, Any]], delay: int | None = None) -> List[int]:
        """Add a batch of messages to the queue.

        Args:
            data_list: List of data payloads to send
            delay: Optional delay in seconds before the messages become visible

        Returns:
            List[int]: List of IDs of added messages
        """
        job_ids = self.provider.send_batch(self.name, data_list, delay)
        self.logger.info(f"Sent batch of {len(job_ids)} jobs to queue {self.name}")
        return job_ids

    def next(self) -> Job | None:
        """Check for new jobs in the queue.

        Returns:
            Optional[Job]: Next job if available, None otherwise
        """
        try:
            if self.timeout == 0:
                job = self.provider.pop(self.name)
            else:
                # Use full timeout as visibility timeout (vt)
                # pgmq's read() is non-blocking, timeout controls how long
                # jobs stay invisible before retry (not poll interval)
                jobs = self.provider.read(self.name, self.timeout, 1)
                job = jobs[0] if jobs else None
            if job:
                self.logger.debug(f"Retrieved job {job.id} from queue {self.name}")
            return job
        except QueueNotFoundError as e:
            self.logger.error(f"Queue {self.name} not found", str(e))
            return None

    def get_runtime_config(self, job: Job) -> RunnableConfig:
        """Create a runtime configuration for the job.

        Extracts LangGraph-specific configuration (thread_id) from job data
        and places it in config["configurable"] where LangGraph expects it.

        Args:
            job: The job to create configuration for

        Returns:
            RunnableConfig: Configuration for running the job
        """
        # Extract thread_id from job data for LangGraph checkpointing
        # Use job-provided thread_id or generate one from job ID
        configurable = {}
        if "thread_id" in job.data:
            configurable["thread_id"] = job.data["thread_id"]
        else:
            # Auto-generate thread_id for LangGraph workflows with checkpointing
            configurable["thread_id"] = f"job-{job.id}"

        return RunnableConfig(
            metadata={
                "worker": self.worker_name,
                "queue": self.name,
                "job": job.id,
            },
            tags=self.tags,
            configurable=configurable,
        )

    def run(self, job: Job) -> Any:
        """Process a specific job using the configured runnable.

        The thread_id is extracted from job data and placed in the runtime
        config, so it is filtered out of the input data to avoid duplication.
        """
        runtime_config = self.get_runtime_config(job)

        # Filter out thread_id from input data since it's now in config
        input_data = {k: v for k, v in job.data.items() if k != "thread_id"}

        return self.runnable.invoke(input_data, runtime_config)

    def send_to_dlq(self, job: Job, error: Exception) -> int:
        """Send a failed job to the dead-letter queue with error context.

        Args:
            job: The failed job
            error: The exception that caused the failure

        Returns:
            int: The ID of the DLQ message

        Raises:
            ValueError: If no DLQ is configured for this queue
        """
        if not self.dlq:
            raise ValueError(f"No DLQ configured for queue {self.name}")

        dlq_data = {
            "original_queue": self.name,
            "original_job_id": job.id,
            "attempt_count": job.attempt,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "job_data": job.data,
        }

        dlq_job_id = self.provider.send(self.dlq, dlq_data, delay=None)
        self.logger.warning(
            f"Sent job {job.id} to DLQ {self.dlq} after {job.attempt} attempts",
            dlq_data,
        )
        return dlq_job_id

    def work(self) -> Any:  # noqa: C901
        """Process jobs in the queue using the configured runnable.

        Implements retry limits and dead-letter queue handling:
        - Checks job.read_count against max_retries
        - Sends to DLQ if max retries exceeded
        - Always finishes job (archive/delete) in finally block
        - Calls on_error callback if configured

        Returns:
            Any: Result from processing each job, or None if no job or DLQ sent
        """
        job = self.next()
        if job is None:
            return None

        # Determine effective max_retries (use queue setting or config default)
        effective_max_retries = (
            self.max_retries if self.max_retries is not None else config.queue_max_retries
        )

        self.logger.info(
            f"Processing job {job.id} in queue {self.name} (attempt {job.attempt}/{effective_max_retries})",
            job.data,
        )

        try:
            result = self.run(job)
            self.logger.info(f"Job {job.id} processed successfully", result)
            self.finish(job)
            return result

        except Exception as e:
            # Log error with context
            self.logger.error(
                f"Error processing job {job.id} (attempt {job.attempt}/{effective_max_retries}): {str(e)}",
                {"job_data": job.data, "error_type": type(e).__name__},
            )

            # Call custom error handler if configured
            if self.on_error:
                try:
                    self.on_error(job, e)
                except Exception as handler_error:
                    self.logger.error(f"Error in on_error handler: {str(handler_error)}")

            # Check if max retries exceeded
            if job.attempt >= effective_max_retries:
                if self.dlq:
                    # Send to dead-letter queue
                    try:
                        self.send_to_dlq(job, e)
                        # Clean up original job after successful DLQ send
                        self.finish(job)
                        return None
                    except Exception as dlq_error:
                        self.logger.error(f"Failed to send job {job.id} to DLQ: {str(dlq_error)}")
                        # Don't finish job - let it retry
                        raise
                else:
                    # No DLQ configured - finish job to prevent infinite retries
                    self.logger.warning(
                        f"Job {job.id} exceeded max retries ({effective_max_retries}) with no DLQ configured. Archiving job.",
                        {"job_id": job.id, "attempts": job.attempt},
                    )
                    self.finish(job)
                    return None

            # Haven't exceeded max retries yet - re-raise to let job retry
            raise

    def finish(self, job: Job) -> bool:
        """Finish processing a job.

        If the job was popped, do nothing.
        Otherwise, either archive or delete based on delete_on_finish setting.

        Args:
            job: The job to finish

        Returns:
            bool: True if the operation was successful
        """
        if job._popped:
            self.logger.debug(f"Job {job.id} was popped, no cleanup needed")
            return True

        try:
            if self.delete_on_finish:
                self.provider.delete(self.name, job.id)
                self.logger.info(f"Deleted job {job.id} from queue {self.name}")
            else:
                self.provider.archive(self.name, job.id)
                self.logger.info(f"Archived job {job.id} from queue {self.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error finishing job {job.id}: {str(e)}")
            return False
