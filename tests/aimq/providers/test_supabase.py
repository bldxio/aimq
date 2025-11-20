from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from aimq.job import Job
from aimq.providers.supabase import QueueNotFoundError, SupabaseQueueProvider


@pytest.fixture
def mock_supabase():
    with patch("aimq.providers.supabase.supabase") as mock:
        # Create a mock for the execute chain
        execute_mock = Mock()
        execute_mock.execute.return_value.data = [{"mock": "data"}]

        # Set up the client chain
        mock.client.schema.return_value.rpc.return_value = execute_mock
        yield mock


@pytest.fixture
def provider():
    return SupabaseQueueProvider()


@pytest.fixture
def mock_job_data():
    now = datetime.now()
    return {
        "msg_id": 1,
        "message": {"test": "msg"},
        "read_ct": 0,
        "enqueued_at": now.isoformat(),
        "vt": (now + timedelta(hours=1)).isoformat(),
        "created_at": now.isoformat(),
    }


class TestSupabaseQueueProvider:
    """Tests for the Supabase Queue Provider implementation."""

    def test_send_message(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test sending a single message to the queue."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [123]
        data = {"test": "message"}

        # Execute
        msg_id = provider.send("test_queue", data)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "send", {"queue_name": "test_queue", "message": data}
        )
        assert msg_id == 123

    def test_send_message_with_delay(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test sending a message with delay."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [123]
        data = {"test": "message"}
        delay = 60

        # Execute
        msg_id = provider.send("test_queue", data, delay)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "send", {"queue_name": "test_queue", "message": data, "sleep_seconds": delay}
        )
        assert msg_id == 123

    def test_send_batch(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test sending multiple messages in batch."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [1, 2, 3]
        messages = [{"test": f"message{i}"} for i in range(3)]

        # Execute
        msg_ids = provider.send_batch("test_queue", messages)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "send_batch", {"queue_name": "test_queue", "messages": messages}
        )
        assert msg_ids == [1, 2, 3]

    def test_send_batch_with_delay(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test sending batch messages with delay."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [1, 2]
        messages = [{"test": "msg1"}, {"test": "msg2"}]
        delay = 30

        # Execute
        msg_ids = provider.send_batch("test_queue", messages, delay)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "send_batch", {"queue_name": "test_queue", "messages": messages, "sleep_seconds": delay}
        )
        assert msg_ids == [1, 2]

    def test_read_messages(self, provider: SupabaseQueueProvider, mock_supabase, mock_job_data):
        """Test reading messages from the queue."""
        # Setup
        mock_data = [mock_job_data, {**mock_job_data, "msg_id": 2}]
        mock_supabase.client.schema().rpc().execute.return_value.data = mock_data

        # Execute
        jobs = provider.read("test_queue", timeout=5, count=2)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "read", {"queue_name": "test_queue", "sleep_seconds": 5, "n": 2}
        )
        assert len(jobs) == 2
        assert all(isinstance(job, Job) for job in jobs)
        assert jobs[0].id == 1
        assert jobs[1].id == 2

    def test_pop_message(self, provider: SupabaseQueueProvider, mock_supabase, mock_job_data):
        """Test popping a message from the queue."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [mock_job_data]

        # Execute
        job = provider.pop("test_queue")

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with("pop", {"queue_name": "test_queue"})
        assert isinstance(job, Job)
        assert job.id == 1
        assert job.popped is True

    def test_pop_empty_queue(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test popping from an empty queue."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = []

        # Execute
        job = provider.pop("test_queue")

        # Verify
        assert job is None

    def test_archive_message(self, provider: SupabaseQueueProvider, mock_supabase, mock_job_data):
        """Test archiving a message."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [True]
        job = Job(**mock_job_data, queue="test_queue")

        # Execute
        result = provider.archive("test_queue", job)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "archive", {"queue_name": "test_queue", "message_id": 1}
        )
        assert result is True

    def test_archive_message_by_id(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test archiving a message using just the ID."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [True]

        # Execute
        result = provider.archive("test_queue", 123)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "archive", {"queue_name": "test_queue", "message_id": 123}
        )
        assert result is True

    def test_delete_message(self, provider: SupabaseQueueProvider, mock_supabase, mock_job_data):
        """Test deleting a message."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [True]
        job = Job(**mock_job_data, queue="test_queue")

        # Execute
        result = provider.delete("test_queue", job)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "delete", {"queue_name": "test_queue", "message_id": 1}
        )
        assert result is True

    def test_delete_message_by_id(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test deleting a message using just the ID."""
        # Setup
        mock_supabase.client.schema().rpc().execute.return_value.data = [True]

        # Execute
        result = provider.delete("test_queue", 123)

        # Verify
        mock_supabase.client.schema().rpc.assert_called_with(
            "delete", {"queue_name": "test_queue", "message_id": 123}
        )
        assert result is True

    def test_queue_not_found_error(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test handling of queue not found errors."""
        # Setup
        error_msg = 'relation "pgmq_public.some_table" does not exist (42P01)'
        mock_supabase.client.schema().rpc().execute.side_effect = Exception(error_msg)

        # Execute and verify
        with pytest.raises(QueueNotFoundError) as exc_info:
            provider.send("test_queue", {"test": "msg"})

        assert "Queue 'test_queue' does not exist" in str(exc_info.value)

    def test_general_error_handling(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test handling of general errors."""
        # Setup
        mock_supabase.client.schema().rpc().execute.side_effect = Exception("Some other error")

        # Execute and verify
        with pytest.raises(Exception) as exc_info:
            provider.send("test_queue", {"test": "msg"})

        assert str(exc_info.value) == "Some other error"


class TestQueueManagement:
    """Tests for queue management methods."""

    @patch("aimq.providers.supabase.config")
    def test_create_queue_with_realtime(
        self, mock_config, provider: SupabaseQueueProvider, mock_supabase
    ):
        """Test creating a queue with realtime enabled."""
        mock_config.supabase_realtime_channel = "worker-wakeup"
        mock_config.supabase_realtime_event = "job_enqueued"

        mock_supabase.client.schema().rpc().execute.return_value.data = {
            "success": True,
            "queue_name": "test-queue",
            "realtime_enabled": True,
            "channel": "worker-wakeup",
            "event": "job_enqueued",
        }

        result = provider.create_queue("test-queue")

        mock_supabase.client.schema.assert_called_with("pgmq_public")
        assert result["success"] is True
        assert result["queue_name"] == "test-queue"
        assert result["realtime_enabled"] is True

    @patch("aimq.providers.supabase.config")
    def test_create_queue_without_realtime(
        self, mock_config, provider: SupabaseQueueProvider, mock_supabase
    ):
        """Test creating a queue without realtime."""
        mock_config.supabase_realtime_channel = "worker-wakeup"
        mock_config.supabase_realtime_event = "job_enqueued"

        mock_supabase.client.schema().rpc().execute.return_value.data = {
            "success": True,
            "queue_name": "test-queue",
            "realtime_enabled": False,
        }

        result = provider.create_queue("test-queue", with_realtime=False)

        assert result["success"] is True
        assert result["realtime_enabled"] is False

    def test_list_queues_success(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test listing queues successfully."""
        mock_supabase.client.schema().rpc().execute.return_value.data = {
            "success": True,
            "queues": [
                {
                    "queue_name": "queue-1",
                    "realtime_enabled": True,
                    "queue_length": 5,
                    "total_messages": 100,
                },
                {
                    "queue_name": "queue-2",
                    "realtime_enabled": False,
                    "queue_length": 0,
                    "total_messages": 50,
                },
            ],
        }

        result = provider.list_queues()

        assert len(result) == 2
        assert result[0]["queue_name"] == "queue-1"
        assert result[0]["realtime_enabled"] is True
        assert result[0]["queue_length"] == 5
        assert result[1]["queue_name"] == "queue-2"
        assert result[1]["realtime_enabled"] is False

    def test_list_queues_empty(self, provider: SupabaseQueueProvider, mock_supabase):
        """Test listing queues when none exist."""
        mock_supabase.client.schema().rpc().execute.return_value.data = {
            "success": True,
            "queues": [],
        }

        result = provider.list_queues()

        assert result == []

    @patch("aimq.providers.supabase.config")
    def test_enable_queue_realtime_success(
        self, mock_config, provider: SupabaseQueueProvider, mock_supabase
    ):
        """Test enabling realtime on existing queue."""
        mock_config.supabase_realtime_channel = "worker-wakeup"
        mock_config.supabase_realtime_event = "job_enqueued"

        mock_supabase.client.schema().rpc().execute.return_value.data = {
            "success": True,
            "message": "Realtime enabled for queue: test-queue",
            "queue_name": "test-queue",
            "realtime_enabled": True,
        }

        result = provider.enable_queue_realtime("test-queue")

        assert result["success"] is True
        assert result["queue_name"] == "test-queue"
        assert result["realtime_enabled"] is True

    @patch("aimq.providers.supabase.config")
    def test_enable_queue_realtime_not_found(
        self, mock_config, provider: SupabaseQueueProvider, mock_supabase
    ):
        """Test enabling realtime on non-existent queue."""
        mock_config.supabase_realtime_channel = "worker-wakeup"
        mock_config.supabase_realtime_event = "job_enqueued"

        mock_supabase.client.schema().rpc().execute.return_value.data = {
            "success": False,
            "error": "Queue does not exist: nonexistent-queue",
        }

        result = provider.enable_queue_realtime("nonexistent-queue")

        assert result["success"] is False
        assert "does not exist" in result["error"]
