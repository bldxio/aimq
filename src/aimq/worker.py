import os
import signal
import sys
import threading
import time
from collections import OrderedDict
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional

from langchain.schema.runnable import Runnable, RunnableLambda
from pydantic import BaseModel, ConfigDict, Field

from .config import config  # Import config singleton instead of Config class
from .job import Job
from .logger import Logger, LogLevel
from .queue import Queue
from .realtime import RealtimeWakeupService
from .utils import load_module


class WorkerThread(threading.Thread):
    """A thread that processes jobs from multiple queues.

    Args:
        queues: Ordered dictionary of queue name to Queue instance mappings
        logger: Logger instance for recording worker activities
        running: Threading event to control the worker's execution
        idle_wait: Time in seconds to wait when no jobs are found
        realtime_service: Optional realtime service for instant wake-up

    Attributes:
        queues: The queues to process jobs from
        logger: Logger instance
        running: Threading event controlling execution
        idle_wait: Sleep duration when idle
        consecutive_failures: Track consecutive failures for backoff
        current_backoff: Current backoff duration in seconds
        realtime_service: Realtime service for instant wake-up
        wakeup_event: Event set by realtime service to wake this thread
    """

    def __init__(
        self,
        queues: OrderedDict[str, Queue],
        logger: Logger,
        running: threading.Event,
        idle_wait: float = 1.0,
        realtime_service: Optional[RealtimeWakeupService] = None,
    ):
        super().__init__()
        self.queues = queues
        self.logger = logger
        self.running = running
        self.idle_wait = idle_wait
        self.realtime_service = realtime_service
        # Track consecutive failures per queue for backoff
        self.consecutive_failures: dict[str, int] = {name: 0 for name in queues.keys()}
        self.current_backoff = idle_wait

        self.wakeup_event = threading.Event()
        if self.realtime_service:
            self.realtime_service.register_worker(self.wakeup_event)

    def run(self) -> None:  # noqa: C901
        """Start the worker thread with resilient error handling.

        Features:
        - Catches all exceptions to prevent thread crashes
        - Implements exponential backoff on repeated failures
        - Tracks consecutive failures per queue
        - Resets backoff on successful job processing
        - Only stops on shutdown signal (KeyboardInterrupt, SystemExit)
        """
        self.logger.info("Worker thread started")

        while self.running.is_set():
            try:
                found_jobs = False
                had_errors = False

                for queue in self.queues.values():
                    if not self.running.is_set():
                        break

                    # Work next job in queue
                    try:
                        # Track job start time for presence
                        job_start = time.time()
                        result = queue.work()

                        if result is not None:
                            found_jobs = True
                            # Reset consecutive failures on success
                            self.consecutive_failures[queue.name] = 0
                            self.current_backoff = self.idle_wait

                            # Update presence: busy with job timing
                            if self.realtime_service and hasattr(result, "id"):
                                self.realtime_service.update_presence(
                                    "busy", {result.id: job_start}
                                )

                    except Exception as e:
                        had_errors = True
                        # Increment consecutive failure counter
                        self.consecutive_failures[queue.name] += 1
                        failure_count = self.consecutive_failures[queue.name]

                        # Log with context (queue, job, attempt)
                        self.logger.error(
                            f"Error in queue {queue.name} (consecutive failures: {failure_count})",
                            {
                                "error": str(e),
                                "error_type": type(e).__name__,
                                "queue": queue.name,
                            },
                        )

                        # Calculate exponential backoff if multiple consecutive failures
                        if failure_count > 1:
                            # Exponential backoff: idle_wait * (multiplier ^ (failures - 1))
                            self.current_backoff = min(
                                self.idle_wait
                                * (config.queue_backoff_multiplier ** (failure_count - 1)),
                                config.queue_max_backoff,
                            )
                            self.logger.info(
                                f"Backing off for {self.current_backoff:.1f}s due to repeated failures in {queue.name}"
                            )

                # Update presence: idle (if realtime enabled and no jobs found)
                if not found_jobs and self.realtime_service:
                    self.realtime_service.update_presence("idle", {})

                if not found_jobs:
                    self.logger.debug(
                        f"No jobs found, waiting {self.current_backoff:.1f}s..."
                        + (" (backed off)" if had_errors else "")
                    )

                    # Interruptible sleep: check shutdown flag and realtime wake-up event
                    sleep_start = time.time()
                    self.wakeup_event.clear()  # Clear before sleeping

                    while (time.time() - sleep_start) < self.current_backoff:
                        if not self.running.is_set():
                            break

                        # Check if woken by realtime notification
                        if self.wakeup_event.is_set():
                            self.logger.debug("Woken by realtime notification")
                            self.current_backoff = self.idle_wait  # Reset backoff
                            break

                        time.sleep(0.1)  # Check every 100ms

                    # Exit main loop if shutdown was requested during sleep
                    if not self.running.is_set():
                        break

            except (KeyboardInterrupt, SystemExit):
                # Graceful shutdown signals - stop the thread
                self.logger.info("Received shutdown signal, stopping worker thread")
                self.running.clear()
                break

            except Exception as e:
                # Catch-all for truly unexpected errors (shouldn't happen with queue.work() handling)
                self.logger.error(
                    "Unexpected error in worker loop",
                    {
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                # Don't stop the thread - continue processing

        # Cleanup: unregister from realtime service
        if self.realtime_service:
            self.realtime_service.unregister_worker(self.wakeup_event)
            self.logger.debug("Unregistered from realtime service")


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
    realtime_service: Optional[RealtimeWakeupService] = None
    _shutdown_count: int = 0
    _original_termios_settings: Optional[Any] = None

    def assign(
        self,
        runnable: Runnable,
        *,
        queue: str | None = None,
        timeout: int = 300,
        delete_on_finish: bool = False,
        tags: List[str] | None = None,
        max_retries: int | None = None,
        dlq: str | None = None,
        on_error: Callable[[Job, Exception], None] | None = None,
    ) -> None:
        """Register a task with a queue name and runnable instance.

        Args:
            runnable: Langchain Runnable instance to process jobs
            queue: Queue name to assign the task to
            timeout: Maximum time in seconds for a task to complete. If 0, messages will be popped instead of read.
            delete_on_finish: Whether to delete (True) or archive (False) jobs after processing
            tags: Optional list of tags to associate with the queue
            max_retries: Maximum retry attempts for failed jobs. None uses config default.
            dlq: Dead-letter queue name for failed jobs exceeding max_retries
            on_error: Optional callback for custom error handling
        """

        runnable.name = queue or runnable.name
        if runnable.name is None:
            raise ValueError("Queue name is required")

        self.queues[runnable.name] = Queue(
            runnable=runnable,
            timeout=timeout,
            tags=tags or [],
            delete_on_finish=delete_on_finish,
            max_retries=max_retries,
            dlq=dlq,
            on_error=on_error,
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
        max_retries: int | None = None,
        dlq: str | None = None,
        on_error: Callable[[Job, Exception], None] | None = None,
    ) -> Callable:
        """Decorator to register a function that returns a Runnable with a queue.

        Args:
            queue: Name of the queue to get jobs from
            timeout: Maximum time in seconds for a task to complete. If 0, messages will be popped instead of read
            delete_on_finish: Whether to delete (True) or archive (False) jobs after processing
            tags: Optional list of tags to associate with the queue
            max_retries: Maximum retry attempts for failed jobs. None uses config default.
            dlq: Dead-letter queue name for failed jobs exceeding max_retries
            on_error: Optional callback for custom error handling
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
                max_retries=max_retries,
                dlq=dlq,
                on_error=on_error,
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

    def _setup_termios(self) -> None:
        """Disable ^C echo in terminal (Unix/Linux/macOS only)."""
        try:
            import termios

            # Only modify terminal settings if stdin is a TTY
            if sys.stdin.isatty():
                # Save original settings
                self._original_termios_settings = termios.tcgetattr(sys.stdin.fileno())

                # Create new settings with ECHOCTL disabled
                new_settings = termios.tcgetattr(sys.stdin.fileno())
                new_settings[3] = new_settings[3] & ~termios.ECHOCTL  # Disable ^C echo

                # Apply new settings
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, new_settings)
        except (ImportError, OSError, AttributeError):
            # termios not available (Windows) or not a TTY - skip
            pass

    def _restore_termios(self) -> None:
        """Restore original terminal settings."""
        if self._original_termios_settings is not None:
            try:
                import termios

                termios.tcsetattr(
                    sys.stdin.fileno(), termios.TCSADRAIN, self._original_termios_settings
                )
                self._original_termios_settings = None
            except (ImportError, OSError, AttributeError):
                # Can't restore - not critical
                pass

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self._shutdown_count += 1

        if self._shutdown_count == 1:
            # First Ctrl+C: Graceful shutdown
            print("\r", end="", flush=True)  # Clear ^C if termios didn't work

            # Log shutdown message with hint about force quit
            self.logger.info("Shutting down gracefully... (Press Ctrl+C again to force quit)")

            # Stop the worker thread
            self.stop()

            # Flush any remaining logs
            self.log(block=False)

            # Stop the logger to unblock queue.get() - AFTER flushing so None isn't consumed
            self.logger.stop()

            # Restore terminal settings if they were modified
            self._restore_termios()

            # Don't call sys.exit() - let the main thread complete naturally
            # The None sentinel will unblock logger.print(block=True) and process will exit
            # Goodbye message will be shown after thread completes successfully

        else:
            # Second Ctrl+C: Force quit
            try:
                from rich.console import Console

                console = Console()
                console.print("\n[bold red]Force quitting...[/bold red]")
            except ImportError:
                print("\nForce quitting...")

            # Restore terminal settings
            self._restore_termios()

            # Force exit immediately without cleanup (avoids threading exceptions)
            os._exit(1)

    def start(
        self,
        block: bool = True,
        motd: Optional[str | bool] = None,
        show_info: Optional[bool] = None,
    ) -> None:
        """Start processing tasks in an endless loop.

        Args:
            block: If True, block until events are available
            motd: MOTD source:
                - None (default): Auto-detect MOTD.md or use built-in
                - False: Disable MOTD
                - True: Use module docstring
                - str: Path to markdown file
            show_info: Show queue list (default: from AIMQ_SHOW_INFO env var)
        """
        if self.thread and self.thread.is_alive():
            return

        # Display MOTD and queue information
        from aimq.motd import print_startup_info

        # ENV override for show_info
        if show_info is None:
            show_info = os.getenv("AIMQ_SHOW_INFO", "false").lower() == "true"

        print_startup_info(worker=self, motd=motd, show_info=show_info)

        # Setup terminal to suppress ^C display (Unix/Linux/macOS only)
        self._setup_termios()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start realtime service if enabled
        if config.supabase_realtime_enabled and not self.realtime_service:
            try:
                queue_names = list(self.queues.keys())
                self.realtime_service = RealtimeWakeupService(
                    url=config.supabase_url,
                    key=config.supabase_key,
                    worker_name=self.name,
                    queues=queue_names,
                    logger=self.logger,
                )
                self.realtime_service.start()
                self.logger.info("Realtime wake-up service enabled")
            except Exception as e:
                self.logger.warning(
                    f"Failed to start realtime service: {e}. Falling back to polling.",
                    {"error_type": type(e).__name__},
                )
                self.realtime_service = None

        self.is_running.set()
        self.thread = WorkerThread(
            self.queues,
            self.logger,
            self.is_running,
            idle_wait=self.idle_wait,
            realtime_service=self.realtime_service,
        )
        self.thread.start()

        if block:
            try:
                self.log(block=block)
            finally:
                # Restore terminal settings on normal exit
                self._restore_termios()

    def stop(self) -> None:
        """Stop processing tasks and clear job history."""
        if self.is_running.is_set():
            self.is_running.clear()

            # Stop realtime service first
            if self.realtime_service:
                self.logger.info("Stopping realtime service...")
                self.realtime_service.stop()
                self.realtime_service = None

            if self.thread:
                # Wait up to 10 seconds for thread to finish
                # (accounts for 5-second queue read timeout)
                self.thread.join(timeout=10.0)

                # Log warning if thread didn't stop in time
                if self.thread.is_alive():
                    self.logger.warning(
                        "Worker thread did not stop within 10 seconds. "
                        "Press Ctrl+C again to force quit."
                    )
                else:
                    self.thread = None
                    self.logger.info("Worker stopped")

                    # Print goodbye message only if shutdown was successful
                    if self._shutdown_count > 0:  # Only during signal-based shutdown
                        try:
                            from rich.console import Console

                            console = Console()
                            console.print("\n[bold blue]Goodbye! 👋[/bold blue]")
                        except ImportError:
                            # Fallback if Rich is not available
                            print("\nGoodbye! 👋")
            else:
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
