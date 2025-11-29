"""Tests for Queue visibility timeout behavior.

Verifies that:
1. Queue uses full timeout as visibility timeout (not capped at 5s)
2. Queue with timeout=0 uses pop() instead of read()
"""

from unittest.mock import MagicMock

import pytest
from langchain_core.runnables import RunnableLambda

from aimq.queue import Queue


class TestQueueVisibilityTimeout:
    """Test visibility timeout configuration in Queue."""

    @pytest.fixture
    def simple_runnable(self):
        """Create a simple runnable for testing."""
        return RunnableLambda(lambda x: {"result": "success"})

    def test_queue_uses_full_timeout_not_capped(self, simple_runnable):
        """Test that queue uses full timeout value, not capped at 5 seconds."""
        # Create mock provider
        mock_provider = MagicMock()
        mock_provider.read.return_value = []

        # Create queue with 900-second timeout
        queue = Queue(
            runnable=simple_runnable,
            timeout=900,
        )
        queue.provider = mock_provider

        # Call next() to trigger read
        queue.next()

        # Verify provider.read() was called with full timeout (900), not 5
        mock_provider.read.assert_called_once_with(queue.name, 900, 1)
        mock_provider.pop.assert_not_called()

    def test_queue_timeout_30_uses_full_value(self, simple_runnable):
        """Test that timeout=30 is used as-is, not capped."""
        mock_provider = MagicMock()
        mock_provider.read.return_value = []

        queue = Queue(
            runnable=simple_runnable,
            timeout=30,
        )
        queue.provider = mock_provider

        queue.next()

        # Should use 30, not min(30, 5)
        mock_provider.read.assert_called_once_with(queue.name, 30, 1)

    def test_queue_timeout_zero_uses_pop(self, simple_runnable):
        """Test that timeout=0 uses pop() instead of read()."""
        mock_provider = MagicMock()
        mock_provider.pop.return_value = None

        queue = Queue(
            runnable=simple_runnable,
            timeout=0,
        )
        queue.provider = mock_provider

        queue.next()

        # Should call pop, not read
        mock_provider.pop.assert_called_once_with(queue.name)
        mock_provider.read.assert_not_called()

    def test_queue_default_timeout_300(self, simple_runnable):
        """Test that default timeout is 300 seconds."""
        mock_provider = MagicMock()
        mock_provider.read.return_value = []

        queue = Queue(runnable=simple_runnable)
        queue.provider = mock_provider

        queue.next()

        # Default timeout should be 300
        mock_provider.read.assert_called_once_with(queue.name, 300, 1)

    def test_queue_timeout_field_description(self):
        """Test that timeout field has correct description."""
        from aimq.queue import Queue as QueueClass

        # Get the field description
        timeout_field = QueueClass.model_fields["timeout"]

        # Should mention visibility timeout
        assert "visibility timeout" in timeout_field.description.lower()
        assert "vt" in timeout_field.description.lower()

    def test_queue_timeout_large_values(self, simple_runnable):
        """Test that large timeout values are used without capping."""
        mock_provider = MagicMock()
        mock_provider.read.return_value = []

        # Test with very large timeout (1 hour = 3600 seconds)
        queue = Queue(
            runnable=simple_runnable,
            timeout=3600,
        )
        queue.provider = mock_provider

        queue.next()

        # Should use full 3600, not capped
        mock_provider.read.assert_called_once_with(queue.name, 3600, 1)

    def test_worker_assign_configures_timeout(self):
        """Test that Worker.assign() properly configures queue timeout."""
        from aimq.worker import Worker

        worker = Worker()
        runnable = RunnableLambda(lambda x: x)

        # Assign with custom timeout
        worker.assign(runnable, queue="test", timeout=900)

        # Check that queue was created with correct timeout
        assert "test" in worker.queues
        assert worker.queues["test"].timeout == 900

    def test_failed_job_raises_exception_not_archived(self, simple_runnable):
        """Test that failed jobs raise exceptions and don't get archived immediately."""
        from aimq.job import Job

        # Create a runnable that always fails
        failing_runnable = RunnableLambda(lambda x: 1 / 0)  # ZeroDivisionError

        # Create mock provider
        mock_provider = MagicMock()

        # Mock a job
        job_data = {
            "msg_id": 1,
            "read_ct": 1,
            "enqueued_at": "2024-01-01T00:00:00Z",
            "vt": "2024-01-01T00:05:00Z",
            "message": {"test": "data"},
        }
        job = Job.from_response(job_data, queue="test")
        mock_provider.read.return_value = [job]

        queue = Queue(
            runnable=failing_runnable,
            timeout=15,  # 15-second visibility timeout
            max_retries=5,
        )
        queue.provider = mock_provider

        # Process the job - should fail and re-raise
        with pytest.raises(ZeroDivisionError):
            queue.work()

        # Job should NOT be archived or deleted
        # (it stays in queue, invisible for 15 seconds)
        mock_provider.archive.assert_not_called()
        mock_provider.delete.assert_not_called()
