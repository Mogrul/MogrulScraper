import logging

from mogrulscraper.core import Settings
from mogrulscraper.events import event_manager, TerminalEvent

class Host:
    def __init__(
            self,
            group: list[str],
            host_name: str,
            logger: logging.Logger | None = None,
    ):
        self._logger = logger or logging.getLogger(__name__)
        self._group = group
        self._settings = Settings()
        self._host_name = host_name
        self._events = event_manager

    def start(self):
        msg = f"Handling {len(self._group)} urls..."
        self._logger.info(msg)
        self._events.send(
            TerminalEvent(msg)
        )

    def _on_task(self, url: str):
        pass

    def _handle_album(self, url: str):
        pass

    def _handle_file(self, url: str):
        pass