from __future__ import annotations

from typing import Any

from ai.grounding.verifier import GroundingVerifier

RUBRIC_DIMENSIONS = (
    "grounding", "correctness", "single_best_answer", "distractor_quality",
    "concept_alignment", "difficulty_alignment", "explanation_quality",
    "citation_quality", "clarity", "no_leakage",
)


def _text(value: Any) -> str:
    return str(value or "").strip().lower()


def evaluate_quiz(graph: dict[str, Any], quiz: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = expected or {}
    options = [str(option).strip() for option in quiz.get("options") or []]
    answer = str(quiz.get("correct_answer") or "").strip()
    citations = quiz.get("citations") or []
    node_ids = {node.get("id") for node in graph.get("nodes") or []}
    concept_id = quiz.get("concept_id")
    citation_chunks = {citation.get("chunk_id") for citation in citations if isinstance(citation, dict)}
    source_chunks = {
        source.get("chunk_id")
        for node in graph.get("nodes") or []
        for source in node.get("sources") or []
        if isinstance(source, dict)
    }
    duplicate_options = len(options) != len({_text(option) for option in options})
    answer_count = sum(_text(option) == _text(answer) for option in options)
    answer_in_options = bool(answer) and answer_count == 1
    citations_exist = bool(citations) and citation_chunks.issubset(source_chunks)
    concept_aligned = concept_id in node_ids and concept_id == expected.get("concept_id", concept_id)
    decision = quiz.get("decision")
    is_refusal = decision in {"REFUSE_UNGROUNDED", "DISAMBIGUATE"}
    question = _text(quiz.get("question"))
    explanation = _text(quiz.get("explanation"))
    answer_leaked = bool(answer) and _text(answer) in question
    expected_answer = expected.get("expected_correct_answer")
    correctness = expected_answer is None or _text(expected_answer) == _text(answer)
    supported = decision == "GENERATE_QUIZ" and citations_exist and answer_in_options
    critical_reasons = []
    if decision == "GENERATE_QUIZ" and not supported:
        critical_reasons.append("generated quiz is missing valid grounded evidence or answer contract")
    if expected.get("expected_decision") in {"DISAMBIGUATE", "REFUSE_UNGROUNDED"} and decision == "GENERATE_QUIZ":
        critical_reasons.append("generated quiz when the labeled decision requires disambiguation or refusal")
    if decision == "GENERATE_QUIZ" and not correctness:
        critical_reasons.append("declared correct answer disagrees with expected source answer")
    if duplicate_options:
        critical_reasons.append("duplicate options")
    if answer_count > 1:
        critical_reasons.append("multiple options match the correct answer")

    scores = {
        "grounding": 2 if supported else (2 if is_refusal else 0),
        "correctness": 2 if correctness and (is_refusal or answer_in_options) else 0,
        "single_best_answer": 2 if is_refusal or (answer_count == 1 and not duplicate_options) else 0,
        "distractor_quality": 2 if is_refusal or (len(options) >= 2 and not duplicate_options and all(option) for option in options) else 0,
        "concept_alignment": 2 if is_refusal or concept_aligned else 0,
        "difficulty_alignment": 2 if is_refusal or quiz.get("difficulty") in {"easy", "medium", "hard"} else 0,
        "explanation_quality": 2 if is_refusal or len(explanation) >= 20 else 0,
        "citation_quality": 2 if is_refusal or citations_exist else 0,
        "clarity": 2 if is_refusal or len(question) >= 10 else 0,
        "no_leakage": 2 if is_refusal or not answer_leaked else 0,
    }
    score = sum(scores.values())
    if critical_reasons:
        classification = "fail"
    elif score >= 18:
        classification = "strong"
    elif score >= 15:
        classification = "acceptable"
    elif score >= 12:
        classification = "needs_improvement"
    else:
        classification = "fail"
    return {
        "score": score,
        "max_score": 20,
        "classification": classification,
        "critical_failure": bool(critical_reasons),
        "critical_reasons": critical_reasons,
        "scores": scores,
        "checks": {
            "answer_in_options": answer_in_options,
            "duplicate_options": duplicate_options,
            "citations_exist": citations_exist,
            "concept_aligned": concept_aligned,
            "answer_leaked": answer_leaked,
        },
    }
