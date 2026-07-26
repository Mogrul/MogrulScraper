from enum import Enum

class Status(Enum):
    OK = 200
    ERROR = 404
    ERROR_JSON = 405
    ERROR_SOUP = 406
    ERROR_TIMEOUT = 407

class ResponseType(Enum):
    JSON = 1
    SOUP = 2
    TEXT = 3

class RequestType(Enum):
    GET = 1
    POST = 2

class EventDownloadType(Enum):
    ADD = "download_add"
    PROGRESS = "download_progress"
    COMPLETE = "download_complete"