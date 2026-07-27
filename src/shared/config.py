import argparse
import json
from pathlib import Path

from .singleton import SingletonMeta

class Config(metaclass = SingletonMeta):
    def __init__(self):
        _args = self._parse_args()

        self.web_client: bool = _args.web_client
        self.urls: list[str] = _args.urls
        self.host: str = _args.host
        self.port: int = _args.port
        self.debug: bool = _args.debug
        self.chunk_size: int = _args.chunk_size
        self.concurrent: int = _args.concurrent
        self.timeout: int = _args.timeout
        self.porndb_token: str | None = _args.porndb_token
        self.download_path = Path(_args.download_path)
        self.disabled_domains: list[str] = _args.disabled_domains

        # Attempt to load json configs
        _json = self._load_json()
        self.domain_paths = _json.get("domain.paths", {})

    def _load_json(self) -> dict:
        path = Path("config.json")

        if not path.exists():
            return {}

        try:
            return json.load(path.open())

        except json.decoder.JSONDecodeError:
            return {}

    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "urls",
            nargs = "*",
            metavar = "URL",
            default = [],
            help = "URLs to scrape",
        )

        parser.add_argument(
            "--disabled-domains",
            nargs = "*",
            metavar = "DOMAIN",
            default = [],
            help = "Domain to disable",
        )

        parser.add_argument(
            "--web-client",
            action = "store_true",
            default = False,
            help = "Use web client",
        )

        parser.add_argument(
            "--host",
            type = str,
            default = "127.0.0.1",
            help = "Host address",
        )

        parser.add_argument(
            "--port",
            type = int,
            default = 8080,
            help = "Host port",
        )

        parser.add_argument(
            "--debug",
            action = "store_true",
            default = False,
            help = "Debug mode",
        )

        parser.add_argument(
            "--chunk-size",
            type = int,
            default = 1024 * 1024,
            help = "Chunk size",
        )

        parser.add_argument(
            "--concurrent",
            type = int,
            default = 10,
            help = "Number of concurrent downloads",
        )

        parser.add_argument(
            "--timeout",
            type = int,
            default = 10,
            help = "Timeout in seconds",
        )

        parser.add_argument(
            "--porndb-token",
            type = str,
            default = None,
            help = "PornDB token",
        )

        parser.add_argument(
            "--download-path",
            type = str,
            default = "Downloads",
            help = "Path to download directory",
        )

        return parser.parse_args()