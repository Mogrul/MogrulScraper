import logging
import threading

from session import Session
from shared import SingletonMeta, Config

class Scraper(metaclass = SingletonMeta):
    def __init__(self):
        self._logger = logging.getLogger("Scraper")
        self._config = Config()
        self._session = Session()
        self._stop_event = threading.Event()

    @property
    def is_playing(self) -> bool:
        return not self._stop_event.is_set()

    def start(self):
        self._logger.info("Started")

    def stop(self):
        self._logger.info("Stopping...")
        self._stop_event.set()