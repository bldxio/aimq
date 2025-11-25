"""Base class for Supabase Realtime listeners."""

import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Optional

from ..config import config
from ..logger import Logger


class RealtimeBaseListener(ABC):
    """Base class for Supabase Realtime listeners.

    Handles common functionality:
    - Thread management with asyncio event loop
    - Connection/reconnection with exponential backoff
    - Broadcast channel subscription
    - Graceful shutdown

    Subclasses implement _handle_broadcast() to process messages.

    Args:
        url: Supabase project URL
        key: Supabase API key (anon or service key)
        channel_name: Realtime channel name
        event_name: Broadcast event name
        logger: Logger instance for recording activities

    Example:
        >>> class MyListener(RealtimeBaseListener):
        ...     async def _handle_broadcast(self, payload):
        ...         print(f"Got message: {payload}")
        >>> listener = MyListener(url, key, "my-channel", "my-event")
        >>> listener.start()
        >>> listener.stop()
    """

    def __init__(
        self,
        url: str,
        key: str,
        channel_name: Optional[str] = None,
        event_name: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        self._url = url
        self._key = key
        self._channel_name = channel_name or config.supabase_realtime_channel
        self._event_name = event_name or config.supabase_realtime_event
        self._logger = logger or Logger()

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._shutdown = threading.Event()
        self._lock = threading.Lock()

        self._client: Optional[Any] = None
        self._channel: Optional[Any] = None
        self._connected = threading.Event()

    def start(self) -> None:
        """Start the realtime listener in a background thread."""
        if self._thread is not None and self._thread.is_alive():
            self._logger.warning(f"{self.__class__.__name__} already running")
            return

        self._shutdown.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name=self.__class__.__name__,
            daemon=True,
        )
        self._thread.start()
        self._logger.info(f"{self.__class__.__name__} started on channel '{self._channel_name}'")

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the realtime listener gracefully.

        Args:
            timeout: Maximum time to wait for shutdown (seconds)
        """
        if self._thread is None or not self._thread.is_alive():
            return

        self._logger.info(f"Stopping {self.__class__.__name__}...")
        self._shutdown.set()

        self._thread.join(timeout=timeout)

        if self._thread.is_alive():
            self._logger.warning(f"{self.__class__.__name__} did not stop within {timeout}s")
        else:
            self._logger.info(f"{self.__class__.__name__} stopped")

    @property
    def is_connected(self) -> bool:
        """Check if the listener is connected to Realtime."""
        return self._connected.is_set()

    def _run_loop(self) -> None:
        """Run the asyncio event loop in this thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._run())
        except Exception as e:
            self._logger.error(
                f"{self.__class__.__name__} crashed: {e}",
                {"error_type": type(e).__name__},
            )
        finally:
            try:
                pending = asyncio.all_tasks(self._loop)
                if pending:
                    self._logger.debug(f"Cancelling {len(pending)} pending task(s)")
                    for task in pending:
                        task.cancel()

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
            pass
        finally:
            await self._disconnect()
            self._logger.debug(f"{self.__class__.__name__} _run() completed")

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

        self._channel.on_broadcast(self._event_name, self._handle_broadcast_wrapper)

        await self._channel.subscribe()

        self._logger.info(
            f"Connected to Realtime channel '{self._channel_name}', "
            f"listening for '{self._event_name}' events"
        )

    async def _listen(self) -> None:
        """Keep the connection alive and handle events."""
        while not self._shutdown.is_set():
            await asyncio.sleep(1)

    async def _disconnect(self) -> None:
        """Disconnect from Supabase Realtime."""
        if self._channel:
            try:
                await asyncio.wait_for(self._channel.unsubscribe(), timeout=2.0)
                self._logger.debug("Unsubscribed from Realtime channel")
            except asyncio.TimeoutError:
                self._logger.warning("Unsubscribe timed out, forcing disconnect")
            except Exception as e:
                self._logger.debug(f"Error unsubscribing from channel: {e}")

        if self._client:
            try:
                await asyncio.wait_for(self._client.close(), timeout=2.0)
                self._logger.debug("Closed Realtime client")
            except asyncio.TimeoutError:
                self._logger.warning("Client close timed out")
            except Exception as e:
                self._logger.debug(f"Error closing Realtime client: {e}")

        self._client = None
        self._channel = None
        self._connected.clear()

    def _handle_broadcast_wrapper(self, broadcast_payload: Any) -> None:
        """Wrapper to extract payload and call subclass handler.

        Args:
            broadcast_payload: BroadcastPayload from Supabase Realtime
        """
        try:
            payload = broadcast_payload["payload"]
        except (KeyError, TypeError):
            payload = broadcast_payload

        try:
            self._handle_broadcast(payload)
        except Exception as e:
            self._logger.error(f"Error in broadcast handler: {e}")

    @abstractmethod
    def _handle_broadcast(self, payload: dict) -> None:
        """Handle broadcast message (implemented by subclasses).

        Args:
            payload: Broadcast payload dict
        """
        pass
