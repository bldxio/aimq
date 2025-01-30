"""Command for starting the AIMQ worker."""

import signal
import sys
from pathlib import Path
from typing import Any, Optional

import typer

from aimq.logger import LogLevel
from aimq.worker import Worker

WORKER_PATH_ARG = typer.Argument(
    None,
    help="Path to the Python file containing worker definitions",
)

LOG_LEVEL_OPTION = typer.Option(
    LogLevel.INFO,
    "--log-level",
    "-l",
    help="Set the log level (debug, info, warning, error, critical)",
    case_sensitive=False,
)

DEBUG_OPTION = typer.Option(
    False,
    "--debug",
    "-d",
    help="Enable debug logging (shortcut for --log-level debug)",
)


def start(
    worker_path: Optional[Path] = WORKER_PATH_ARG,
    log_level: LogLevel = LOG_LEVEL_OPTION,
    debug: bool = DEBUG_OPTION,
) -> None:
    """Start the AIMQ worker with the specified tasks.

    Args:
        worker_path: Optional path to a Python file containing worker definitions.
        log_level: The logging level to use. Defaults to INFO.
        debug: If True, sets log_level to DEBUG regardless of log_level setting.

    Raises:
        typer.Exit: If there is an error starting the worker.
    """
    if worker_path:
        worker = Worker.load(worker_path)
    else:
        worker = Worker()

    worker.log_level = LogLevel.DEBUG if debug else log_level

    def signal_handler(signum: int, frame: Optional[Any]) -> None:
        """Handle shutdown signals gracefully.

        Args:
            signum: Signal number received.
            frame: Current stack frame (unused but required by signal.signal).
        """
        print("")
        worker.logger.info("Shutting down...")
        worker.log(block=False)
        worker.stop()
        worker.log(block=False)
        sys.exit(0)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        worker.start()
    except Exception as e:
        worker.logger.error(f"Error: {e}")
        worker.log(block=False)
        worker.stop()
        worker.log(block=False)
        sys.exit(1)


if __name__ == "__main__":
    typer.run(start)
