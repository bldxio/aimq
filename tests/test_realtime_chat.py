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

    @patch("aimq.clients.supabase.supabase")
    def test_wait_for_message_received(self, mock_supabase):
        """Test waiting for message that arrives."""
        message_id = "test_msg_123"
        job_id = 12345

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [
            {
                "msg_id": job_id,
                "message": {"message_id": message_id, "content": "test response"},
            }
        ]
        mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
            mock_response
        )

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
        )

        # Simulate message arrival in background thread
        def send_message():
            time.sleep(0.1)
            listener._handle_broadcast({"queue": "outgoing-messages", "job_id": job_id})

        thread = threading.Thread(target=send_message)
        thread.start()

        # Wait for message
        result = listener.wait_for_message(message_id, timeout=2.0)

        thread.join()

        assert result is not None
        assert result["message_id"] == message_id

    @patch("aimq.clients.supabase.supabase")
    def test_handle_message_notification(self, mock_supabase):
        """Test handling message notification."""
        callback_called = False
        received_payload = None

        def on_message(payload):
            nonlocal callback_called, received_payload
            callback_called = True
            received_payload = payload

        job_id = 12345
        message_id = "test_123"

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [
            {
                "msg_id": job_id,
                "message": {"message_id": message_id, "content": "test"},
            }
        ]
        mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
            mock_response
        )

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
            on_message=on_message,
        )

        listener._handle_broadcast({"queue": "outgoing-messages", "job_id": job_id})

        assert callback_called
        assert received_payload["message_id"] == message_id
        assert received_payload["message"]["content"] == "test"

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

        # Send notification for wrong queue
        listener._handle_broadcast({"queue": "other-queue", "job_id": 12345})

        # Callback should not be called for wrong queue
        assert not callback_called

    @patch("aimq.clients.supabase.supabase")
    def test_handle_message_notification_callback_error(self, mock_supabase):
        """Test handling callback errors gracefully."""

        def on_message(payload):
            raise Exception("Callback error")

        job_id = 12345

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [
            {
                "msg_id": job_id,
                "message": {"message_id": "test_123", "content": "test"},
            }
        ]
        mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
            mock_response
        )

        listener = RealtimeChatListener(
            url="https://test.supabase.co",
            key="test-key",
            on_message=on_message,
        )

        # Should not crash
        listener._handle_broadcast({"queue": "outgoing-messages", "job_id": job_id})

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
            "job_id": 12345,
        }

        broadcast_payload = MockBroadcastPayload(payload_data)

        # Should extract payload from BroadcastPayload object via wrapper
        # This tests the base class _handle_broadcast_wrapper method
        listener._handle_broadcast_wrapper(broadcast_payload)

        # Should not crash (no Supabase mock needed since no job_id fetch happens)

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
