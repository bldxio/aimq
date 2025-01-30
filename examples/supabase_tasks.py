"""Example demonstrating Supabase tools usage with a worker."""

from typing import Any, Dict

# Ignore missing type hints in aimq.core.runnable
from aimq.core.runnable import (  # type: ignore
    RunnableAssign,
    RunnableParallel,
    RunnablePick,
)
from aimq.tools.supabase import ReadFile, ReadRecord, WriteRecord
from aimq.worker import Worker

# Create worker
worker = Worker()


@worker.task()
def read_records(_: Dict[str, Any]) -> RunnablePick:
    """Retrieve a user record from Supabase.

    Args:
        _: Input dictionary (unused)

    Returns:
        RunnablePick: A runnable that picks specific keys from the record
    """
    picker = RunnablePick(keys=["summary"])
    return ReadRecord(table="users") | picker


@worker.task()
def write_records(data: Dict[str, Any]) -> WriteRecord:
    """Update an existing user's name in Supabase.

    Args:
        data: Input data containing record updates

    Returns:
        WriteRecord: A runnable that writes the record to Supabase
    """
    return WriteRecord(table="users")


@worker.task()
def process_document(data: Dict[str, Any]) -> RunnableAssign:
    """Process a document using Supabase tools.

    Args:
        data: Input data for document processing

    Returns:
        RunnableAssign: A runnable that processes and assigns document data
    """
    return ReadRecord(
        table="documents_with_metadata",
        select="id, path:storage_object_path",
    ) | RunnableAssign(
        RunnableParallel({"file": ReadFile(bucket="files")})  # type: ignore
    )  # type: ignore


if __name__ == "__main__":
    # Start the worker
    worker.start()

    # Example usage:
    # Create a new user
    # worker.enqueue("create_user", args={"name": "John", "email": "john@example.com"})
    # Get user by email
    # worker.enqueue("get_user", args={"email": "john@example.com"})
    # Update user's name
    # worker.enqueue(
    #     "update_user",
    #     args={"email": "john@example.com", "name": "Johnny"}
    # )
