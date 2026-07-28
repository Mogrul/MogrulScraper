import logging
import threading
import time
from uuid import uuid3, uuid4

from mogrulscraper.events import event_manager, StatusEvent, EventType, TerminalEvent, DownloadEvent


class Scraper:
    def __init__(self):
        self._thread = None
        self._running = False
        self._logger = logging.getLogger("Scraper")
        self._events = event_manager

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> bool:
        if self._running:
            return False

        self._running = True

        self._thread = threading.Thread(
            target = self.run_main,
            daemon = True,
        )
        self._thread.start()

        return True

    def stop(self) -> bool:
        if not self._running:
            return False

        self._running = False

        self._events.send(
            StatusEvent(type = EventType.STATUS_STOPPED)
        )

        return True

    def run_main(self):
        self._events.send(
            TerminalEvent("Started Scraper")
        )
        self._events.send(
            StatusEvent(type = EventType.STATUS_STARTED)
        )
        self._logger.info(
            "Started Scraper"
        )

        while self._running:
            time.sleep(1)
            self._events.send(
                DownloadEvent(
                    id = str(uuid4()),
                    name = str(uuid4()),
                    progress = 10,
                    type = EventType.DOWNLOAD_ADD
                )
            )

            pass

        self._events.send(
            TerminalEvent("Stopped Scraper")
        )
        self._events.send(
            StatusEvent(type = EventType.STATUS_STOPPED)
        )
        self._logger.info(
            "Stopped Scraper"
        )