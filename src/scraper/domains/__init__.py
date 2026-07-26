from .domain import Domain

from .javtiful import Javtiful
from .simpcity import SimpCity

DOMAINS: dict[str, type[Domain]] = {
    "simpcity.cr": SimpCity,
    "javtiful.com": Javtiful,
}