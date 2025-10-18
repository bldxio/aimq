"""Command for starting the AIMQ worker."""

import signal
import sys
from pathlib import Path
from typing import Optional

import typer

from aimq.config import config
from aimq.logger import LogLevel
from aimq.worker import Worker


def start(
    worker_path: Optional[Path] = typer.Argument(
        config.worker_path,
        help="Path to the Python file containing worker definitions",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO,
        "--log-level",
        "-l",
        help="Set the log level (debug, info, warning, error, critical)",
        case_sensitive=False,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging (shortcut for --log-level debug)",
    ),
):
    """Start the AIMQ worker with the specified tasks."""
    if worker_path:
        worker = Worker.load(worker_path)
    else:
        worker_path = config.worker_path
        worker = Worker.load()

    worker.log_level = LogLevel.DEBUG if debug else log_level

    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
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
