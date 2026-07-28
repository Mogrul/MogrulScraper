from .manager import EventManager
from .models import Event, DownloadEvent, TerminalEvent, StatusEvent
from .enums import EventType

event_manager = EventManager()

__all__ = [
    "EventManager",
    "DownloadEvent",
    "TerminalEvent",
    "StatusEvent",
    "EventType",
    "event_manager",
]