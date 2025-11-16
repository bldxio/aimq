import asyncio
import threading
from typing import Any, Optional

from .config import config
from .logger import Logger


class RealtimeWakeupService:
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
        self._url = url
        self._key = key
        self._worker_name = worker_name
        self._queues = queues
        self._channel_name = channel_name or config.supabase_realtime_channel
        self._event_name = event_name or config.supabase_realtime_event
        self._logger = logger or Logger()

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._shutdown = threading.Event()
        self._worker_events: set[threading.Event] = set()
        self._lock = threading.Lock()

        self._client: Optional[Any] = None
        self._channel: Optional[Any] = None
        self._connected = threading.Event()

    def start(self) -> None:
        """Start the realtime service in a background thread."""
        if self._thread is not None and self._thread.is_alive():
            self._logger.warning("Realtime service already running")
            return

        self._shutdown.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name=f"RealtimeWakeup-{self._worker_name}",
            daemon=True,
        )
        self._thread.start()
        self._logger.info(
            f"Realtime service started for worker '{self._worker_name}' on channel '{self._channel_name}'"
        )

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the realtime service gracefully.

        Args:
            timeout: Maximum time to wait for shutdown (seconds)
        """
        if self._thread is None or not self._thread.is_alive():
            return

        self._logger.info("Stopping realtime service...")
        self._shutdown.set()

        # Wait for the thread to finish (it will exit when shutdown flag is set)
        self._thread.join(timeout=timeout)

        if self._thread.is_alive():
            self._logger.warning(f"Realtime service did not stop within {timeout}s")
        else:
            self._logger.info("Realtime service stopped")

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

    def _run_loop(self) -> None:
        """Run the asyncio event loop in this thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._run())
        except Exception as e:
            self._logger.error(f"Realtime service crashed: {e}", {"error_type": type(e).__name__})
        finally:
            # Cancel all remaining tasks before closing the loop
            try:
                pending = asyncio.all_tasks(self._loop)
                if pending:
                    self._logger.debug(f"Cancelling {len(pending)} pending task(s)")
                    for task in pending:
                        task.cancel()

                    # Give tasks a moment to cancel
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception as e:
                self._logger.debug(f"Error cancelling tasks: {e}")

            self._loop.close()
            self._loop = None

    async def _run(self) -> None:
        """Main async loop with reconnection logic."""
        backoff = 1.0
        max_backoff = 60.0

        try:
            while not self._shutdown.is_set():
                try:
                    await self._connect()
                    self._connected.set()
                    backoff = 1.0

                    await self._listen()

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._connected.clear()
                    self._logger.error(
                        f"Realtime connection error: {e}",
                        {"error_type": type(e).__name__, "backoff": backoff},
                    )

                    if not self._shutdown.is_set():
                        await asyncio.sleep(min(backoff, max_backoff))
                        backoff *= 2
        except asyncio.CancelledError:
            # Expected during shutdown
            pass
        finally:
            # Always disconnect on exit
            await self._disconnect()
            self._logger.debug("Realtime service _run() completed")

    async def _connect(self) -> None:
        """Connect to Supabase Realtime and subscribe to channels."""
        try:
            from supabase import acreate_client
        except ImportError:
            self._logger.error(
                "supabase package not installed or doesn't support async client. "
                "Install with: uv add supabase"
            )
            raise

        self._logger.info(f"Connecting to Supabase Realtime channel '{self._channel_name}'...")

        self._client = await acreate_client(self._url, self._key)
        self._channel = self._client.channel(self._channel_name)

        # Register broadcast callback
        self._channel.on_broadcast(self._event_name, self._handle_job_notification)

        # Subscribe to channel first
        await self._channel.subscribe()

        # Track presence after subscribing
        await self._channel.track(
            {
                "worker": self._worker_name,
                "queues": self._queues,
                "status": "idle",
                "current_jobs": {},
            }
        )

        self._logger.info(
            f"Connected to Realtime channel '{self._channel_name}', listening for '{self._event_name}' events"
        )

    async def _listen(self) -> None:
        """Keep the connection alive and handle events."""
        while not self._shutdown.is_set():
            await asyncio.sleep(1)

    async def _disconnect(self) -> None:
        """Disconnect from Supabase Realtime."""
        if self._channel:
            try:
                # Unsubscribe with timeout to avoid hanging
                await asyncio.wait_for(self._channel.unsubscribe(), timeout=2.0)
                self._logger.debug("Unsubscribed from Realtime channel")
            except asyncio.TimeoutError:
                self._logger.warning("Unsubscribe timed out, forcing disconnect")
            except Exception as e:
                self._logger.debug(f"Error unsubscribing from channel: {e}")

        if self._client:
            try:
                # Close the client
                await asyncio.wait_for(self._client.close(), timeout=2.0)
                self._logger.debug("Closed Realtime client")
            except asyncio.TimeoutError:
                self._logger.warning("Client close timed out")
            except Exception as e:
                self._logger.debug(f"Error closing Realtime client: {e}")

        self._client = None
        self._channel = None
        self._connected.clear()

    def _handle_job_notification(self, broadcast_payload: Any) -> None:
        """Handle job notification broadcast.

        Args:
            broadcast_payload: BroadcastPayload with event and payload attributes
                payload format: {"queue": "incoming-messages", "job_id": 12345}

        Only wakes workers if the notification is for a queue this worker monitors.
        This prevents unnecessary wake-ups when multiple workers monitor different queues.
        """
        # Extract the actual payload dict from BroadcastPayload
        payload = (
            broadcast_payload.payload
            if hasattr(broadcast_payload, "payload")
            else broadcast_payload
        )

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

    @property
    def is_connected(self) -> bool:
        """Check if the service is connected to Realtime."""
        return self._connected.is_set()
