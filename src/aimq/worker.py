import threading
import time
from collections import OrderedDict
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional

from langchain.schema.runnable import Runnable, RunnableLambda
from pydantic import BaseModel, ConfigDict, Field

from .config import config  # Import config singleton instead of Config class
from .logger import Logger, LogLevel
from .queue import Queue
from .utils import load_module


class WorkerThread(threading.Thread):
    """A thread that processes jobs from multiple queues.

    Args:
        queues: Ordered dictionary of queue name to Queue instance mappings
        logger: Logger instance for recording worker activities
        running: Threading event to control the worker's execution
        idle_wait: Time in seconds to wait when no jobs are found

    Attributes:
        queues: The queues to process jobs from
        logger: Logger instance
        running: Threading event controlling execution
        idle_wait: Sleep duration when idle
    """

    def __init__(
        self,
        queues: OrderedDict[str, Queue],
        logger: Logger,
        running: threading.Event,
        idle_wait: float = 1.0,
    ):
        super().__init__()
        self.queues = queues
        self.logger = logger
        self.running = running
        self.idle_wait = idle_wait

    def run(self) -> None:
        """Start the worker thread."""
        self.logger.info("Worker thread started")

        while self.running.is_set():
            try:
                found_jobs = False
                for queue in self.queues.values():
                    if not self.running.is_set():
                        break

                    # work next job in queue
                    try:
                        found_jobs = found_jobs or bool(queue.work())
                    except RuntimeError as e:
                        self.logger.error(f"Runtime error in queue {queue.name}", {"error": str(e)})

                if not found_jobs:
                    self.logger.debug("No jobs found, waiting...")
                    time.sleep(self.idle_wait)

            except Exception as e:
                self.logger.critical(
                    "Worker thread encountered an unhandled error", {"error": str(e)}
                )
                self.running.clear()


class Worker(BaseModel):
    """Main worker class that manages job processing across multiple queues.

    The Worker class is responsible for managing multiple queues and their associated
    processing threads. It handles queue registration, thread management, and provides
    a clean interface for starting and stopping job processing.

    Attributes:
        queues: Ordered dictionary of registered queues
        logger: Logger instance for recording worker activities
        log_level: Current logging level
        running: Threading event controlling worker execution
        thread: Worker thread instance
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    queues: OrderedDict[str, Queue] = Field(default_factory=OrderedDict)
    logger: Logger = Field(default_factory=Logger)
    log_level: LogLevel | str = Field(default_factory=lambda: config.worker_log_level)
    idle_wait: float = Field(default_factory=lambda: config.worker_idle_wait)
    is_running: threading.Event = Field(default_factory=threading.Event)
    thread: Optional[WorkerThread] = None
    name: str = Field(default_factory=lambda: config.worker_name, description="Name of this worker")

    def assign(
        self,
        runnable: Runnable,
        *,
        queue: str | None = None,
        timeout: int = 300,
        delete_on_finish: bool = False,
        tags: List[str] | None = None,
    ) -> None:
        """Register a task with a queue name and runnable instance.

        Args:
            runnable: Langchain Runnable instance to process jobs
            queue: Queue name to assign the task to
            timeout: Maximum time in seconds for a task to complete. If 0, messages will be popped instead of read.
            delete_on_finish: Whether to delete (True) or archive (False) jobs after processing
            tags: Optional list of tags to associate with the queue
        """

        runnable.name = queue or runnable.name
        if runnable.name is None:
            raise ValueError("Queue name is required")

        self.queues[runnable.name] = Queue(
            runnable=runnable,
            timeout=timeout,
            tags=tags or [],
            delete_on_finish=delete_on_finish,
            logger=self.logger,
            worker_name=self.name,
        )
        self.logger.info(f"Registered task {runnable.name}")

    def task(
        self,
        *,
        queue: str | None = None,
        timeout: int = 300,
        tags: List[str] | None = None,
        delete_on_finish: bool = False,
    ) -> Callable:
        """Decorator to register a function that returns a Runnable with a queue.

        Args:
            queue: Name of the queue to get jobs from
            timeout: Maximum time in seconds for a task to complete. If 0, messages will be popped instead of read
            delete_on_finish: Whether to delete (True) or archive (False) jobs after processing
            tags: Optional list of tags to associate with the queue
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            self.assign(
                RunnableLambda(func, name=(queue or func.__name__)),
                timeout=timeout,
                delete_on_finish=delete_on_finish,
                tags=tags,
            )
            return wrapper

        return decorator

    def send(self, queue: str, data: dict[str, Any], delay: int | None = None) -> int:
        """Send data to a queue.

        Args:
            queue: Name of the queue to send data to
            data: Data to send
            delay: Optional delay in seconds before sending the data
        """
        return self.queues[queue].send(data, delay)

    def work(self, queue: str) -> Any:
        """Process a job from a queue.

        Args:
            queue: Name of the queue to process a job from
        """
        return self.queues[queue].work()

    def start(self, block: bool = True) -> None:
        """Start processing tasks in an endless loop.

        Args:
            block: If True, block until events are available
        """
        if self.thread and self.thread.is_alive():
            return

        self.is_running.set()
        self.thread = WorkerThread(
            self.queues, self.logger, self.is_running, idle_wait=self.idle_wait
        )
        self.thread.start()

        if block:
            self.log(block=block)

    def stop(self) -> None:
        """Stop processing tasks and clear job history."""
        if self.is_running.is_set():
            self.is_running.clear()
            if self.thread:
                self.thread.join()
                self.thread = None
            self.logger.info("Worker stopped")

    def log(self, block: bool = True) -> None:
        """Print log events from the logger.

        Args:
            block: If True, block until events are available
        """
        self.logger.print(block=block, level=self.log_level)

    @classmethod
    def load(cls, worker_path: Path) -> "Worker":
        """Load a worker instance from a Python file.

        Args:
            worker_path: Path to the Python file containing the worker instance

        Returns:
            Worker instance exported as 'worker' from the module

        Raises:
            ImportError: If the module cannot be loaded
            AttributeError: If the module does not export a 'worker' attribute
        """
        module = load_module(worker_path)

        if not hasattr(module, "worker"):
            raise AttributeError(f"Module {worker_path} does not export a 'worker' attribute")

        worker: Worker = module.worker
        worker.logger.info(f"Tasks loaded from file {worker_path}")

        return worker
