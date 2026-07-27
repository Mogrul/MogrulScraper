import logging
import os
from pathlib import Path
from threading import Event

from session import Session
from shared import Config


class Domain:
    def __init__(
            self,
            url: str,
            stop_event: Event,
            domain_name: str,
            logger: logging.Logger | None = None,
            site_name: str | None = None,
    ):
        self._url = url
        self._logger = logger if logger else logging.getLogger("Domain")
        self._site_name = site_name if site_name else "domain"
        self._session = Session()
        self._config = Config()
        self._stop_event = stop_event

        _path_str = self._config.domain_paths.get(domain_name)
        self._domain_path = Path(_path_str) if _path_str else None

        from web.routes import send_terminal
        self._send_terminal = send_terminal

    def run(self):
        pass