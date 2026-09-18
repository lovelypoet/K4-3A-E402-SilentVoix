from __future__ import annotations

from typing import Any


def evaluate_grounding(graph: dict[str, Any], expected_source: dict[str, Any] | None, citations: list[dict[str, Any]]) -> dict[str, Any]:
    all_sources = [source for node in graph.get("nodes") or [] for source in node.get("sources") or []]
    if not expected_source:
        return {"citation_accuracy": 1.0 if not citations else 0.0, "source_recall": 1.0, "unsupported_claim": bool(citations), "matched": False}
    def matches(source: dict[str, Any]) -> bool:
        return all(source.get(key) == value for key, value in expected_source.items())
    matched = any(matches(source) for source in citations)
    source_recall = 1.0 if any(matches(source) for source in all_sources) else 0.0
    return {
        "citation_accuracy": 1.0 if matched else 0.0,
        "source_recall": source_recall,
        "unsupported_claim": not matched,
        "matched": matched,
    }
