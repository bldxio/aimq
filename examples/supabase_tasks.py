"""
Example demonstrating Supabase tools usage with a worker.
"""

from langchain_core.runnables import RunnableParallel

from aimq.helpers import assign, pick
from aimq.tools.supabase import ReadFile, ReadRecord
from aimq.worker import Worker

# Create worker
worker = Worker()


@worker.task()
def read_records(_: dict):
    """Retrieve a user record from Supabase."""
    read_record_tool = ReadRecord(table="records", select="*")
    picker = pick(key=["summary"])
    return read_record_tool | picker


@worker.task()
def process_document(data: dict):
    """Process a document using Supabase tools."""
    read_record_tool = ReadRecord(
        table="documents_with_metadata", select="id, path:storage_object_path"
    )
    read_file_tool = ReadFile(bucket="files")
    return read_record_tool | assign(RunnableParallel({"file": read_file_tool}))


if __name__ == "__main__":
    # Start the worker
    worker.start()
