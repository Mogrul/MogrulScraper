import logging

from session import Session
from shared import Config


class Domain:
    def __init__(
            self,
            url: str,
            logger: logging.Logger | None = None,
            site_name: str | None = None,
    ):
        self._url = url
        self._logger = logger if logger else logging.getLogger("Domain")
        self._site_name = site_name if site_name else "domain"
        self._session = Session()
        self._config = Config()

        from web.routes import send_terminal
        self._send_terminal = send_terminal

    def run(self):
        pass