from datetime import datetime, timedelta
from typing import Any
from unittest.mock import Mock

import pytest
from langchain.schema.runnable import Runnable, RunnableConfig

from aimq.job import Job
from aimq.providers import QueueNotFoundError, QueueProvider
from aimq.queue import Queue


class MockRunnable(Runnable):
    """Mock runnable for testing."""

    name = "test_runnable"

    def invoke(self, input: Any, config: RunnableConfig | None = None, **kwargs: Any) -> Any:
        return input


@pytest.fixture
def mock_provider():
    provider = Mock(spec=QueueProvider)
    provider.send.return_value = 1
    provider.send_batch.return_value = [1, 2, 3]
    return provider


@pytest.fixture
def queue(mock_provider):
    return Queue(
        runnable=MockRunnable(),
        provider=mock_provider,
        worker_name="test_worker",
        tags=["test"],
        timeout=60,
    )


def create_test_job(
    job_id: int = 1, queue_name: str = "test_queue", data: dict | None = None, popped: bool = False
) -> Job:
    """Helper function to create a test job."""
    now = datetime.now()
    return Job.from_response(
        {
            "msg_id": job_id,
            "read_ct": 0,
            "enqueued_at": now,
            "vt": now + timedelta(hours=1),
            "message": data or {"key": "value"},
        },
        queue=queue_name,
        popped=popped,
    )


