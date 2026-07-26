from .domain import Domain

from .simpcity import SimpCity

DOMAINS: dict[str, type[Domain]] = {
    "simpcity.cr": SimpCity,
}