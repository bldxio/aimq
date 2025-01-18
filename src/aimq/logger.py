import queue
from enum import Enum
from typing import Any, Optional, NamedTuple, Union
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class LogStyle(NamedTuple):
    template: str
    color: str

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def __ge__(self, other: Union["LogLevel", str]) -> bool:
        if isinstance(other, str):
            other = LogLevel(other)
        levels = list(LogLevel)
        return levels.index(self) >= levels.index(other)

class LogEvent(BaseModel):
    level: LogLevel
    msg: str
    data: Optional[Any] = None
    styles: dict[str, LogStyle] = Field(default_factory=lambda: {
        LogLevel.DEBUG: LogStyle("🔍 DEBUG", "blue"),
        LogLevel.INFO: LogStyle("ℹ️ INFO", "green"),
        LogLevel.WARNING: LogStyle("⚠️ WARNING", "yellow"),
        LogLevel.ERROR: LogStyle("❌ ERROR", "red"),
        LogLevel.CRITICAL: LogStyle("🚨 CRITICAL", "red bold")
    })

    def __str__(self) -> str:
        style = self.styles[self.level]
        result = f"{style.template}: {self.msg}"
        if self.data:
            result += f"\nData: {self.data}"
        return result

    def __repr__(self) -> str:
        return f"LogEvent(level={self.level!r}, msg={self.msg!r}, data={self.data!r})"

    def __rich__(self) -> Text:
        style = self.styles[self.level]
        text = Text()
        text.append(f"{style.template}: ", style=f"{style.color}")
        text.append(self.msg, style=f"dim {style.color}")
        
        if self.data:
            text.append("\nData: ", style=f"{style.color} bold")
            text.append(str(self.data), style=f"dim {style.color}")
        
        return text

    def print(self):
        style = self.styles[self.level]
        console.print(Panel(self.__rich__(), border_style=style.color))

class Logger:
    def __init__(self):
        self._queue = queue.Queue()

    def log_event(self, event: LogEvent):
        self._queue.put(event)

    def debug(self, msg: str, data: Any = None):
        self.log_event(LogEvent(level=LogLevel.DEBUG, msg=msg, data=data))

    def info(self, msg: str, data: Any = None):
        self.log_event(LogEvent(level=LogLevel.INFO, msg=msg, data=data))

    def warning(self, msg: str, data: Any = None):
        self.log_event(LogEvent(level=LogLevel.WARNING, msg=msg, data=data))

    def error(self, msg: str, data: Any = None):
        self.log_event(LogEvent(level=LogLevel.ERROR, msg=msg, data=data))

    def critical(self, msg: str, data: Any = None):
        self.log_event(LogEvent(level=LogLevel.CRITICAL, msg=msg, data=data))

    def stop(self):
        self._queue.put(None)

    def events(self, block=True):
        while True:
            try:
                event = self._queue.get(block=block)
                if event is None:
                    break
                yield event
            except queue.Empty:
                break

    def print(self, block=True, level: Union[LogLevel, str] = LogLevel.INFO):
        if isinstance(level, str):
            level = LogLevel(level)
        [event.print() for event in self.events(block=block) if event.level >= level]