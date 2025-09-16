from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.runnables import Runnable, RunnableConfig
from .providers import QueueProvider, SupabaseQueueProvider
from .job import Job
from .logger import Logger
from aimq import config, job

class QueueNotFoundError(Exception):
    """Raised when attempting to access a queue that does not exist."""
    pass

class Queue(BaseModel):
    """A queue class that manages workflows with configurable parameters."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    runnable: Runnable = Field(description="Langchain runnable to process jobs")
    timeout: int = Field(default=300, description="Maximum time in seconds for a task to complete. If 0, messages will be popped instead of read.")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the queue")
    worker_name: str = Field(default="peon", description="Name of the worker processing this queue")
    delay: int = Field(default=0, ge=0, description="Delay in seconds between processing tasks")
    delete_on_finish: bool = Field(default=False, description="Whether to delete (True) or archive (False) jobs after processing")
    provider: QueueProvider = Field(default_factory=SupabaseQueueProvider, description="Queue provider implementation")
    logger: Logger = Field(default_factory=Logger, description="Logger instance to use for queue events")

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
        
        Args:
            job: The job to create configuration for
            
        Returns:
            RunnableConfig: Configuration for running the job
        """
        return RunnableConfig(
            metadata={
                "worker": self.worker_name,
                "queue": self.name, 
                "job": job.id, 
            }, 
            tags=self.tags,
            configurable=job.data
        )

    def run(self, job: Job) -> Any:
        """Process a  specific job using the configured runnable."""
        runtime_config = self.get_runtime_config(job)
        return self.runnable.invoke(job.data, runtime_config)

    def work(self) -> Any:
        """Process jobs in the queue using the configured runnable.
        
        Returns:
            Any: Result from processing each job
        """
        job = self.next()
        if job is None:
            return None
        
        self.logger.info(f"Processing job {job.id} in queue {self.name}", job.data)
        try:
            result = self.run(job)
            self.logger.info(f"Job {job.id} processed successfully", result)
            self.finish(job)
            return result
        except Exception as e:
            self.logger.error(f"Error processing job {job.id}: {str(e)}", job.data)
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
