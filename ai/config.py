from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
LOCAL_KEYS_FILE = ROOT_DIR / "local_api_keys.md"


def _read_local_keys() -> dict[str, str]:
    """Read simple KEY=value entries from the ignored local markdown file."""
    if not LOCAL_KEYS_FILE.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in LOCAL_KEYS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key:
            values[key] = value
    return values


def get_config(name: str, default: str | None = None) -> str | None:
    """Prefer process environment variables, then the ignored local key file."""
    value = os.getenv(name)
    if value is not None and value != "":
        return value
    return _read_local_keys().get(name) or default

