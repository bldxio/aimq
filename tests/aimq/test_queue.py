# type: ignore  # mypy is configured to ignore test files in pyproject.toml
"""Tests for the queue module.

This module contains test cases for the Queue class and its functionality,
including message handling, job processing, and provider interactions.
"""

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

    def invoke(self, input: Any, config: RunnableConfig | None = None) -> Any:
        """Process the input and return it unchanged.

        Args:
            input: The input to process.
            config: Optional runnable configuration.

        Returns:
            The unmodified input.
        """
        return input


@pytest.fixture
def mock_provider() -> Mock:
    """Create a mock queue provider for testing.

    Returns:
        A Mock object configured as a QueueProvider.
    """
    provider = Mock(spec=QueueProvider)
    provider.send.return_value = 1
    provider.send_batch.return_value = [1, 2, 3]
    provider.read.return_value = []
    provider.pop.return_value = None
    return provider


@pytest.fixture
def queue(mock_provider) -> Queue:
    """Create a test queue instance.

    Args:
        mock_provider: The mock provider fixture.

    Returns:
        A Queue instance configured for testing.
    """
    return Queue(
        runnable=MockRunnable(),
        provider=mock_provider,
        worker_name="test_worker",
        tags=["test"],
        timeout=60,
    )


def create_test_job(
    job_id: int = 1,
    queue_name: str = "test_queue",
    data: dict = None,
    popped: bool = False,
) -> Job:
    """Create a job for testing.

    Args:
        job_id: The ID for the job.
        queue_name: The name of the queue.
        data: Optional data for the job.
        popped: Whether the job has been popped.

    Returns:
        A Job instance configured for testing.
    """
    if data is None:
        data = {"test": "data"}

    now = datetime.now()
    return Job.from_response(
        {
            "msg_id": job_id,
            "read_ct": 0,
            "enqueued_at": now,
            "vt": now + timedelta(hours=1),
            "message": data,
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
        """Test creation of runtime configuration."""
        job = create_test_job()
        config = queue.get_runtime_config(job)

        expected_metadata = {
            "worker": queue.worker_name,
            "queue": queue.name,
            "job": job.id,
        }
        assert isinstance(config, dict)
        assert config["metadata"] == expected_metadata
        assert config["tags"] == queue.tags
        assert config["configurable"] == job.data

    def test_run_job(self, queue):
        """Test running a specific job."""
        job_data = {"key": "value"}
        job = create_test_job(data=job_data)

        result = queue.run(job)
        assert result == job_data

    def test_work_success(self, queue, mock_provider):
        """Test successful job processing."""
        job_data = {"key": "value"}
        job = create_test_job(data=job_data)
        mock_provider.read.return_value = [job]

        result = queue.work()
        assert result == job_data
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
