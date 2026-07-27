from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from bs4 import BeautifulSoup

from enums import Status, ResponseType, RequestType, EventDownloadType


@dataclass(frozen = True)
class Request:
    url: str
    request_type: RequestType
    response_type: ResponseType
    headers: dict = field(default_factory = dict)
    params: dict = field(default_factory = dict)
    json: dict = field(default_factory = dict)

@dataclass(frozen = True)
class Response:
    url: str
    status: Status
    headers: dict = field(default_factory = dict)
    params: dict = field(default_factory = dict)
    json: dict = field(default_factory = dict)
    soup: BeautifulSoup = field(
        default_factory = lambda: BeautifulSoup("", "html.parser")
    )
    text: str = field(default_factory = str)

@dataclass(frozen = True)
class DownloadRequest:
    url: str
    destination: Path
    headers: dict = field(default_factory = dict)
    params: dict = field(default_factory = dict)

@dataclass(frozen = True)
class EventDownload:
    type: EventDownloadType
    id: str
    name: str
    progress: int

@dataclass(frozen = True)
class EventTerminal:
    message: str
    type: str = "terminal"

@dataclass(frozen = True)
class EventStop:
    type: str = "stop"

@dataclass
class Download:
    id: str
    name: str
    progress: int