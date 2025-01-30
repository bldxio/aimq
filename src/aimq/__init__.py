"""
AIMQ: AI Message Queue.

This package provides a robust message queue implementation designed for AI tasks.
It enables asynchronous task processing with support for retries, error handling,
and monitoring.
"""

from aimq.worker import Worker

__version__ = "0.1.0"
__all__ = ["Worker"]
