from dataclasses import dataclass, field

from .enums import EventType


@dataclass
class Event:
    type: EventType = field(kw_only=True)


@dataclass
class DownloadEvent(Event):
    id: str
    name: str
    progress: int = 0


@dataclass
class TerminalEvent(Event):
    message: str
    type: EventType = field(
        default = EventType.TERMINAL,
        kw_only = True,
    )


@dataclass
class StatusEvent(Event):
    pass
