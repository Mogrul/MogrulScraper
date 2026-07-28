import json
from dataclasses import dataclass, field

from .util import get_data_dir

@dataclass
class DownloadStats:
    downloaded_bytes: int
    downloaded_total: int

    _initialised: bool = field(
        default=False,
        init=False,
        repr=False,
    )

    def __post_init__(self):
        object.__setattr__(self, "_initialised", True)

    def __setattr__(self, name, value):
        old_value = getattr(self, name, None)

        super().__setattr__(name, value)

        if (
            getattr(self, "_initialised", False)
            and name in {"downloaded_bytes", "downloaded_total"}
            and old_value != value
        ):
            self._on_change(name, value)

    def _on_change(self, name: str, new: int):
        stat_file = get_data_dir() / "stats.json"
        stat_file.parent.mkdir(parents=True, exist_ok=True)

        if stat_file.exists():
            with open(stat_file, "r") as f:
                stats = json.load(f)
        else:
            stats = {}

        stats[name] = new

        with open(stat_file, "w") as f:
            json.dump(stats, f, indent=4)


        with open(stat_file, "w") as f:
            json.dump(stats, f, indent=4)