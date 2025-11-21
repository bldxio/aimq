"""Tests for realtime chat listener."""

import asyncio
import threading
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from aimq.realtime import RealtimeChatListener


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase async client."""
    mock_client = Mock()  # Use regular Mock for client
    mock_channel = Mock()  # Use regular Mock for channel (not async)

    mock_client.channel = Mock(return_value=mock_channel)
    mock_channel.on_broadcast = Mock()
    mock_channel.subscribe = AsyncMock()
    mock_channel.unsubscribe = AsyncMock()
    mock_client.close = AsyncMock()

    return mock_client, mock_channel


class TestRealtimeChatListener:
    """Tests for RealtimeChatListener."""

    def test_init(self):
        """Test listener initialization."""
        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        assert listener._url == "https://test.supabase.co"
        assert listener._key == "test-key"
        assert listener._thread is None
        assert not listener.is_connected

    def test_start_stop(self):
        """Test starting and stopping listener."""
        with patch("supabase.acreate_client") as mock_create:
            mock_client = Mock()
            mock_channel = Mock()
            mock_channel.on_broadcast = Mock()
            mock_channel.subscribe = AsyncMock()
            mock_channel.unsubscribe = AsyncMock()
            mock_client.channel = Mock(return_value=mock_channel)
            mock_client.close = AsyncMock()
            mock_create.return_value = mock_client

            listener = RealtimeChatListener(
                url="https://test.supabase.co",
                key="test-key",
            )

            listener.start()
            time.sleep(0.1)  # Give thread time to start

            assert listener._thread is not None
            assert listener._thread.is_alive()

            listener.stop(timeout=2.0)

            assert not listener._thread.is_alive()

    def test_start_already_running(self):
        """Test starting listener when already running."""
        with patch("supabase.acreate_client") as mock_create:
            mock_client = Mock()
            mock_channel = Mock()
            mock_channel.on_broadcast = Mock()
            mock_channel.subscribe = AsyncMock()
            mock_channel.unsubscribe = AsyncMock()
            mock_client.channel = Mock(return_value=mock_channel)
            mock_client.close = AsyncMock()
            mock_create.return_value = mock_client

            listener = RealtimeChatListener(
                url="https://test.supabase.co",
                key="test-key",
            )

            listener.start()
            time.sleep(0.1)

            # Try to start again
            listener.start()  # Should log warning but not crash

            listener.stop(timeout=2.0)

    def test_stop_not_running(self):
        """Test stopping listener when not running."""
        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        # Should not crash
        listener.stop()

    def test_wait_for_message_timeout(self):
        """Test waiting for message with timeout."""
        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        # Wait for message that never arrives
        result = listener.wait_for_message("test_msg_123", timeout=0.5)

        assert result is None

    def test_wait_for_message_received(self):
        """Test waiting for message that arrives."""
        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        message_id = "test_msg_123"
        test_payload = {
            "queue": "outgoing-messages",
            "message_id": message_id,
            "message": {"content": "test response"},
        }

        # Simulate message arrival in background thread
        def send_message():
            time.sleep(0.1)
            listener._handle_message_notification(test_payload)

        thread = threading.Thread(target=send_message)
        thread.start()

        # Wait for message
        result = listener.wait_for_message(message_id, timeout=2.0)

        thread.join()

        assert result is not None
        assert result["message_id"] == message_id

    def test_handle_message_notification(self):
        """Test handling message notification."""
        callback_called = False
        received_payload = None

        def on_message(payload):
            nonlocal callback_called, received_payload
            callback_called = True
            received_payload = payload

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
            on_message=on_message,
        )

        payload = {
            "queue": "outgoing-messages",
            "message_id": "test_123",
            "message": {"content": "test"},
        }

        listener._handle_message_notification(payload)

        assert callback_called
        assert received_payload == payload

    def test_handle_message_notification_wrong_queue(self):
        """Test handling notification for wrong queue."""
        callback_called = False

        def on_message(payload):
            nonlocal callback_called
            callback_called = True

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
            on_message=on_message,
        )

        payload = {
            "queue": "other-queue",
            "message_id": "test_123",
        }

        listener._handle_message_notification(payload)

        # Callback should not be called for wrong queue
        assert not callback_called

    def test_handle_message_notification_callback_error(self):
        """Test handling callback errors gracefully."""

        def on_message(payload):
            raise Exception("Callback error")

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
            on_message=on_message,
        )

        payload = {
            "queue": "outgoing-messages",
            "message_id": "test_123",
        }

        # Should not crash
        listener._handle_message_notification(payload)

    def test_handle_message_notification_with_broadcast_payload(self):
        """Test handling BroadcastPayload object."""

        class MockBroadcastPayload:
            def __init__(self, payload):
                self.payload = payload

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        payload_data = {
            "queue": "outgoing-messages",
            "message_id": "test_123",
        }

        broadcast_payload = MockBroadcastPayload(payload_data)

        # Should extract payload from BroadcastPayload object
        listener._handle_message_notification(broadcast_payload)

        # Should not crash

    @pytest.mark.asyncio
    async def test_connect(self, mock_supabase_client):
        """Test connecting to Supabase Realtime."""
        mock_client, mock_channel = mock_supabase_client

        with patch("supabase.acreate_client", return_value=mock_client):
            listener = RealtimeChatListener(
                url="https://test.supabase.co",
                key="test-key",
            )

            await listener._connect()

            mock_client.channel.assert_called_once()
            mock_channel.on_broadcast.assert_called_once()
            mock_channel.subscribe.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect(self, mock_supabase_client):
        """Test disconnecting from Supabase Realtime."""
        mock_client, mock_channel = mock_supabase_client

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        listener._client = mock_client
        listener._channel = mock_channel

        await listener._disconnect()

        mock_channel.unsubscribe.assert_called_once()
        mock_client.close.assert_called_once()
        assert listener._client is None
        assert listener._channel is None

    @pytest.mark.asyncio
    async def test_disconnect_timeout(self):
        """Test disconnect with timeout."""
        mock_channel = AsyncMock()
        mock_channel.unsubscribe = AsyncMock(side_effect=asyncio.TimeoutError())

        mock_client = AsyncMock()
        mock_client.close = AsyncMock()

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        listener._client = mock_client
        listener._channel = mock_channel

        # Should handle timeout gracefully
        await listener._disconnect()

        assert listener._client is None
        assert listener._channel is None
