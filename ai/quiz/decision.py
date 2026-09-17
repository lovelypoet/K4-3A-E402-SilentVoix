from typing import Any, Dict


VALID_DECISIONS = {"GENERATE_QUIZ", "DISAMBIGUATE", "REFUSE_UNGROUNDED"}


def decide_quiz(graph: Dict[str, Any], concept_id: str) -> str:
    if not concept_id:
        return "REFUSE_UNGROUNDED"

    node = next((n for n in graph.get("nodes") or [] if n.get("id") == concept_id), None)
    if node is None:
        return "REFUSE_UNGROUNDED"

    sources = node.get("sources") or []
    if not sources:
        return "REFUSE_UNGROUNDED"

    if len(sources) == 1:
        return "GENERATE_QUIZ"

    return "GENERATE_QUIZ"
