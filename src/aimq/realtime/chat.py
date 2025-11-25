"""Realtime listener for chat CLI instant message notifications."""

import threading
from typing import Callable, Optional

from ..logger import Logger
from .base import RealtimeBaseListener


class RealtimeChatListener(RealtimeBaseListener):
    """Manages Supabase Realtime connection for instant chat message notifications.

    Similar to RealtimeWakeupService but designed for CLI chat applications.
    Subscribes to broadcast channel for outgoing message notifications and
    invokes callbacks when messages arrive.

    Features:
    - Thread-safe message notification
    - Graceful reconnection with exponential backoff
    - Message filtering by message_id
    - No-op when Supabase not configured

    Args:
        url: Supabase project URL
        key: Supabase API key (anon or service key)
        channel_name: Realtime channel name (default from config)
        event_name: Broadcast event name (default from config)
        on_message: Callback function called when messages arrive
        logger: Logger instance for recording activities

    Example:
        >>> def handle_message(payload):
        ...     print(f"Got message: {payload}")
        >>> listener = RealtimeChatListener(
        ...     url="https://xxx.supabase.co",
        ...     key="eyJ...",
        ...     on_message=handle_message
        ... )
        >>> listener.start()
        >>> # Later: stop the listener
        >>> listener.stop()
    """

    def __init__(
        self,
        url: str,
        key: str,
        channel_name: Optional[str] = None,
        event_name: Optional[str] = None,
        on_message: Optional[Callable[[dict], None]] = None,
        logger: Optional[Logger] = None,
    ):
        super().__init__(url, key, channel_name, event_name, logger)
        self._on_message = on_message
        self._pending_messages: dict[str, dict] = {}

    def wait_for_message(self, message_id: str, timeout: float = 60.0) -> Optional[dict]:
        """Wait for a specific message to arrive via realtime.

        Args:
            message_id: Message ID to wait for
            timeout: Maximum time to wait (seconds)

        Returns:
            Message payload if received, None if timeout
        """
        event = threading.Event()

        with self._lock:
            self._pending_messages[message_id] = {"event": event, "payload": None}

        received = event.wait(timeout=timeout)

        with self._lock:
            result = self._pending_messages.pop(message_id, {}).get("payload")

        return result if received else None

    def _handle_broadcast(self, payload: dict) -> None:
        """Handle message notification broadcast.

        Args:
            payload: Broadcast payload with queue and job_id
                format: {"queue": "outgoing-messages", "job_id": 12345}
        """
        queue = payload.get("queue", "unknown")
        job_id = payload.get("job_id")

        self._logger.debug(f"Message notification received: queue={queue}, job_id={job_id}")

        if queue != "outgoing-messages":
            return

        # Fetch the full message from the queue using job_id
        if job_id:
            try:
                from ..clients.supabase import supabase

                response = (
                    supabase.client.schema("pgmq_public")
                    .rpc("read", {"queue_name": queue, "sleep_seconds": 0, "n": 100})
                    .execute()
                )

                if response.data:
                    for job in response.data:
                        if job.get("msg_id") == job_id:
                            msg = job.get("message", {})
                            message_id = msg.get("message_id")

                            # Build full payload with message data
                            full_payload = {
                                "queue": queue,
                                "job_id": job_id,
                                "message_id": message_id,
                                "message": msg,
                            }

                            if self._on_message:
                                try:
                                    self._on_message(full_payload)
                                except Exception as e:
                                    self._logger.error(f"Error in message callback: {e}")

                            if message_id:
                                with self._lock:
                                    if message_id in self._pending_messages:
                                        self._pending_messages[message_id]["payload"] = full_payload
                                        self._pending_messages[message_id]["event"].set()
                                        self._logger.debug(
                                            f"Resolved pending message: {message_id}"
                                        )
                            break

            except Exception as e:
                self._logger.error(f"Error fetching message for job_id {job_id}: {e}")
