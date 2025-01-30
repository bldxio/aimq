"""Supabase queue provider implementation for AIMQ.

This module provides a Supabase-based implementation of the QueueProvider interface,
utilizing Supabase's PostgreSQL-based message queue functionality (PGMQ) for reliable
message queuing and processing.
"""

from typing import Any, List, Sequence, cast

from ..clients.supabase import supabase
from ..job import Job
from .base import QueueNotFoundError, QueueProvider


class SupabaseQueueProvider(QueueProvider):
    """Supabase implementation of QueueProvider."""

    def _rpc(self, method: str, params: dict) -> list[Any]:
        """Execute a Supabase RPC call.

        Args:
            method: RPC method name.
            params: Method parameters.

        Returns:
            list[Any]: RPC result.

        Raises:
            QueueNotFoundError: If queue doesn't exist.
        """
        try:
            result = supabase.client.schema("pgmq_public").rpc(method, params).execute()
            return cast(list[Any], result.data)
        except Exception as e:
            # Check for PostgreSQL error in error message or details
            error_msg = str(e)
            if "42P01" in error_msg:  # Check for table/relation not found error
                raise QueueNotFoundError(
                    f"Queue '{params.get('queue_name')}' does not exist. "
                    "Please create the queue before using it."
                )
            raise

    def send(
        self, queue_name: str, data: dict[str, Any], delay: int | None = None
    ) -> int:
        """Send a message to the queue.

        Args:
            queue_name: Name of the queue.
            data: Message data.
            delay: Optional delay in seconds.

        Returns:
            int: Message ID.

        Raises:
            QueueNotFoundError: If queue doesn't exist.
            ValueError: If message could not be sent.
        """
        params = {"queue_name": queue_name, "message": data}
        if delay is not None:
            params["sleep_seconds"] = cast(str, delay)

        result = self._rpc("send", params)
        if not result:
            raise ValueError(f"Failed to send message to queue '{queue_name}'")

        msg_id = result[0]
        return int(msg_id) if isinstance(msg_id, (str, int)) else cast(int, msg_id)

    def send_batch(
        self,
        queue_name: str,
        data_list: Sequence[dict[str, Any]],
        delay: int | None = None,
    ) -> list[int]:
        """Send multiple messages to the queue.

        Args:
            queue_name: Name of the queue.
            data_list: List of message data.
            delay: Optional delay in seconds.

        Returns:
            list[int]: List of message IDs.

        Raises:
            QueueNotFoundError: If queue doesn't exist.
            ValueError: If any message could not be sent.
        """
        params = {"queue_name": queue_name, "messages": data_list}
        if delay is not None:
            params["sleep_seconds"] = cast(str, delay)

        result = self._rpc("send_batch", params)
        if not result or any(msg_id is None for msg_id in result):
            raise ValueError(
                f"Failed to send one or more messages to queue '{queue_name}'"
            )

        return [
            int(msg_id) if isinstance(msg_id, (str, int)) else cast(int, msg_id)
            for msg_id in result
        ]

    def read(self, queue_name: str, timeout: int, count: int) -> List[Job]:
        """Read messages from the queue without removing them.

        Args:
            queue_name: Name of the queue to read from.
            timeout: Time to wait for messages in seconds.
            count: Maximum number of messages to read.

        Returns:
            List[Job]: List of jobs read from the queue.

        Raises:
            QueueNotFoundError: If queue doesn't exist.
        """
        data = self._rpc(
            "read", {"queue_name": queue_name, "sleep_seconds": timeout, "n": count}
        )

        return [Job.from_response(job, queue=queue_name) for job in data]

    def pop(self, queue_name: str) -> Job | None:
        """Pop a single message from the queue.

        Args:
            queue_name: Name of the queue to pop from.

        Returns:
            Job | None: The popped job or None if queue is empty.

        Raises:
            QueueNotFoundError: If queue doesn't exist.
        """
        data = self._rpc("pop", {"queue_name": queue_name})

        return (
            Job.from_response(data[0], queue=queue_name, popped=True) if data else None
        )

    def archive(self, queue_name: str, job_or_id: int | Job) -> bool:
        """Archive a message in the queue.

        Args:
            queue_name: Name of the queue containing the message.
            job_or_id: Job object or message ID to archive.

        Returns:
            bool: True if message was archived, False otherwise.

        Raises:
            QueueNotFoundError: If queue doesn't exist.
        """
        msg_id = job_or_id.id if isinstance(job_or_id, Job) else job_or_id
        data = self._rpc("archive", {"queue_name": queue_name, "message_id": msg_id})

        return bool(data)

    def delete(self, queue_name: str, job_or_id: int | Job) -> bool:
        """Delete a message from the queue.

        Args:
            queue_name: Name of the queue containing the message.
            job_or_id: Job object or message ID to delete.

        Returns:
            bool: True if message was deleted, False otherwise.

        Raises:
            QueueNotFoundError: If queue doesn't exist.
        """
        msg_id = job_or_id.id if isinstance(job_or_id, Job) else job_or_id
        data = self._rpc("delete", {"queue_name": queue_name, "message_id": msg_id})

        return bool(data)
