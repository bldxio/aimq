from abc import ABC, abstractmethod
from typing import Any, List

from ..job import Job


class QueueNotFoundError(Exception):
    """Raised when attempting to access a queue that does not exist."""

    pass


class QueueProvider(ABC):
    """Abstract base class for queue providers."""

    @abstractmethod
    def send(self, queue_name: str, data: dict[str, Any], delay: int | None = None) -> int:
        """Add a message to the queue.

        Returns:
            int: The ID of the added message
        """
        pass

    @abstractmethod
    def send_batch(
        self, queue_name: str, data_list: list[dict[str, Any]], delay: int | None = None
    ) -> list[int]:
        """Add a batch of messages to the queue.

        Returns:
            list[int]: The IDs of the added messages
        """
        pass

    @abstractmethod
    def read(self, queue_name: str, timeout: int, count: int) -> List[Job]:
        """Read messages from the queue."""
        pass

    @abstractmethod
    def pop(self, queue_name: str) -> Job | None:
        """Pop a message from the queue."""
        pass

    @abstractmethod
    def archive(self, queue_name: str, job_or_id: int | Job) -> bool:
        """Archive a message in the queue."""
        pass

    @abstractmethod
    def delete(self, queue_name: str, job_or_id: int | Job) -> bool:
        """Delete a message from the queue."""
        pass
