import json
import re
from typing import Any, Dict, List, Optional

from ..clients.supabase import supabase
from ..config import config
from ..job import Job
from .base import QueueNotFoundError, QueueProvider


class SupabaseQueueProvider(QueueProvider):
    """Supabase implementation of QueueProvider.

    Provides queue operations via Supabase pgmq_public RPC functions.
    Includes Supabase-specific features like realtime triggers for instant worker wake-up.
    """

    def _rpc(self, method: str, params: dict) -> Any:
        """Execute a Supabase RPC call to pgmq_public schema."""
        try:
            result = supabase.client.schema("pgmq_public").rpc(method, params).execute()
            return result.data
        except Exception as e:
            # Check for PostgreSQL error in error message or details
            error_msg = str(e)
            if "42P01" in error_msg:  # Check for table/relation not found error
                raise QueueNotFoundError(
                    f"Queue '{params.get('queue_name')}' does not exist. Please create the queue before using it."
                )

            # WORKAROUND: PostgREST sometimes fails to parse jsonb responses from functions
            # that use dynamic SQL (execute format). The function executes successfully but
            # PostgREST returns "JSON could not be generated" with the actual result in details.
            # Extract and parse the result from the error details.
            if "'code': 200" in error_msg or "'code': '200'" in error_msg:
                # Try to extract JSON from the details field
                # Format: 'details': 'b\'{"success": true, ...}\''
                match = re.search(r"'details':\s*'b\\'(.+?)\\'", error_msg)
                if match:
                    try:
                        json_str = match.group(1).replace("\\'", "'")
                        return json.loads(json_str)
                    except (json.JSONDecodeError, AttributeError):
                        pass  # Fall through to raise original error

            raise

    def send(self, queue_name: str, data: dict[str, Any], delay: int | None = None) -> int:
        params: dict[str, Any] = {"queue_name": queue_name, "message": data}
        if delay is not None:
            params["sleep_seconds"] = delay

        result = self._rpc("send", params)
        return result[0]

    def send_batch(
        self, queue_name: str, data_list: list[dict[str, Any]], delay: int | None = None
    ) -> list[int]:
        params: dict[str, Any] = {"queue_name": queue_name, "messages": data_list}
        if delay is not None:
            params["sleep_seconds"] = delay

        result = self._rpc("send_batch", params)
        return result

    def read(self, queue_name: str, timeout: int, count: int) -> List[Job]:
        data = self._rpc("read", {"queue_name": queue_name, "sleep_seconds": timeout, "n": count})

        return [Job.from_response(job, queue=queue_name) for job in data]

    def pop(self, queue_name: str) -> Job | None:
        data = self._rpc("pop", {"queue_name": queue_name})

        return Job.from_response(data[0], queue=queue_name, popped=True) if data else None

    def archive(self, queue_name: str, job_or_id: int | Job) -> bool:
        msg_id = job_or_id.id if isinstance(job_or_id, Job) else job_or_id
        data = self._rpc("archive", {"queue_name": queue_name, "message_id": msg_id})

        return bool(data)

    def delete(self, queue_name: str, job_or_id: int | Job) -> bool:
        msg_id = job_or_id.id if isinstance(job_or_id, Job) else job_or_id
        data = self._rpc("delete", {"queue_name": queue_name, "message_id": msg_id})

        return bool(data)

    # =========================================================================
    # Queue Management (Supabase-specific)
    # =========================================================================

    def create_queue(
        self,
        queue_name: str,
        with_realtime: bool = True,
        channel_name: Optional[str] = None,
        event_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new pgmq queue with optional realtime trigger.

        Args:
            queue_name: Name of the queue to create
            with_realtime: Whether to attach realtime trigger (default: True)
            channel_name: Realtime channel name (default: from config)
            event_name: Realtime event name (default: from config)

        Returns:
            Dict with queue details and realtime configuration:
            {
                "success": true,
                "queue_name": "my-queue",
                "realtime_enabled": true,
                "channel": "worker-wakeup",
                "event": "job_enqueued"
            }

        Raises:
            Exception: If queue creation fails

        Example:
            >>> provider = SupabaseQueueProvider()
            >>> result = provider.create_queue("my-queue")
            >>> print(result["queue_name"])
            my-queue
        """
        params = {
            "queue_name": queue_name,
            "with_realtime": with_realtime,
            "channel_name": channel_name or config.supabase_realtime_channel,
            "event_name": event_name or config.supabase_realtime_event,
        }

        return self._rpc("create_queue", params)

    def list_queues(self) -> List[Dict[str, Any]]:
        """List all pgmq queues with their realtime status and metrics.

        Returns:
            List of queue objects:
            [
                {
                    "queue_name": "my-queue",
                    "realtime_enabled": true,
                    "queue_length": 5,
                    "total_messages": 100,
                    "newest_msg_age_sec": 10,
                    "oldest_msg_age_sec": 3600,
                    "scrape_time": "2025-11-19T12:00:00Z"
                },
                ...
            ]

        Raises:
            Exception: If listing fails

        Example:
            >>> provider = SupabaseQueueProvider()
            >>> queues = provider.list_queues()
            >>> for queue in queues:
            ...     print(f"{queue['queue_name']}: {queue['queue_length']} messages")
        """
        result = self._rpc("list_queues", {})

        if isinstance(result, dict) and "queues" in result:
            return result["queues"]

        return []

    def enable_queue_realtime(
        self,
        queue_name: str,
        channel_name: Optional[str] = None,
        event_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enable realtime trigger on an existing pgmq queue.

        This "upgrades" a standard pgmq queue to an AIMQ queue with instant
        worker wake-up via Supabase Realtime.

        Args:
            queue_name: Name of the queue to upgrade
            channel_name: Realtime channel name (default: from config)
            event_name: Realtime event name (default: from config)

        Returns:
            Dict with operation result:
            {
                "success": true,
                "message": "Realtime enabled for queue: my-queue",
                "queue_name": "my-queue",
                "realtime_enabled": true,
                "channel": "worker-wakeup",
                "event": "job_enqueued"
            }

            Or if queue doesn't exist:
            {
                "success": false,
                "error": "Queue does not exist: my-queue"
            }

        Raises:
            Exception: If operation fails

        Example:
            >>> provider = SupabaseQueueProvider()
            >>> result = provider.enable_queue_realtime("existing-queue")
            >>> if result["success"]:
            ...     print(f"Upgraded: {result['queue_name']}")
        """
        params = {
            "queue_name": queue_name,
            "channel_name": channel_name or config.supabase_realtime_channel,
            "event_name": event_name or config.supabase_realtime_event,
        }

        return self._rpc("enable_queue_realtime", params)
