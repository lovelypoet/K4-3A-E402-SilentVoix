from __future__ import annotations

import re
from typing import Any


_EXPLANATORY_MARKERS = (
    " is ", " are ", " used ", " measures ", " predicts ", " minimizes ",
    " algorithm", " function", " model", " method", " mechanism", " represents ",
    " stores ", " made of ", " type of ", " optimizer", " updates ", " processes ",
)
_MENTION_MARKERS = ("mentions", "mentioned", "introduces")


def _source_texts(node: dict[str, Any]) -> list[str]:
    return [str(source.get("text") or "").strip().lower() for source in node.get("sources") or [] if source.get("text")]


def _concept_tokens(label: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", label.lower()) if len(token) > 2}


def analyze_evidence(graph: dict[str, Any], concept_id: str) -> dict[str, Any]:
    nodes = graph.get("nodes") or []
    node = next((item for item in nodes if item.get("id") == concept_id), None)
    if node is None:
        return {
            "concept_supported": False,
            "concept_unambiguous": True,
            "question_support_available": False,
            "answer_support_available": False,
            "explanation_support_available": False,
            "citation_available": False,
            "evidence_level": "none",
            "decision": "REFUSE_UNGROUNDED",
            "reasons": ["requested concept is absent from the graph"],
        }

    texts = _source_texts(node)
    combined = " ".join(texts)
    label = str(node.get("label") or concept_id).lower()
    concept_present = bool(texts) and any(label in text or concept_id.replace("_", " ") in text for text in texts)
    explanatory = any(marker in combined for marker in _EXPLANATORY_MARKERS)
    mention_only = bool(texts) and any(marker in combined for marker in _MENTION_MARKERS) and not explanatory
    other_nodes = [item for item in nodes if item.get("id") != concept_id]
    requested_tokens = _concept_tokens(label)
    competing = [item.get("id") for item in other_nodes if requested_tokens & _concept_tokens(str(item.get("label") or item.get("id") or ""))]
    unambiguous = not competing
    concept_supported = concept_present and not mention_only
    enough_for_claims = concept_supported and explanatory
    if not texts:
        decision = "REFUSE_UNGROUNDED"
        evidence_level = "none"
        reasons = ["concept has no source text"]
    elif not unambiguous:
        decision = "DISAMBIGUATE"
        evidence_level = "ambiguous"
        reasons = ["competing concept interpretation is present: " + ", ".join(competing)]
    elif mention_only:
        decision = "REFUSE_UNGROUNDED"
        evidence_level = "mention_only"
        reasons = ["source only mentions the concept without explanatory content"]
    elif not enough_for_claims:
        decision = "DISAMBIGUATE"
        evidence_level = "partial"
        reasons = ["source text is present but does not support all quiz claims"]
    else:
        decision = "GENERATE_QUIZ"
        evidence_level = "sufficient"
        reasons = []

    return {
        "concept_supported": concept_supported,
        "concept_unambiguous": unambiguous,
        "question_support_available": enough_for_claims,
        "answer_support_available": enough_for_claims,
        "explanation_support_available": enough_for_claims,
        "citation_available": bool(node.get("sources")),
        "evidence_level": evidence_level,
        "decision": decision,
        "reasons": reasons,
        "retrieved_sources": node.get("sources") or [],
    }
