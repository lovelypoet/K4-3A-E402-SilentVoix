from typing import Any, Dict

from ai.grounding.evidence import analyze_evidence


VALID_DECISIONS = {"GENERATE_QUIZ", "DISAMBIGUATE", "REFUSE_UNGROUNDED"}


def decide_quiz(graph: Dict[str, Any], concept_id: str) -> str:
    if not concept_id:
        return "REFUSE_UNGROUNDED"

    node = next((n for n in graph.get("nodes") or [] if n.get("id") == concept_id), None)
    if node is None:
        return "REFUSE_UNGROUNDED"

    return analyze_evidence(graph, concept_id)["decision"]


def analyze_quiz_evidence(graph: Dict[str, Any], concept_id: str) -> Dict[str, Any]:
    return analyze_evidence(graph, concept_id)
