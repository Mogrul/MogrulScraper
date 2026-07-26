import logging

from .domain import Domain

class SimpCity(Domain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            logger = logging.getLogger("Domain.SimpCity"),
            *args,
            **kwargs,
        )