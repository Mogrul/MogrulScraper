from .host import Host
from .javtiful import Javtiful

HOSTS: dict[str, type[Host]] = {
    "javtiful.com": Javtiful,
}

__all__ = ["HOSTS", "Host", "Javtiful"]