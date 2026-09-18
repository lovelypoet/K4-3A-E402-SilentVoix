from __future__ import annotations

import time
import uuid
import logging
from typing import Any

from ai.grounding.retriever import GroundingRetriever
from ai.quiz.decision import analyze_quiz_evidence, decide_quiz
from ai.quiz.providers.base import QuizProvider
from ai.quiz.providers.gemini import ProviderOutputError, ProviderRateLimitError
from ai.quiz.cache import PROMPT_VERSION, QuizCache, build_cache_key, source_content_hash
from ai.quiz.generator import QUESTION_BANK, generate_quiz as generate_deterministic_quiz
from ai.quiz.health import record
from ai.quiz.retrieval import evidence_character_count, select_evidence
from ai.quiz.schema import Quiz, QuizCitation, QuizOption, QuizValidation
from ai.quiz.validator import validate_canonical_quiz_output, validate_draft_constraints

logger = logging.getLogger(__name__)


def _failure(lesson_id: str, concept: dict[str, Any], difficulty: str, decision: str, reason: str, **metadata: Any) -> Quiz:
    if decision == "GENERATION_FAILED":
        record("generation_failed")
    elif decision == "VALIDATION_FAILED":
        record("validation_failed")
    logger.info(
        "quiz_generation lesson_id=%s concept_id=%s provider=%s model=%s evidence_chunk_count=%s "
        "evidence_character_count=%s attempt_count=%s latency_ms=%s http_status=%s result=%s",
        lesson_id, concept.get("id"), metadata.get("provider"), metadata.get("model"),
        metadata.get("evidence_chunk_count"), metadata.get("evidence_character_count"),
        metadata.get("attempt_count"), metadata.get("latency_ms"), metadata.get("http_status"), decision,
    )
    return Quiz(
        quiz_id=f"quiz_{uuid.uuid4().hex[:12]}", lesson_id=lesson_id,
        concept_id=str(concept.get("id") or ""), concept_label=str(concept.get("label") or ""),
        difficulty=difficulty, decision=decision, validation=QuizValidation(passed=False, reason=reason),
        generator_type=metadata.pop("generator_type", None), metadata=metadata,
    )


