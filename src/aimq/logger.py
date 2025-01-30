"""Logging configuration and utilities for AIMQ.

This module provides logging setup and custom log handlers for the AIMQ package.
It supports both file and console logging with different log levels and formats.
"""

import queue
from enum import Enum
from typing import Any, Generator, NamedTuple, Optional, Union

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class LogStyle(NamedTuple):
    """A named tuple representing a log style.

    Attributes:
        template (str): The log template.
        color (str): The log color.
    """

    template: str
    color: str


class LogLevel(str, Enum):
    """An enumeration of log levels.

    Attributes:
        DEBUG: Debug log level.
        INFO: Info log level.
        WARNING: Warning log level.
        ERROR: Error log level.
        CRITICAL: Critical log level.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def __ge__(self, other: Union["LogLevel", str]) -> bool:
        """Check if the log level is greater than or equal to another level.

        Args:
            other: The other log level.

        Returns:
            True if the log level is greater than or equal to the other level.
        """
        levels = list(LogLevel)
        if isinstance(other, str):
            other = LogLevel(other)
        return levels.index(self) >= levels.index(other)


class LogEvent(BaseModel):
    """A base model representing a log event.

    Attributes:
        level: The log level.
        msg: The log message.
        data: Optional log data.
        styles: A dictionary of log styles.
    """

    level: LogLevel
    msg: str
    data: Optional[Any] = None
    styles: dict[str, LogStyle] = Field(
        default_factory=lambda: {
            LogLevel.DEBUG.value: LogStyle("🔍 DEBUG", "blue"),
            LogLevel.INFO.value: LogStyle("ℹ️ INFO", "green"),
            LogLevel.WARNING.value: LogStyle("⚠️ WARNING", "yellow"),
            LogLevel.ERROR.value: LogStyle("❌ ERROR", "red"),
            LogLevel.CRITICAL.value: LogStyle("🚨 CRITICAL", "red bold"),
        }
    )

    def __str__(self) -> str:
        """Return a string representation of the log event.

        Returns:
            str: A string representation of the log event.
        """
        style = self.styles[self.level]
        result = f"{style.template}: {self.msg}"
        if self.data:
            result += f"\nData: {self.data}"
        return result

    def __repr__(self) -> str:
        """Return a repr representation of the log event.

        Returns:
            A repr representation of the log event.
        """
        return f"LogEvent(level={self.level!r}, msg={self.msg!r}, data={self.data!r})"

    def __rich__(self) -> Text:
        """Return a rich representation of the log event.

        Returns:
            A rich representation of the log event.
        """
        style = self.styles[self.level]
        text = Text()
        text.append(f"{style.template}: ", style=f"{style.color}")
        text.append(self.msg, style=f"dim {style.color}")

        if self.data:
            text.append("\nData: ", style=f"{style.color} bold")
            text.append(str(self.data), style=f"dim {style.color}")

        return text

    def print(self) -> None:
        """Print the log event."""
        style = self.styles[self.level]
        console = Console()
        console.print(Panel(self.__rich__(), border_style=style.color))


class Logger:
    """A logger class.

    Attributes:
        _queue: A queue for log events.
    """

    def __init__(self) -> None:
        """Initialize the logger."""
        self._queue: queue.Queue[Optional[LogEvent]] = queue.Queue()

    def log_event(self, event: LogEvent) -> None:
        """Log an event.

        Args:
            event: The log event.
        """
        self._queue.put(event)

    def debug(self, msg: str, data: Any = None) -> None:
        """Log a debug message.

        Args:
            msg: The debug message.
            data: Optional debug data.
        """
        self.log_event(LogEvent(level=LogLevel.DEBUG, msg=msg, data=data))

    def info(self, msg: str, data: Any = None) -> None:
        """Log an info message.

        Args:
            msg: The info message.
            data: Optional info data.
        """
        self.log_event(LogEvent(level=LogLevel.INFO, msg=msg, data=data))

    def warning(self, msg: str, data: Any = None) -> None:
        """Log a warning message.

        Args:
            msg: The warning message.
            data: Optional warning data.
        """
        self.log_event(LogEvent(level=LogLevel.WARNING, msg=msg, data=data))

    def error(self, msg: str, data: Any = None) -> None:
        """Log an error message.

        Args:
            msg: The error message.
            data: Optional error data.
        """
        self.log_event(LogEvent(level=LogLevel.ERROR, msg=msg, data=data))

    def critical(self, msg: str, data: Any = None) -> None:
        """Log a critical message.

        Args:
            msg: The critical message.
            data: Optional critical data.
        """
        self.log_event(LogEvent(level=LogLevel.CRITICAL, msg=msg, data=data))

    def stop(self) -> None:
        """Stop the logger."""
        self._queue.put(None)

    def events(self, block: bool = True) -> Generator[LogEvent, None, None]:
        """Get log events.

        Args:
            block: Whether to block until an event is available.

        Yields:
            LogEvent: A log event.
        """
        while True:
            try:
                event = self._queue.get(block=block)
                if event is None:
                    break
                yield event
            except queue.Empty:
                break

    def print(
        self, block: bool = True, level: Union[LogLevel, str] = LogLevel.INFO
    ) -> Generator[None, None, None]:
        """Print log events.

        Args:
            block: Whether to block until an event is available.
            level: The minimum log level to print.
        """
        if isinstance(level, str):
            level = LogLevel(level)
        for event in self.events(block=block):
            if event.level >= level:
                event.print()
                yield
