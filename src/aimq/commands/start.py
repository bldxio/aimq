from pathlib import Path
from typing import Optional
import signal
import sys
import typer

from aimq.worker import Worker
from aimq.logger import LogLevel

app = typer.Typer()

# @app.callback(invoke_without_command=True)
@app.command()
def start(
    worker_path: Optional[Path] = typer.Argument(
        None,
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
        worker = Worker()

    worker.log_level = LogLevel.DEBUG if debug else log_level
    
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        print('')
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
    app()