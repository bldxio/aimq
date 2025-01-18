"""
Example demonstrating Supabase tools usage with a worker.
"""

from aimq.worker import Worker
from aimq.helpers import assign, const, pick, orig, echo, select
from aimq.tools.supabase import WriteRecord, ReadRecord, ReadFile, WriteFile

# Create worker
worker = Worker()


@worker.task()
def read_records(_: dict):
    """Retrieve a user record from Supabase."""
    picker = RunnablePick(keys=["summary"])
    return read_record | picker


@worker.task()
def write_records(data: dict):
    """Update an existing user's name in Supabase."""
    return write_record


if __name__ == "__main__":
    # Start the worker
    worker.start()


@worker.task()
def process_document(data: dict):
    """Process a document using Supabase tools."""

    return ReadRecord(
        table="documents_with_metadata", select="id, path:storage_object_path"
    ) | RunnableAssign(RunnableParallel({"file": ReadFile(bucket="files")}))

    # Example usage:
    # worker.enqueue("create_user", args={"name": "John Doe", "email": "john@example.com"})
    # worker.enqueue("get_user", args={"email": "john@example.com"})
    # worker.enqueue("update_user", args={"email": "john@example.com", "new_name": "Johnny Doe"})
