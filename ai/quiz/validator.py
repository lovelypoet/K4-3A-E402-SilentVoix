from __future__ import annotations

import re
from typing import Any


def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2}


def validate_quiz_output(graph: dict[str, Any], quiz: dict[str, Any]) -> dict[str, Any]:
    if quiz.get("decision") != "GENERATE_QUIZ":
        return {"valid": True, "failures": []}
    failures: list[str] = []
    options = [str(option).strip() for option in quiz.get("options") or []]
    answer = str(quiz.get("correct_answer") or "").strip()
    question = str(quiz.get("question") or "").strip()
    citations = quiz.get("citations") or []
    concept_id = str(quiz.get("concept_id") or "")
    node = next((item for item in graph.get("nodes") or [] if item.get("id") == concept_id), None)
    if not question:
        failures.append("missing question")
    if not options:
        failures.append("missing options")
    if not answer or sum(option.lower() == answer.lower() for option in options) != 1:
        failures.append("correct answer must occur exactly once in options")
    if len(options) != len({option.lower() for option in options}):
        failures.append("duplicate options")
    if not citations:
        failures.append("missing citation")
    source_texts = [str(source.get("text") or "").lower() for source in (node or {}).get("sources") or []]
    concept_terms = set(concept_id.split("_"))
    if source_texts and not any(concept_terms & _tokens(question) for _ in source_texts):
        failures.append("question is not aligned to requested concept")
    answer_tokens = _tokens(answer)
    if source_texts and answer_tokens and not any(answer_tokens & _tokens(text) for text in source_texts):
        failures.append("correct answer has no lexical support in cited source text")
    valid_chunks = {source.get("chunk_id") for item in graph.get("nodes") or [] for source in item.get("sources") or []}
    if any(citation.get("chunk_id") not in valid_chunks for citation in citations if isinstance(citation, dict)):
        failures.append("citation target does not exist")
    return {"valid": not failures, "failures": failures}
