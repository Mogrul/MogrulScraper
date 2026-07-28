import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

from mogrulscraper.core import SingletonMeta
from .util import get_data_dir
from .models import DownloadStats

def _load_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "urls",
        nargs = "*",
        metavar = "URL",
        help = "List of URLs to scrape",
        default = [],
    )

    parser.add_argument(
        "--excluded-domains",
        nargs = "*",
        metavar = "DOMAIN",
        help = "Domain(s) to exclude",
        default = [],
    )

    parser.add_argument(
        "--chunk-size",
        type = int,
        help = "Chunk size (in bytes)",
        default = 1024 * 1024,
    )

    parser.add_argument(
        "--concurrent-downloads",
        type = int,
        help = "Number of concurrent downloads",
        default = 10,
    )

    parser.add_argument(
        "--debug",
        action = "store_true",
        help = "Enable debug logging",
        default = False,
    )

    parser.add_argument(
        "--timeout",
        type = int,
        help = "Timeout in seconds",
        default = 10,
    )

    parser.add_argument(
        "--porndb-token",
        type = str,
        help = "PornDB token",
        default = None,
    )

    parser.add_argument(
        "--download-path",
        type = str,
        help = "Download path",
        default = "Downloads",
    )

    return parser.parse_args()

def _load_json(path: Path, default: dict | None = None) -> dict:
    default = default or {}

    try:
        with open(path, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(default, f, indent=4)

        return default

    except json.JSONDecodeError:
        return default

class Settings(metaclass = SingletonMeta):
    def __init__(self):
        _args = _load_args()

        self.urls = _args.urls
        self.excluded_domains = _args.excluded_domains
        self.chunk_size = _args.chunk_size
        self.concurrent_downloads = _args.concurrent_downloads
        self.debug = _args.debug
        self.timeout = _args.timeout
        self.porndb_token: str | None = _args.porndb_token
        self.download_path = Path(_args.download_path)

        _history = _load_json(
            get_data_dir() / "history.json",
            default = {
                "history": []
            },
        )
        self.download_history: list[str] = _history["history"]

        _stats = _load_json(
            get_data_dir() / "stats.json",
            default = {
                "downloaded_bytes": 0,
                "downloaded_total": 0,
            }
        )
        self.stats = DownloadStats(
            downloaded_bytes = _stats["downloaded_bytes"],
            downloaded_total = _stats["downloaded_total"],
        )