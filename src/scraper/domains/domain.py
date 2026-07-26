import logging


class Domain:
    def __init__(
            self,
            url: str,
            logger: logging.Logger | None = None
    ):
        self.url = url
        self.logger = logger if logger else logging.getLogger("Domain")