class TestQueue:
    """Test suite for Queue class."""

    def test_queue_initialization(self, queue):
        """Test queue initialization with default and custom parameters."""
        assert queue.worker_name == "test_worker"
        assert queue.tags == ["test"]
        assert queue.timeout == 60
        assert queue.delete_on_finish is False
        assert queue.delay == 0
        assert isinstance(queue.runnable, MockRunnable)

    def test_queue_name(self, queue):
        """Test queue name property."""
        assert queue.name == "test_runnable"

    def test_send_message(self, queue, mock_provider):
        """Test sending a single message to the queue."""
        data = {"key": "value"}
        job_id = queue.send(data)

        assert job_id == 1
        mock_provider.send.assert_called_once_with(queue.name, data, None)

    def test_send_batch(self, queue, mock_provider):
        """Test sending multiple messages to the queue."""
        data_list = [{"key": "value1"}, {"key": "value2"}, {"key": "value3"}]
        job_ids = queue.send_batch(data_list)

        assert job_ids == [1, 2, 3]
        mock_provider.send_batch.assert_called_once_with(queue.name, data_list, None)

    def test_next_with_timeout(self, queue, mock_provider):
        """Test retrieving next job with timeout."""
        mock_job = create_test_job()
        mock_provider.read.return_value = [mock_job]

        job = queue.next()
        assert job == mock_job
        mock_provider.read.assert_called_once_with(queue.name, queue.timeout, 1)

    def test_next_with_pop(self, queue, mock_provider):
        """Test retrieving next job with pop (timeout=0)."""
        queue.timeout = 0
        mock_job = create_test_job(popped=True)
        mock_provider.pop.return_value = mock_job

        job = queue.next()
        assert job == mock_job
        mock_provider.pop.assert_called_once_with(queue.name)

    def test_next_queue_not_found(self, queue, mock_provider):
        """Test handling of QueueNotFoundError in next()."""
        mock_provider.read.side_effect = QueueNotFoundError("Queue not found")

        with pytest.raises(QueueNotFoundError):
            queue.next()

    def test_get_runtime_config(self, queue):
        """Test creation of runtime configuration.

        The thread_id should be extracted from job data and placed in
        config["configurable"], or auto-generated if not present.
        """
        job = create_test_job()
        config = queue.get_runtime_config(job)

        expected_metadata = {"worker": queue.worker_name, "queue": queue.name, "job": job.id}
        assert isinstance(config, dict)
        assert config["metadata"] == expected_metadata
        assert config["tags"] == queue.tags
        # thread_id is auto-generated from job ID
        assert config["configurable"] == {"thread_id": f"job-{job.id}"}

    def test_get_runtime_config_with_thread_id(self, queue):
        """Test runtime config when thread_id is provided in job data."""
        job = create_test_job(data={"key": "value", "thread_id": "custom-thread-123"})
        config = queue.get_runtime_config(job)

        # thread_id should be extracted from job data
        assert config["configurable"] == {"thread_id": "custom-thread-123"}

    def test_run_job(self, queue):
        """Test running a specific job.

        The job data should be passed to the runnable, excluding thread_id
        which is moved to the config.
        """
        job_data = {"key": "value"}
        job = create_test_job(data=job_data)

        result = queue.run(job)
        # Result should match input (MockRunnable echoes input)
        assert result == job_data

    def test_run_job_with_thread_id(self, queue):
        """Test running a job with thread_id in data.

        The thread_id should be filtered out of the input data and
        placed in the config instead.
        """
        job_data = {"key": "value", "thread_id": "test-123"}
        job = create_test_job(data=job_data)

        result = queue.run(job)
        # Result should not include thread_id (it's filtered out)
        assert result == {"key": "value"}
        assert "thread_id" not in result

    def test_work_success(self, queue, mock_provider):
        """Test successful job processing."""
        job = create_test_job()
        mock_provider.read.return_value = [job]

        result = queue.work()
        assert result == {"key": "value"}
        mock_provider.read.assert_called_once()

    def test_work_no_jobs(self, queue, mock_provider):
        """Test work() when no jobs are available."""
        mock_provider.read.return_value = []

        result = queue.work()
        assert result is None

    def test_finish_popped_job(self, queue, mock_provider):
        """Test finishing a popped job."""
        job = create_test_job(popped=True)

        assert queue.finish(job) is True
        mock_provider.delete.assert_not_called()
        mock_provider.archive.assert_not_called()

    def test_finish_with_delete(self, queue, mock_provider):
        """Test finishing a job with delete_on_finish=True."""
        queue.delete_on_finish = True
        job = create_test_job()

        queue.finish(job)
        mock_provider.delete.assert_called_once_with(queue.name, job.id)

    def test_send_to_dlq_success(self, queue, mock_provider):
        """Test sending a job to dead-letter queue."""
        queue.dlq = "test_dlq"
        job = create_test_job()
        job.attempt = 3
        error = ValueError("Test error")

        mock_provider.send.return_value = 999

        dlq_job_id = queue.send_to_dlq(job, error)

        assert dlq_job_id == 999
        mock_provider.send.assert_called_once()
        call_args = mock_provider.send.call_args
        assert call_args[0][0] == "test_dlq"
        dlq_data = call_args[0][1]
        assert dlq_data["original_queue"] == queue.name
        assert dlq_data["original_job_id"] == job.id
        assert dlq_data["error_type"] == "ValueError"
        assert dlq_data["error_message"] == "Test error"

    def test_send_to_dlq_no_dlq_configured(self, queue):
        """Test sending to DLQ when no DLQ is configured raises ValueError."""
        job = create_test_job()
        error = ValueError("Test error")

        with pytest.raises(ValueError, match="No DLQ configured"):
            queue.send_to_dlq(job, error)

    def test_work_with_custom_error_handler(self, queue, mock_provider):
        """Test work with custom error handler."""
        error_handler = Mock()
        queue.on_error = error_handler
        queue.max_retries = 1

        job = create_test_job()
        mock_provider.read.return_value = [job]

        class FailingRunnable(Runnable):
            name = "failing"

            def invoke(
                self, input: Any, config: RunnableConfig | None = None, **kwargs: Any
            ) -> Any:
                raise RuntimeError("Test failure")

        queue.runnable = FailingRunnable()

        with pytest.raises(RuntimeError):
            queue.work()

        error_handler.assert_called_once()
        call_args = error_handler.call_args[0]
        assert call_args[0] == job
        assert isinstance(call_args[1], RuntimeError)

    def test_work_error_handler_exception(self, queue, mock_provider):
        """Test work when error handler itself raises an exception."""

        def bad_error_handler(job, error):
            raise ValueError("Handler error")

        queue.on_error = bad_error_handler
        queue.max_retries = 1

        job = create_test_job()
        mock_provider.read.return_value = [job]

        class FailingRunnable(Runnable):
            name = "failing"

            def invoke(
                self, input: Any, config: RunnableConfig | None = None, **kwargs: Any
            ) -> Any:
                raise RuntimeError("Test failure")

        queue.runnable = FailingRunnable()

        with pytest.raises(RuntimeError):
            queue.work()

    def test_work_max_retries_with_dlq(self, queue, mock_provider):
        """Test work sends to DLQ after max retries."""
        queue.max_retries = 2
        queue.dlq = "test_dlq"

        job = create_test_job()
        job.attempt = 2
        mock_provider.read.return_value = [job]
        mock_provider.send.return_value = 999

        class FailingRunnable(Runnable):
            name = "failing"

            def invoke(
                self, input: Any, config: RunnableConfig | None = None, **kwargs: Any
            ) -> Any:
                raise RuntimeError("Test failure")

        queue.runnable = FailingRunnable()

        result = queue.work()

        assert result is None
        mock_provider.send.assert_called_once()
        call_args = mock_provider.send.call_args[0]
        assert call_args[0] == "test_dlq"
        mock_provider.archive.assert_called_once_with(queue.name, job.id)

    def test_work_max_retries_no_dlq(self, queue, mock_provider):
        """Test work archives job after max retries when no DLQ configured."""
        queue.max_retries = 2

        job = create_test_job()
        job.attempt = 2
        mock_provider.read.return_value = [job]

        class FailingRunnable(Runnable):
            name = "failing"

            def invoke(
                self, input: Any, config: RunnableConfig | None = None, **kwargs: Any
            ) -> Any:
                raise RuntimeError("Test failure")

        queue.runnable = FailingRunnable()

        result = queue.work()

        assert result is None
        mock_provider.archive.assert_called_once_with(queue.name, job.id)

    def test_work_dlq_send_failure(self, queue, mock_provider):
        """Test work when DLQ send fails."""
        queue.max_retries = 2
        queue.dlq = "test_dlq"

        job = create_test_job()
        job.attempt = 2
        mock_provider.read.return_value = [job]
        mock_provider.send.side_effect = Exception("DLQ send failed")

        class FailingRunnable(Runnable):
            name = "failing"

            def invoke(
                self, input: Any, config: RunnableConfig | None = None, **kwargs: Any
            ) -> Any:
                raise RuntimeError("Test failure")

        queue.runnable = FailingRunnable()

        with pytest.raises(Exception, match="DLQ send failed"):
            queue.work()

        mock_provider.archive.assert_not_called()
