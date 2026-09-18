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


def validate_canonical_quiz_output(graph: dict[str, Any], quiz: dict[str, Any]) -> dict[str, Any]:
    """Validate the provider draft after it has been converted to canonical schema."""
    failures: list[str] = []
    options = quiz.get("options") or []
    texts = [str(item.get("text") or "").strip() for item in options if isinstance(item, dict)]
    answer = str(quiz.get("correct_option") or "").strip().upper()
    citations = quiz.get("citations") or []
    if not quiz.get("question", "").strip(): failures.append("missing question")
    if len(options) != 4 or len(texts) != 4: failures.append("exactly four options required")
    if len(set(text.lower() for text in texts)) != len(texts): failures.append("duplicate options")
    if answer not in {item.get("id") for item in options if isinstance(item, dict)}: failures.append("correct option must identify one option")
    if not quiz.get("explanation", "").strip(): failures.append("missing explanation")
    if not citations: failures.append("missing citation")
    node = next((item for item in graph.get("nodes") or [] if item.get("id") == quiz.get("concept_id")), None)
    if node is None: failures.append("concept is not in lesson graph")
    valid_sources = {source.get("chunk_id"): source for source in (node or {}).get("sources") or []}
    if any(item.get("chunk_id") not in valid_sources for item in citations if isinstance(item, dict)):
        failures.append("citation target does not exist for requested concept")
    source_text = " ".join(str(source.get("text") or "") for source in valid_sources.values())
    support_tokens = _tokens(source_text)
    question_tokens = _tokens(str(quiz.get("question") or ""))
    explanation_tokens = _tokens(str(quiz.get("explanation") or ""))
    if support_tokens and not (question_tokens & support_tokens): failures.append("question has no lexical support in cited evidence")
    if support_tokens and not (explanation_tokens & support_tokens): failures.append("explanation has no lexical support in cited evidence")
    if len(answer) == 1 and options and 0 <= ord(answer) - 65 < len(texts):
        answer_tokens = _tokens(texts[ord(answer) - 65])
        if support_tokens and not (answer_tokens & support_tokens): failures.append("correct answer has no lexical support in cited evidence")
    return {"valid": not failures, "failures": failures}


def validate_draft_constraints(draft: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    failures: list[str] = []
    question = str(draft.get("question") or "").strip()
    options = [str(value).strip() for value in draft.get("options") or []]
    explanation = str(draft.get("explanation") or "").strip()
    used_ids = draft.get("used_evidence_ids") or []
    if len(question.split()) > 25: failures.append("question exceeds 25 words")
    if len(options) != 4: failures.append("exactly four options required")
    if any(len(option.split()) > 12 for option in options): failures.append("option exceeds 12 words")
    if len(set(option.lower() for option in options)) != len(options): failures.append("duplicate options")
    if not 0 <= int(draft.get("correct_index", -1)) < 4: failures.append("correct_index must select exactly one option")
    if len(explanation.split()) > 40: failures.append("explanation exceeds 40 words")
    valid_ids = {item.get("_evidence_id") for item in evidence}
    if not used_ids or any(item not in valid_ids for item in used_ids): failures.append("used evidence ID does not exist")
    return {"valid": not failures, "failures": failures}
