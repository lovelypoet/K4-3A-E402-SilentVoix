from __future__ import annotations

from collections import Counter


_COUNTERS = Counter({
    "live_generation_success": 0,
    "cache_hit": 0,
    "429_count": 0,
    "503_count": 0,
    "generation_failed": 0,
    "validation_failed": 0,
})


def record(name: str, amount: int = 1) -> None:
    _COUNTERS[name] += amount


def summary() -> dict[str, int]:
    return dict(_COUNTERS)

