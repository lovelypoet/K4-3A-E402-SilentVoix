from __future__ import annotations

import re
from typing import Any

from ai.config import get_config


def _as_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        return max(minimum, min(maximum, int(get_config(name, str(default)) or default)))
    except (TypeError, ValueError):
        return default


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _overlap(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    return len(a & b) / max(1, len(a | b))


def _rank_score(concept: dict[str, Any], source: dict[str, Any]) -> float:
    text = str(source.get("text") or "")
    label_tokens = _tokens(str(concept.get("label") or concept.get("id") or ""))
    text_tokens = _tokens(text)
    explanatory = sum(marker in text.lower() for marker in (" is ", " are ", " used ", " means ", " because ", " minimizes ", " predicts ", " measures "))
    return len(label_tokens & text_tokens) * 5 + explanatory * 2 + min(len(text), 2000) / 2000


def select_evidence(
    concept: dict[str, Any], evidence: list[dict[str, Any]],
    top_k: int | None = None, max_chars: int | None = None,
) -> list[dict[str, Any]]:
    """Select short, ranked, non-duplicate evidence while retaining source metadata."""
    configured_top_k = _as_int("QUIZ_EVIDENCE_TOP_K", 3, 1, 5)
    configured_max_chars = _as_int("QUIZ_EVIDENCE_MAX_CHARS", 6000, 500, 6000)
    top_k = max(1, min(5, top_k if top_k is not None else configured_top_k))
    max_chars = max(500, min(6000, max_chars if max_chars is not None else configured_max_chars))

    ranked = sorted(
        [item for item in evidence if str(item.get("text") or "").strip()],
        key=lambda item: _rank_score(concept, item), reverse=True,
    )
    selected: list[dict[str, Any]] = []
    for source in ranked:
        text = str(source.get("text") or "").strip()
        if any(text == str(item.get("text") or "").strip() or _overlap(text, str(item.get("text") or "")) >= 0.88 for item in selected):
            continue
        selected.append(dict(source))
        if len(selected) >= top_k:
            break

    # Keep complete chunks whenever possible. If one chunk is oversized, truncate at
    # a sentence/newline boundary and retain its original chunk_id for citation.
    budgeted: list[dict[str, Any]] = []
    used_chars = 0
    for item in selected:
        text = str(item.get("text") or "").strip()
        remaining = max_chars - used_chars
        if remaining <= 0:
            break
        if len(text) > remaining:
            if not budgeted and remaining > 0:
                candidate = text[:remaining]
                boundary = max(candidate.rfind("\n"), candidate.rfind(". "), candidate.rfind("; "))
                item["text"] = candidate[:boundary + 1].strip() if boundary >= max(100, remaining // 3) else candidate.strip()
                budgeted.append(item)
            break
        budgeted.append(item)
        used_chars += len(text)

    for index, item in enumerate(budgeted, start=1):
        item["_evidence_id"] = f"E{index}"
    return budgeted


def evidence_character_count(evidence: list[dict[str, Any]]) -> int:
    return sum(len(str(item.get("text") or "")) for item in evidence)