def generate_grounded_quiz(
    graph: dict[str, Any], lesson_id: str, concept_id: str, difficulty: str,
    provider: QuizProvider, allow_deterministic_fallback: bool = False,
    cache: QuizCache | None = None,
) -> Quiz:
    node = next((n for n in graph.get("nodes") or [] if n.get("id") == concept_id), None)
    if node is None:
        return _failure(lesson_id, {"id": concept_id}, difficulty, "REFUSE_UNGROUNDED", "requested concept is absent from the lesson graph")

    all_evidence = GroundingRetriever(graph).retrieve_evidence(concept_id)
    evidence = select_evidence(node, all_evidence)
    if not evidence:
        return _failure(lesson_id, node, difficulty, "REFUSE_UNGROUNDED", "no usable evidence remained after evidence selection")

    cache = cache or QuizCache()
    provider_name = getattr(provider, "provider_name", "unknown")
    model = getattr(provider, "model", "unknown")
    selected_source_hash = source_content_hash(evidence)
    cache_key = build_cache_key(lesson_id, concept_id, difficulty, selected_source_hash, provider_name, model)
    cached = cache.get(cache_key)
    if cached:
        cached_quiz = Quiz.model_validate(cached)
        cached_quiz.generator_type = "gemini_cached"
        cached_quiz.metadata.update({"cache_hit": True, "source_hash": selected_source_hash, "prompt_version": PROMPT_VERSION, "provider": provider_name, "model": model})
        record("cache_hit")
        return cached_quiz

    decision = decide_quiz(graph, concept_id)
    analysis = analyze_quiz_evidence(graph, concept_id)
    if decision != "GENERATE_QUIZ":
        return _failure(lesson_id, node, difficulty, decision, "; ".join(analysis.get("reasons") or ["evidence is insufficient"]))

    started = time.perf_counter()
    try:
        draft = provider.generate_quiz_from_evidence(node, evidence, difficulty)
    except ProviderOutputError as exc:
        return _failure(
            lesson_id, node, difficulty, "VALIDATION_FAILED", str(exc),
            provider=provider_name, model=model,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
            evidence_chunk_count=len(evidence), evidence_character_count=evidence_character_count(evidence),
            attempt_count=getattr(provider, "last_request_metrics", {}).get("attempt_count", 0),
            http_status=getattr(provider, "last_request_metrics", {}).get("http_status"),
        )
    except ProviderRateLimitError as exc:
        return _failure(
            lesson_id, node, difficulty, "GENERATION_FAILED", str(exc),
            provider=provider_name, model=model,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
            evidence_chunk_count=len(evidence), evidence_character_count=evidence_character_count(evidence),
            attempt_count=getattr(provider, "last_request_metrics", {}).get("attempt_count", 0),
            http_status=getattr(provider, "last_request_metrics", {}).get("http_status"),
        )
    except Exception as exc:
        if allow_deterministic_fallback and concept_id in QUESTION_BANK:
            fallback = generate_deterministic_quiz(graph, concept_id, difficulty)
            if fallback.get("decision") == "GENERATE_QUIZ":
                fallback_options = [QuizOption(id=chr(65 + i), text=text) for i, text in enumerate(fallback.get("options") or [])]
                fallback_citations = [QuizCitation(**{key: source.get(key) for key in ("document_id", "chunk_id", "page", "slide", "start_time", "end_time")}) for source in all_evidence]
                return Quiz(
                    quiz_id=f"quiz_{uuid.uuid4().hex[:12]}", lesson_id=lesson_id, concept_id=concept_id,
                    concept_label=str(node.get("label") or concept_id), difficulty=difficulty,
                    question=fallback.get("question", ""), options=fallback_options,
                    correct_option=chr(65 + (fallback.get("options") or []).index(fallback.get("correct_answer"))),
                    explanation=fallback.get("explanation", ""), citations=fallback_citations,
                    decision="GENERATE_QUIZ", validation=QuizValidation(passed=True),
                    generator_type="deterministic_fallback", metadata={
                        "provider": provider_name, "model": model, "fallback_reason": str(exc),
                        "evidence_chunk_count": len(evidence), "evidence_character_count": evidence_character_count(evidence),
                    },
                )
        return _failure(
            lesson_id, node, difficulty, "GENERATION_FAILED", str(exc),
            provider=provider_name, model=model,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
            evidence_chunk_count=len(evidence), evidence_character_count=evidence_character_count(evidence),
            attempt_count=getattr(provider, "last_request_metrics", {}).get("attempt_count", 0),
            http_status=getattr(provider, "last_request_metrics", {}).get("http_status"),
        )

    short_validation = validate_draft_constraints(draft.model_dump(), evidence)
    if not short_validation["valid"]:
        return _failure(
            lesson_id, node, difficulty, "VALIDATION_FAILED", "; ".join(short_validation["failures"]),
            provider=provider_name, model=model, evidence_chunk_count=len(evidence),
            evidence_character_count=evidence_character_count(evidence),
            attempt_count=getattr(provider, "last_request_metrics", {}).get("attempt_count", 0),
            http_status=getattr(provider, "last_request_metrics", {}).get("http_status"),
        )

    citations_by_id = {item.get("_evidence_id"): item for item in evidence}
    used_ids = draft.used_evidence_ids
    citations = [
        QuizCitation(
            document_id=citations_by_id[cid].get("document_id"), chunk_id=citations_by_id[cid].get("chunk_id"),
            page=citations_by_id[cid].get("page"), slide=citations_by_id[cid].get("slide"),
            start_time=citations_by_id[cid].get("start_time"), end_time=citations_by_id[cid].get("end_time"),
        )
        for cid in used_ids if cid in citations_by_id
    ]
    options = [QuizOption(id=chr(65 + i), text=value) for i, value in enumerate(draft.options)]
    correct = chr(65 + draft.correct_index) if 0 <= draft.correct_index < len(options) else ""
    quiz = Quiz(
        quiz_id=f"quiz_{uuid.uuid4().hex[:12]}", lesson_id=lesson_id,
        concept_id=concept_id, concept_label=str(node.get("label") or concept_id), difficulty=difficulty,
        question=draft.question, options=options, correct_option=correct,
        explanation=draft.explanation, citations=citations, decision="GENERATE_QUIZ",
        validation=QuizValidation(passed=False), generator_type="gemini_live",
        metadata={"provider": provider_name, "model": model, "cache_hit": False, "source_hash": selected_source_hash, "prompt_version": PROMPT_VERSION, "evidence_chunk_count": len(evidence), "evidence_character_count": evidence_character_count(evidence), "attempt_count": getattr(provider, "last_request_metrics", {}).get("attempt_count", 1), "http_status": getattr(provider, "last_request_metrics", {}).get("http_status"), "latency_ms": round((time.perf_counter() - started) * 1000, 2)},
    )
    validation = validate_canonical_quiz_output(graph, quiz.model_dump())
    if not validation["valid"]:
        quiz.decision = "VALIDATION_FAILED"
        quiz.validation = QuizValidation(passed=False, reason="; ".join(validation["failures"]))
        quiz.question = ""
        quiz.options = []
        quiz.correct_option = ""
        quiz.explanation = ""
        quiz.citations = []
    else:
        quiz.validation = QuizValidation(passed=True)
        cache.put(cache_key, quiz.model_dump(), source_hash=selected_source_hash, provider=provider_name, model=model)
        record("live_generation_success")
    logger.info(
        "quiz_generation lesson_id=%s concept_id=%s provider=%s model=%s evidence_chunk_count=%s "
        "evidence_character_count=%s attempt_count=%s latency_ms=%s http_status=%s result=%s",
        lesson_id, concept_id, quiz.metadata.get("provider"), quiz.metadata.get("model"),
        quiz.metadata.get("evidence_chunk_count"), quiz.metadata.get("evidence_character_count"),
        quiz.metadata.get("attempt_count"), quiz.metadata.get("latency_ms"), quiz.metadata.get("http_status"), quiz.decision,
    )
    return quiz
