from enum import Enum

class EventType(str, Enum):
    DOWNLOAD_ADD = "download_add"
    DOWNLOAD_PROGRESS = "download_progress"
    DOWNLOAD_COMPLETE = "download_complete"

    STATUS_STOPPED = "status_stopped"
    STATUS_STARTED = "status_started"

    TERMINAL = "terminal"