import logging

from .host import Host

class Javtiful(Host):
    def __init__(self, *args, **kwargs):
        super().__init__(
            logger = logging.getLogger("Host.Javtiful"),
            *args,
            **kwargs
        )

    def _on_task(self, url: str):
        pass