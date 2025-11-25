"""Realtime listener for worker wake-up and presence tracking."""

import asyncio
import threading
from typing import Optional

from ..logger import Logger
from .base import RealtimeBaseListener


class RealtimeWakeupService(RealtimeBaseListener):
    """Manages Supabase Realtime connection for worker wake-up and presence.

    This service runs in a dedicated daemon thread with its own asyncio event loop.
    It subscribes to a broadcast channel for job notifications and reports worker
    presence (online/offline, idle/busy status).

    Features:
    - Thread-safe wake-up signaling to worker threads
    - Graceful reconnection with exponential backoff
    - Worker presence tracking for observability
    - No-op when Supabase not configured

    Args:
        url: Supabase project URL
        key: Supabase API key (anon or service key)
        worker_name: Name of this worker instance
        queues: List of queue names this worker processes
        channel_name: Realtime channel name (default from config)
        event_name: Broadcast event name (default from config)
        logger: Logger instance for recording activities

    Example:
        >>> service = RealtimeWakeupService(
        ...     url="https://xxx.supabase.co",
        ...     key="eyJ...",
        ...     worker_name="worker-1",
        ...     queues=["default", "priority"]
        ... )
        >>> service.start()
        >>> # Register worker thread
        >>> wake_event = threading.Event()
        >>> service.register_worker(wake_event)
        >>> # Later: stop the service
        >>> service.stop()
    """

    def __init__(
        self,
        url: str,
        key: str,
        worker_name: str,
        queues: list[str],
        channel_name: Optional[str] = None,
        event_name: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        super().__init__(url, key, channel_name, event_name, logger)
        self._worker_name = worker_name
        self._queues = queues
        self._worker_events: set[threading.Event] = set()

    def register_worker(self, wake_event: threading.Event) -> None:
        """Register a worker thread's wake-up event.

        Args:
            wake_event: Threading event to set when job notifications arrive
        """
        with self._lock:
            self._worker_events.add(wake_event)
            self._logger.debug(f"Registered worker event (total: {len(self._worker_events)})")

    def unregister_worker(self, wake_event: threading.Event) -> None:
        """Unregister a worker thread's wake-up event.

        Args:
            wake_event: Threading event to remove
        """
        with self._lock:
            self._worker_events.discard(wake_event)
            self._logger.debug(f"Unregistered worker event (remaining: {len(self._worker_events)})")

    def update_presence(self, status: str, current_jobs: Optional[dict[int, float]] = None) -> None:
        """Update worker presence status.

        This is thread-safe and can be called from worker threads.

        Args:
            status: Worker status ("idle" or "busy")
            current_jobs: Dict of job_id -> start_timestamp for jobs in progress.
                         None or empty dict when idle.
        """
        if not self._loop or not self._loop.is_running():
            return

        def _schedule_update():
            if self._loop:
                asyncio.run_coroutine_threadsafe(
                    self._update_presence_async(status, current_jobs), self._loop
                )

        self._loop.call_soon_threadsafe(_schedule_update)

    async def _connect(self) -> None:
        """Connect to Supabase Realtime and subscribe to channels."""
        await super()._connect()

        # Track presence after subscribing
        await self._channel.track(
            {
                "worker": self._worker_name,
                "queues": self._queues,
                "status": "idle",
                "current_jobs": {},
            }
        )

    def _handle_broadcast(self, payload: dict) -> None:
        """Handle job notification broadcast.

        Args:
            payload: Broadcast payload with queue and job_id
                format: {"queue": "incoming-messages", "job_id": 12345}

        Only wakes workers if the notification is for a queue this worker monitors.
        This prevents unnecessary wake-ups when multiple workers monitor different queues.
        """
        queue = payload.get("queue", "unknown")
        job_id = payload.get("job_id", "unknown")

        self._logger.debug(f"Job notification received: queue={queue}, job_id={job_id}")

        # Only wake if this worker monitors the queue
        if queue not in self._queues:
            self._logger.debug(
                f"Ignoring notification for queue '{queue}' (not monitored by this worker)"
            )
            return

        with self._lock:
            for event in list(self._worker_events):
                event.set()

        self._logger.debug(f"Woke {len(self._worker_events)} worker(s) for queue '{queue}'")

    async def _update_presence_async(
        self, status: str, current_jobs: Optional[dict[int, float]]
    ) -> None:
        """Update worker presence (async implementation)."""
        if not self._channel:
            return

        try:
            jobs = current_jobs or {}
            await self._channel.track(
                {
                    "worker": self._worker_name,
                    "queues": self._queues,
                    "status": status,
                    "current_jobs": jobs,
                    "job_count": len(jobs),
                }
            )
            job_ids = list(jobs.keys()) if jobs else []
            self._logger.debug(f"Updated presence: status={status}, jobs={job_ids}")
        except Exception as e:
            self._logger.warning(f"Failed to update presence: {e}")
