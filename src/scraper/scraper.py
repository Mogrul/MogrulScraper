import logging
import os
import threading
from urllib.parse import urlparse

from session import Session
from shared import SingletonMeta, Config
from shared.util import clean_url
from .domains import DOMAINS


class Scraper(metaclass = SingletonMeta):
    def __init__(self):
        self._logger = logging.getLogger("Scraper")
        self._config = Config()
        self._session = Session()
        self._stop_event = threading.Event()

        self._thread: threading.Thread | None = None

        from web.routes import send_terminal
        self._send_terminal = send_terminal

    @property
    def is_playing(self) -> bool:
        return not self._stop_event.is_set()

    def start(self):
        self._stop_event.clear()

        self._thread = threading.Thread(
            target = self._start,
            daemon = True,
        )
        self._thread.start()

    def stop(self):
        self._logger.info("Stopping...")
        self._stop_event.set()

    def _start(self):
        self._logger.info("Started")

        urls = set(self._config.urls)

        if not urls:
            message = "No urls provided."
            self._logger.info(message)
            self._send_terminal(f"{'[SCRAPER]':^15}" + message)

        else:
            message = f"Scraping {len(urls)} urls."
            self._logger.info(message)
            self._send_terminal(f"{'[SCRAPER]':^15}" + message)

        # Clean javtiful out if porndb token not provided
        notified = False
        if not self._config.porndb_token:
            for url in urls.copy():
                if "javtiful" in url:
                    if not notified:
                        message = "Scraping javtiful requires the --porndb-token flag."
                        self._logger.warning(message)
                        self._send_terminal(f"{'[SCRAPER]':^15}" + message)
                        notified = True

                    urls.remove(url)

        for url in urls:
            url = clean_url(url)
            self._pass_to_domain(url)

    def _pass_to_domain(self, url: str):
        domain_name = urlparse(url).netloc
        if domain_name in self._config.disabled_domains:
            return

        domain = DOMAINS.get(domain_name)

        if not domain:
            message = f"{domain_name:<20} Unsupported domain for: {url}"
            self._logger.warning(message)
            self._send_terminal(f"{'[SCRAPER]':^15}" + message)
            return

        domain(
            url = url,
            stop_event = self._stop_event,
        ).run()