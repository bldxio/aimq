import threading
import time
from unittest.mock import AsyncMock, MagicMock, patch

from aimq.realtime import RealtimeWakeupService


class TestRealtimeWakeupService:
    """Tests for RealtimeWakeupService."""

    def test_init(self):
        """Test service initialization."""
        service = RealtimeWakeupService(
            url="https://test.supabase.co",
            key="test-key",
            worker_name="test-worker",
            queues=["queue1", "queue2"],
        )

        assert service._url == "https://test.supabase.co"
        assert service._key == "test-key"
        assert service._worker_name == "test-worker"
        assert service._queues == ["queue1", "queue2"]
        assert service._channel_name == "worker-wakeup"
        assert service._event_name == "job_enqueued"

    def test_register_unregister_worker(self):
        """Test worker event registration and unregistration."""
        service = RealtimeWakeupService(
            url="https://test.supabase.co",
            key="test-key",
            worker_name="test-worker",
            queues=["queue1"],
        )

        event1 = threading.Event()
        event2 = threading.Event()

        service.register_worker(event1)
        assert len(service._worker_events) == 1

        service.register_worker(event2)
        assert len(service._worker_events) == 2

        service.unregister_worker(event1)
        assert len(service._worker_events) == 1

        service.unregister_worker(event2)
        assert len(service._worker_events) == 0

    def test_handle_job_notification(self):
        """Test job notification handling wakes workers."""
        service = RealtimeWakeupService(
            url="https://test.supabase.co",
            key="test-key",
            worker_name="test-worker",
            queues=["queue1", "queue2"],
        )

        event1 = threading.Event()
        event2 = threading.Event()
        service.register_worker(event1)
        service.register_worker(event2)

        assert not event1.is_set()
        assert not event2.is_set()

        # Notification for monitored queue should wake workers
        service._handle_job_notification({"queue": "queue1", "job_id": 123})

        assert event1.is_set()
        assert event2.is_set()

    def test_handle_job_notification_filters_by_queue(self):
        """Test that notifications for unmonitored queues are ignored."""
        service = RealtimeWakeupService(
            url="https://test.supabase.co",
            key="test-key",
            worker_name="test-worker",
            queues=["queue1", "queue2"],  # Only monitors queue1 and queue2
        )

        event1 = threading.Event()
        service.register_worker(event1)

        assert not event1.is_set()

        # Notification for unmonitored queue should NOT wake workers
        service._handle_job_notification({"queue": "queue3", "job_id": 456})

        assert not event1.is_set()  # Should still be unset

        # Notification for monitored queue SHOULD wake workers
        service._handle_job_notification({"queue": "queue2", "job_id": 789})

        assert event1.is_set()  # Now it should be set

    def test_start_stop(self):
        """Test service start and stop."""
        with patch("supabase.acreate_client") as mock_create:

            async def async_noop(*args, **kwargs):
                return None

            mock_client = MagicMock()
            mock_client.close = AsyncMock()
            mock_channel = MagicMock()
            mock_channel.on_broadcast = MagicMock(return_value=None)
            mock_channel.subscribe = MagicMock(side_effect=async_noop)
            mock_channel.track = MagicMock(side_effect=async_noop)
            mock_channel.unsubscribe = MagicMock(side_effect=async_noop)
            mock_client.channel.return_value = mock_channel
            mock_create.return_value = mock_client

            service = RealtimeWakeupService(
                url="https://test.supabase.co",
                key="test-key",
                worker_name="test-worker",
                queues=["queue1"],
            )

            service.start()
            time.sleep(0.2)  # Give thread time to start

            assert service._thread is not None
            assert service._thread.is_alive()

            service.stop(timeout=2.0)

            assert not service._thread.is_alive()

    def test_graceful_fallback_on_import_error(self):
        """Test that service handles missing supabase package gracefully."""
        with patch(
            "supabase.acreate_client", side_effect=ImportError("No module named 'supabase'")
        ):
            service = RealtimeWakeupService(
                url="https://test.supabase.co",
                key="test-key",
                worker_name="test-worker",
                queues=["queue1"],
            )

            service.start()
            time.sleep(0.2)

            # Service should start but fail to connect
            assert service._thread is not None
            assert service._thread.is_alive()

            service.stop(timeout=2.0)

    def test_update_presence_thread_safe(self):
        """Test that update_presence can be called from any thread."""
        import time

        service = RealtimeWakeupService(
            url="https://test.supabase.co",
            key="test-key",
            worker_name="test-worker",
            queues=["queue1"],
        )

        # Should not crash when called before service starts
        service.update_presence("idle", {})
        service.update_presence("busy", {123: time.time(), 456: time.time()})

        # Should not crash when service is not running
        assert service._loop is None
        service.update_presence("idle", {})


class TestRealtimeIntegration:
    """Integration tests for realtime with worker."""

    def test_worker_thread_wakeup(self):
        """Test that worker thread can be woken by realtime event."""
        from collections import OrderedDict

        from aimq.logger import Logger
        from aimq.worker import WorkerThread

        service = RealtimeWakeupService(
            url="https://test.supabase.co",
            key="test-key",
            worker_name="test-worker",
            queues=["queue1"],
        )

        running = threading.Event()
        running.set()

        thread = WorkerThread(
            queues=OrderedDict(),
            logger=Logger(),
            running=running,
            idle_wait=10.0,  # Long wait to test wake-up
            realtime_service=service,
        )

        # Verify event is registered
        assert len(service._worker_events) == 1
        assert thread.wakeup_event in service._worker_events

        # Simulate wake-up
        thread.wakeup_event.set()
        assert thread.wakeup_event.is_set()

        # Cleanup
        running.clear()
        service.unregister_worker(thread.wakeup_event)
        assert len(service._worker_events) == 0

    def test_config_auto_enable(self):
        """Test that realtime is auto-enabled when Supabase configured."""
        import os

        from aimq.config import Config

        # Save original env vars
        orig_url = os.environ.get("SUPABASE_URL")
        orig_key = os.environ.get("SUPABASE_KEY")

        try:
            # Test with Supabase configured
            os.environ["SUPABASE_URL"] = "https://test.supabase.co"
            os.environ["SUPABASE_KEY"] = "test-key"
            config = Config()
            assert config.supabase_realtime_enabled is True

            # Test without Supabase
            os.environ["SUPABASE_URL"] = ""
            os.environ["SUPABASE_KEY"] = ""
            config = Config()
            assert config.supabase_realtime_enabled is False

            # Test with only URL
            os.environ["SUPABASE_URL"] = "https://test.supabase.co"
            os.environ["SUPABASE_KEY"] = ""
            config = Config()
            assert config.supabase_realtime_enabled is False

            # Test with only key
            os.environ["SUPABASE_URL"] = ""
            os.environ["SUPABASE_KEY"] = "test-key"
            config = Config()
            assert config.supabase_realtime_enabled is False

        finally:
            # Restore original env vars
            if orig_url is not None:
                os.environ["SUPABASE_URL"] = orig_url
            elif "SUPABASE_URL" in os.environ:
                del os.environ["SUPABASE_URL"]

            if orig_key is not None:
                os.environ["SUPABASE_KEY"] = orig_key
            elif "SUPABASE_KEY" in os.environ:
                del os.environ["SUPABASE_KEY"]
