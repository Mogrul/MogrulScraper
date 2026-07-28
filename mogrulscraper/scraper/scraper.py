import logging
import threading
from collections import defaultdict
from urllib.parse import urlparse

from mogrulscraper.events import (
    event_manager, StatusEvent,
    EventType, TerminalEvent
)
from mogrulscraper.core import Settings
from mogrulscraper.hosts import HOSTS

class Scraper:
    def __init__(self):
        self._thread = None
        self._running = False
        self._logger = logging.getLogger("Scraper")
        self._events = event_manager
        self._settings = Settings()

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
        if not self._settings.urls:
            self._events.send(
                TerminalEvent(
                    "No URLs provided"
                )
            )
            self._events.send(
                StatusEvent(type=EventType.STATUS_STOPPED)
            )
            self._running = False
            return

        self._on_started()
        host_groups: dict[str, list[str]] = defaultdict(list)

        for url in self._settings.urls:
            parsed = urlparse(url)
            host_groups[parsed.netloc].append(parsed.path)

        for host, group in host_groups.items():
            self._parse_groups(host, group)

        self._on_stopped()

    def _on_started(self):
        self._events.send(
            TerminalEvent("Started Scraper")
        )
        self._events.send(
            StatusEvent(type = EventType.STATUS_STARTED)
        )
        self._logger.info(
            "Started Scraper"
        )

    def _on_stopped(self):
        self._events.send(
            TerminalEvent("Stopped Scraper")
        )
        self._events.send(
            StatusEvent(type = EventType.STATUS_STOPPED)
        )
        self._logger.info(
            "Stopped Scraper"
        )
        self._running = False

    def _parse_groups(self, host: str, group: list[str]):
        if host not in HOSTS:
            self._logger.warning(f"Host {host} is unsupported")
            self._events.send(
                TerminalEvent(f"Host {host} is unsupported")
            )
            return

        cls = HOSTS[host](group, host)
        cls.start()