from pathlib import Path
import platform


def get_data_dir():
    system = platform.system()

    if system == "Windows":
        base = Path.home() / "AppData" / "Local"
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    path = base / "MogrulScraper"
    path.mkdir(parents=True, exist_ok=True)

    return path

def format_bytes(amount: int) -> str:
    value = float(amount)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"{value:.2f} {unit}"

        value /= 1024

    return f"{value:.2f} PB"