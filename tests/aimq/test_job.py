from datetime import datetime, timedelta

import pytest

from aimq.job import Job


class TestJob:
    """Test cases for Job class."""

    @pytest.fixture
    def sample_job_data(self):
        """Fixture providing sample job data."""
        now = datetime.now()
        return {
            "msg_id": 1,
            "read_ct": 0,
            "vt": now + timedelta(hours=1),
            "message": {"task": "test_task"},
            "enqueued_at": now,
        }

    def test_job_creation(self, sample_job_data):
        """Test basic job creation with required fields."""
        job = Job(**sample_job_data)

        assert job.id == sample_job_data["msg_id"]
        assert job.attempt == sample_job_data["read_ct"]
        assert job.expires_at == sample_job_data["vt"]
        assert job.data == sample_job_data["message"]
        assert job.enqueued_at == sample_job_data["enqueued_at"]
        assert job.status == "pending"
        assert job.queue is None
        assert job._popped is False

    def test_job_from_response(self, sample_job_data):
        """Test creating a job from API response data."""
        queue_name = "test_queue"
        job = Job.from_response(sample_job_data, queue=queue_name, popped=True)

        assert job.id == sample_job_data["msg_id"]
        assert job.queue == queue_name
        assert job._popped is True

    def test_job_custom_status(self, sample_job_data):
        """Test job creation with custom status."""
        sample_job_data["status"] = "processing"
        job = Job(**sample_job_data)

        assert job.status == "processing"

    def test_job_updated_at_auto_set(self, sample_job_data):
        """Test that updated_at is automatically set if not provided."""
        job = Job(**sample_job_data)

        assert isinstance(job.updated_at, datetime)
        assert job.updated_at is not None
