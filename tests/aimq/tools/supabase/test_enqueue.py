# type: ignore  # mypy is configured to ignore test files in pyproject.toml
"""Tests for the Supabase enqueue tool.

This module contains test cases for the Enqueue tool, which is responsible for
sending jobs to a Supabase queue. Tests cover initialization, template handling,
and job enqueueing with various parameters.
"""

from unittest.mock import Mock, patch

import pytest
from langchain.prompts import PromptTemplate

from aimq.tools.supabase.enqueue import Enqueue, EnqueueInput


@pytest.fixture
def enqueue_tool():
    """Create an Enqueue tool instance for testing."""
    return Enqueue()


@pytest.fixture
def mock_provider():
    """Create a mock Supabase queue provider for testing.

    Returns a mock instance that can be used to verify queue interactions.
    """
    with patch("aimq.tools.supabase.enqueue.SupabaseQueueProvider") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


class TestEnqueue:
    """Test suite for the Enqueue tool.

    Tests the functionality of the Enqueue tool including initialization,
    template handling, and job enqueueing with various parameters.
    """

    def test_init(self, enqueue_tool):
        """Test initialization of Enqueue tool."""
        assert enqueue_tool.name == "enqueue"
        assert enqueue_tool.description == "Send a job to a Supabase Queue"
        assert enqueue_tool.args_schema == EnqueueInput

    def test_get_template_string(self, enqueue_tool):
        """Test converting string to PromptTemplate."""
        template = enqueue_tool._get_template("test/{name}")
        assert isinstance(template, PromptTemplate)
        assert template.template == "test/{name}"

    def test_get_template_prompt_template(self, enqueue_tool):
        """Test passing PromptTemplate directly."""
        original = PromptTemplate.from_template("test/{name}")
        template = enqueue_tool._get_template(original)
        assert template == original

    def test_run_with_defaults(self, enqueue_tool, mock_provider):
        """Test enqueueing a job with default parameters."""
        data = {"task": "test"}
        job_id = "job-1"
        expected_data = {"job_id": job_id, "queue": "", "status": "enqueued"}

        mock_provider.send.return_value = job_id

        result = enqueue_tool._run(data=data)

        assert result == expected_data
        mock_provider.send.assert_called_once_with(queue_name="", data=data, delay=None)

    def test_run_with_custom_queue(self, enqueue_tool, mock_provider):
        """Test enqueueing a job with custom queue."""
        data = {"task": "test"}
        queue = "custom_queue"
        job_id = "job-1"
        expected_data = {"job_id": job_id, "queue": queue, "status": "enqueued"}

        mock_provider.send.return_value = job_id

        result = enqueue_tool._run(data=data, queue=queue)

        assert result == expected_data
        mock_provider.send.assert_called_once_with(
            queue_name=queue, data=data, delay=None
        )

    def test_run_with_delay(self, enqueue_tool, mock_provider):
        """Test enqueueing a job with delay."""
        data = {"task": "test"}
        delay = 60
        job_id = "job-1"
        expected_data = {"job_id": job_id, "queue": "", "status": "enqueued"}

        mock_provider.send.return_value = job_id

        result = enqueue_tool._run(data=data, delay=delay)

        assert result == expected_data
        mock_provider.send.assert_called_once_with(
            queue_name="", data=data, delay=delay
        )

    def test_run_with_queue_and_delay(self, enqueue_tool, mock_provider):
        """Test enqueueing a job with both queue and delay."""
        data = {"task": "test"}
        queue = "custom_queue"
        delay = 60
        job_id = "job-1"
        expected_data = {"job_id": job_id, "queue": queue, "status": "enqueued"}

        mock_provider.send.return_value = job_id

        result = enqueue_tool._run(data=data, queue=queue, delay=delay)

        assert result == expected_data
        mock_provider.send.assert_called_once_with(
            queue_name=queue, data=data, delay=delay
        )
