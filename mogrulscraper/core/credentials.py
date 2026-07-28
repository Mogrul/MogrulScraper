import secrets
import os

from .util import get_data_dir

def get_secret_key(name: str) -> str:
    secret_file = get_data_dir() / name

    if secret_file.exists():
        return secret_file.read_text().strip()

    key = secrets.token_hex(32)
    secret_file.write_text(key)
    os.chmod(secret_file, 0o600)

    return key