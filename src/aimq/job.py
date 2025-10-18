from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, PrivateAttr


class Job(BaseModel):
    """A job in the queue.

    This class represents a job that can be processed by a worker. Each job has
    a unique identifier, metadata about its processing status, and the actual
    data to be processed.

    Attributes:
        id: Unique identifier for the job (aliased as msg_id)
        attempt: Number of times this job has been attempted (aliased as read_ct)
        updated_at: Timestamp of last update
        enqueued_at: Timestamp when job was added to queue
        expires_at: Timestamp when job expires (aliased as vt)
        data: The actual job data to process (aliased as message)
        status: Current status of the job
        queue: Optional name of the queue this job belongs to
    """

    id: int = Field(alias="msg_id")
    attempt: int = Field(alias="read_ct")
    updated_at: datetime = Field(default_factory=datetime.now)
    enqueued_at: datetime
    expires_at: datetime = Field(alias="vt")
    data: dict[str, Any] = Field(alias="message")
    status: str = Field(default="pending")
    queue: Optional[str] = Field(default=None)
    _popped: bool = PrivateAttr(default=False)

    @property
    def popped(self) -> bool:
        """Check if the job has been popped from the queue.

        Returns:
            bool: True if the job has been popped, False otherwise
        """
        return self._popped

    @classmethod
    def from_response(
        cls, response_data: dict, queue: Optional[str] = None, popped: bool = False
    ) -> "Job":
        """Create a Job instance from API response data.

        Args:
            response_data: Raw response data from the API
            queue: Optional name of the queue this job belongs to
            popped: Whether this job has been popped from the queue

        Returns:
            Job: A new Job instance initialized with the response data
        """
        job = cls(**response_data)
        job._popped = popped
        job.queue = queue
        return job
